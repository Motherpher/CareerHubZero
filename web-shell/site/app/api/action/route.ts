import { put } from '@vercel/blob';
import { randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';
import { loadCareerHubManifest } from '@/lib/manifest';

const OPERATIONS = new Set([
  'analyse_role',
  'track_status',
  'track_priority',
  'track_event',
  'profile_review',
  'profile_rebuild',
  'library_review',
  'search_profile_update',
]);

function githubConfig() {
  return {
    repository: process.env.CAREERHUB_GITHUB_REPOSITORY || '',
    token: process.env.CAREERHUB_GITHUB_TOKEN || '',
    workflow: process.env.CAREERHUB_GITHUB_WORKFLOW || 'careerhub-operations.yml',
    ref: process.env.CAREERHUB_GITHUB_REF || 'main',
  };
}

export async function GET() {
  const cfg = githubConfig();
  return NextResponse.json({
    operations: Array.from(OPERATIONS),
    dispatchConfigured: Boolean(cfg.repository && cfg.token),
    repository: cfg.repository || null,
  });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const operation = typeof body?.operation === 'string' ? body.operation : '';
  const payload = body?.payload && typeof body.payload === 'object' ? body.payload : {};
  if (!OPERATIONS.has(operation)) return NextResponse.json({ error: 'Unsupported CareerHub action.' }, { status: 400 });

  const manifest = loadCareerHubManifest();
  const actionId = `ACT-${new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)}-${randomUUID().slice(0, 8)}`;
  const record = {
    schema_version: '1.0',
    action_id: actionId,
    profile_id: manifest.profile_id,
    operation,
    payload,
    requested_at: new Date().toISOString(),
    state: 'REQUESTED',
  };

  let stored = false;
  try {
    await put(`actions/${manifest.profile_id}/${actionId}.json`, JSON.stringify(record, null, 2), {
      access: 'private',
      addRandomSuffix: false,
      contentType: 'application/json',
    });
    stored = true;
  } catch {
    // Action execution may still continue through GitHub dispatch when Blob is unavailable.
  }

  const cfg = githubConfig();
  if (!cfg.repository || !cfg.token) {
    return NextResponse.json({
      action_id: actionId,
      state: stored ? 'QUEUED' : 'UNCONFIGURED',
      dispatched: false,
      stored,
      message: stored
        ? 'Action queued. Connect the CareerHub GitHub dispatcher to execute motor operations.'
        : 'CareerHub action execution is not configured for this deployment.',
    }, { status: stored ? 202 : 503 });
  }

  const response = await fetch(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}/dispatches`, {
    method: 'POST',
    headers: {
      accept: 'application/vnd.github+json',
      authorization: `Bearer ${cfg.token}`,
      'content-type': 'application/json',
      'x-github-api-version': '2022-11-28',
      'user-agent': 'CareerHub-action-gateway',
    },
    body: JSON.stringify({
      ref: cfg.ref,
      inputs: {
        operation,
        action_id: actionId,
        payload: JSON.stringify(payload),
      },
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    return NextResponse.json({
      error: 'CareerHub motor dispatch failed.',
      action_id: actionId,
      stored,
      detail: detail.slice(0, 500),
    }, { status: 502 });
  }

  return NextResponse.json({
    action_id: actionId,
    state: 'DISPATCHED',
    dispatched: true,
    stored,
    message: 'Action sent to the CareerHub motor.',
  }, { status: 202 });
}
