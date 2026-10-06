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

function githubHeaders(token: string) {
  return {
    accept: 'application/vnd.github+json',
    authorization: `Bearer ${token}`,
    'x-github-api-version': '2022-11-28',
    'user-agent': 'CareerHub-action-gateway',
  };
}

export async function GET(request: Request) {
  const cfg = githubConfig();
  const actionId = new URL(request.url).searchParams.get('action_id')?.trim() || '';

  if (!actionId) {
    return NextResponse.json({
      operations: Array.from(OPERATIONS),
      dispatchConfigured: Boolean(cfg.repository && cfg.token),
      repository: cfg.repository || null,
    });
  }

  if (!cfg.repository || !cfg.token) {
    return NextResponse.json({ action_id: actionId, status: 'unconfigured', conclusion: null });
  }

  const runsUrl = new URL(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}/runs`);
  runsUrl.searchParams.set('event', 'workflow_dispatch');
  runsUrl.searchParams.set('branch', cfg.ref);
  runsUrl.searchParams.set('per_page', '30');
  const response = await fetch(runsUrl, { headers: githubHeaders(cfg.token), cache: 'no-store' });
  if (!response.ok) {
    return NextResponse.json({ error: 'CareerHub could not read motor status.', action_id: actionId }, { status: 502 });
  }
  const data = await response.json().catch(() => ({}));
  const runs = Array.isArray(data?.workflow_runs) ? data.workflow_runs : [];
  const run = runs.find((item: any) => String(item?.display_title ?? '').includes(actionId));
  if (!run) return NextResponse.json({ action_id: actionId, status: 'not_found', conclusion: null });

  return NextResponse.json({
    action_id: actionId,
    status: run.status ?? 'unknown',
    conclusion: run.conclusion ?? null,
    run_url: run.html_url ?? null,
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
      user_state: stored ? 'waiting_for_motor_connection' : 'not_started',
      dispatched: false,
      stored,
      message: stored
        ? 'Request saved, but not started yet. This CareerHub is waiting for its secure motor connection, so no analysis or update is running. The request reference is kept for tracing.'
        : 'Request not started. This CareerHub deployment is not connected to the motor and could not store the request.',
      next_step: 'Connect the CareerHub GitHub dispatcher for this deployment, then submit the action again.',
    }, { status: stored ? 202 : 503 });
  }

  const response = await fetch(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}/dispatches`, {
    method: 'POST',
    headers: {
      ...githubHeaders(cfg.token),
      'content-type': 'application/json',
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
      error: 'CareerHub could not start the motor operation.',
      action_id: actionId,
      stored,
      user_state: 'dispatch_failed',
      message: 'The request was received, but the secure motor hand-off failed. Nothing is running yet.',
      next_step: 'Try again. If it repeats, use the ACT reference when checking the dispatcher configuration.',
      detail: detail.slice(0, 500),
    }, { status: 502 });
  }

  return NextResponse.json({
    action_id: actionId,
    state: 'DISPATCHED',
    user_state: 'running_in_background',
    dispatched: true,
    stored,
    message: 'Started. CareerHub handed the request to the motor, which is now working in the background.',
    next_step: 'You can keep using CareerHub. The relevant profile, analysis, application or tracking view updates after the motor finishes and the site refreshes.',
  }, { status: 202 });
}
