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

async function executionPreflight() {
  const cfg = githubConfig();
  if (!cfg.repository || !cfg.token) {
    return {
      ready: false,
      dispatcherConfigured: false,
      workflowReachable: false,
      state: 'WAITING_FOR_EXECUTION',
      message: 'CareerHub cannot execute Motor actions from this deployment yet.',
      detail: 'The profile deployment is missing its GitHub dispatcher connection.',
      cfg,
    };
  }

  const workflow = await fetch(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}`, {
    headers: {
      accept: 'application/vnd.github+json',
      authorization: `Bearer ${cfg.token}`,
      'x-github-api-version': '2022-11-28',
      'user-agent': 'CareerHub-action-preflight',
    },
    cache: 'no-store',
  });

  if (!workflow.ok) {
    return {
      ready: false,
      dispatcherConfigured: true,
      workflowReachable: false,
      state: 'WAITING_FOR_EXECUTION',
      message: 'CareerHub is connected, but the Motor workflow cannot be reached.',
      detail: `GitHub workflow probe returned ${workflow.status}.`,
      cfg,
    };
  }

  return {
    ready: true,
    dispatcherConfigured: true,
    workflowReachable: true,
    state: 'READY',
    message: 'CareerHub Motor execution is available.',
    detail: 'Semantic HRDM dependency is verified again inside the GitHub workflow before analysis begins.',
    cfg,
  };
}

export async function GET() {
  const probe = await executionPreflight();
  return NextResponse.json({
    operations: Array.from(OPERATIONS),
    ready: probe.ready,
    dispatcherConfigured: probe.dispatcherConfigured,
    workflowReachable: probe.workflowReachable,
    state: probe.state,
    message: probe.message,
    detail: probe.detail,
    repository: probe.cfg.repository || null,
  }, { status: probe.ready ? 200 : 503 });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const operation = typeof body?.operation === 'string' ? body.operation : '';
  const payload = body?.payload && typeof body.payload === 'object' ? body.payload : {};
  if (!OPERATIONS.has(operation)) return NextResponse.json({ error: 'Unsupported CareerHub action.' }, { status: 400 });

  const preflight = await executionPreflight();
  if (!preflight.ready) {
    return NextResponse.json({
      state: preflight.state,
      dispatched: false,
      message: preflight.message,
      detail: preflight.detail,
    }, { status: 503 });
  }

  const manifest = loadCareerHubManifest();
  const actionId = `ACT-${new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)}-${randomUUID().slice(0, 8)}`;
  const record = {
    schema_version: '1.1',
    action_id: actionId,
    profile_id: manifest.profile_id,
    operation,
    payload,
    requested_at: new Date().toISOString(),
    state: 'PREPARING',
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
    stored = false;
  }

  const cfg = preflight.cfg;
  const response = await fetch(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}/dispatches`, {
    method: 'POST',
    headers: {
      accept: 'application/vnd.github+json',
      authorization: `Bearer ${cfg.token}`,
      'content-type': 'application/json',
      'x-github-api-version': '2022-11-28',
      'user-agent': 'CareerHub-action-gateway',
    },
    body: JSON.stringify({ ref: cfg.ref, inputs: { operation, action_id: actionId, payload: JSON.stringify(payload) } }),
  });

  if (!response.ok) {
    const detail = await response.text();
    return NextResponse.json({
      error: 'CareerHub could not start this Motor action.',
      action_id: actionId,
      state: 'FAILED',
      dispatched: false,
      stored,
      detail: detail.slice(0, 500),
    }, { status: 502 });
  }

  return NextResponse.json({
    action_id: actionId,
    state: 'WAITING_FOR_EXECUTION',
    dispatched: true,
    stored,
    message: 'The action was accepted and is waiting for the Motor to begin execution.',
    technical_reference: actionId,
    status_url: `/api/action/status?action_id=${encodeURIComponent(actionId)}`,
    result_url: operation === 'analyse_role' ? `/analyse/${encodeURIComponent(actionId)}` : null,
  }, { status: 202 });
}
