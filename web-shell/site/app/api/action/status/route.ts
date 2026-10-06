import { Buffer } from 'node:buffer';
import { NextResponse } from 'next/server';

function githubConfig() {
  return {
    repository: process.env.CAREERHUB_GITHUB_REPOSITORY || '',
    token: process.env.CAREERHUB_GITHUB_TOKEN || '',
    workflow: process.env.CAREERHUB_GITHUB_WORKFLOW || 'careerhub-operations.yml',
    ref: process.env.CAREERHUB_GITHUB_REF || 'main',
  };
}

function headers(token: string) {
  return {
    accept: 'application/vnd.github+json',
    authorization: `Bearer ${token}`,
    'x-github-api-version': '2022-11-28',
    'user-agent': 'CareerHub-action-status',
  };
}

async function readJsonFile(repository: string, token: string, path: string, ref: string) {
  const response = await fetch(`https://api.github.com/repos/${repository}/contents/${path.split('/').map(encodeURIComponent).join('/')}?ref=${encodeURIComponent(ref)}`, {
    headers: headers(token),
    cache: 'no-store',
  });
  if (!response.ok) return null;
  const payload = await response.json();
  if (!payload?.content) return null;
  try {
    return JSON.parse(Buffer.from(String(payload.content).replace(/\n/g, ''), 'base64').toString('utf8'));
  } catch {
    return null;
  }
}

export async function GET(request: Request) {
  const actionId = new URL(request.url).searchParams.get('action_id')?.trim() || '';
  if (!/^ACT-[A-Za-z0-9-]+$/.test(actionId)) {
    return NextResponse.json({ error: 'A valid action_id is required.' }, { status: 400 });
  }

  const cfg = githubConfig();
  if (!cfg.repository || !cfg.token) {
    return NextResponse.json({
      action_id: actionId,
      state: 'WAITING_FOR_EXECUTION',
      message: 'CareerHub is waiting for its Motor connection before this action can execute.',
    }, { status: 503 });
  }

  const response = await fetch(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}/runs?event=workflow_dispatch&per_page=50`, {
    headers: headers(cfg.token),
    cache: 'no-store',
  });
  if (!response.ok) {
    return NextResponse.json({
      action_id: actionId,
      state: 'FAILED',
      message: 'CareerHub could not read the Motor execution state.',
      detail: `GitHub returned ${response.status}.`,
    }, { status: 502 });
  }

  const payload = await response.json();
  const runs: any[] = Array.isArray(payload?.workflow_runs) ? payload.workflow_runs : [];
  const run = runs.find((item) => String(item?.name ?? '').includes(actionId) || String(item?.display_title ?? '').includes(actionId));

  if (!run) {
    return NextResponse.json({
      action_id: actionId,
      state: 'WAITING_FOR_EXECUTION',
      message: 'The action was accepted and is waiting for the Motor runner.',
    });
  }

  if (run.status === 'queued' || run.status === 'waiting' || run.status === 'requested' || run.status === 'pending') {
    return NextResponse.json({
      action_id: actionId,
      state: 'WAITING_FOR_EXECUTION',
      message: 'The Motor has the action and is waiting to start it.',
      run_url: run.html_url,
    });
  }

  if (run.status !== 'completed') {
    return NextResponse.json({
      action_id: actionId,
      state: 'RUNNING',
      message: 'CareerHub Motor is running the analysis.',
      run_url: run.html_url,
    });
  }

  if (run.conclusion !== 'success') {
    return NextResponse.json({
      action_id: actionId,
      state: 'FAILED',
      message: 'The Motor started but the operation did not complete successfully.',
      conclusion: run.conclusion,
      run_url: run.html_url,
    });
  }

  const hrdm = await readJsonFile(cfg.repository, cfg.token, `output/${actionId}/HRDM_result.json`, cfg.ref);
  const application = await readJsonFile(cfg.repository, cfg.token, `output/${actionId}/application_package.json`, cfg.ref);
  if (!hrdm) {
    return NextResponse.json({
      action_id: actionId,
      state: 'RUNNING',
      message: 'Execution finished; CareerHub is waiting for the generated report to become available.',
      run_url: run.html_url,
    });
  }

  return NextResponse.json({
    action_id: actionId,
    state: 'COMPLETED',
    message: 'HRDM-R completed. The report is ready.',
    process_id: hrdm.process_id ?? hrdm.trace?.process_id ?? null,
    hrdm,
    application,
    run_url: run.html_url,
    result_url: `/analyse/${encodeURIComponent(actionId)}`,
  });
}
