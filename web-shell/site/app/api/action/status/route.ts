import { Buffer } from 'node:buffer';
import { get, issueSignedToken, presignUrl, put } from '@vercel/blob';
import { getToken } from '@vercel/connect';
import { NextResponse } from 'next/server';
import { loadCareerHubManifest } from '@/lib/manifest';

const DEFAULT_GITHUB_CONNECTOR = 'github/amber-bell';
const SEMANTIC_REPOSITORY = process.env.CAREERHUB_SEMANTIC_REPOSITORY || 'Motherpher/CareerHubZero';
const SEMANTIC_WORKFLOW = process.env.CAREERHUB_SEMANTIC_WORKFLOW || 'careerhub-semantic.yml';

type ActionState = 'WAITING_FOR_EXECUTION' | 'RUNNING' | 'COMPLETED' | 'FAILED';

async function githubConfig() {
  const explicit = (process.env.CAREERHUB_GITHUB_TOKEN || '').trim();
  let token = explicit;
  let authSource = explicit ? 'environment' : 'none';

  if (!token) {
    const connector = (process.env.CAREERHUB_GITHUB_CONNECTOR || DEFAULT_GITHUB_CONNECTOR).trim();
    if (connector) {
      try {
        token = await getToken(connector, { subject: { type: 'app' } });
        authSource = token ? 'vercel-connect' : 'none';
      } catch (error) {
        console.error('CareerHub action-status GitHub token exchange failed.', error);
      }
    }
  }

  return {
    repository: process.env.CAREERHUB_GITHUB_REPOSITORY || '',
    token,
    workflow: process.env.CAREERHUB_GITHUB_WORKFLOW || 'careerhub-operations.yml',
    ref: process.env.CAREERHUB_GITHUB_REF || 'main',
    authSource,
  };
}

function githubHeaders(token: string) {
  return {
    accept: 'application/vnd.github+json',
    authorization: `Bearer ${token}`,
    'x-github-api-version': '2022-11-28',
    'user-agent': 'CareerHub-action-status',
  };
}

async function readJsonFile(repository: string, token: string, path: string, ref: string) {
  const encodedPath = path.split('/').map(encodeURIComponent).join('/');
  const response = await fetch(`https://api.github.com/repos/${repository}/contents/${encodedPath}?ref=${encodeURIComponent(ref)}`, {
    headers: githubHeaders(token),
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

async function pathExists(repository: string, token: string, path: string, ref: string) {
  const encodedPath = path.split('/').map(encodeURIComponent).join('/');
  const response = await fetch(`https://api.github.com/repos/${repository}/contents/${encodedPath}?ref=${encodeURIComponent(ref)}`, {
    headers: githubHeaders(token),
    cache: 'no-store',
  });
  return response.ok;
}

async function resolveRemoteProfileRoot(repository: string, token: string, ref: string) {
  if (await pathExists(repository, token, 'careerhub.yaml', ref)) return '';
  if (await pathExists(repository, token, 'CareerHub/careerhub.yaml', ref)) return 'CareerHub';
  return null;
}

function rooted(root: string, path: string) {
  return root ? `${root}/${path}` : path;
}

async function workflowRuns(repository: string, workflow: string, token: string) {
  const response = await fetch(`https://api.github.com/repos/${repository}/actions/workflows/${encodeURIComponent(workflow)}/runs?event=workflow_dispatch&per_page=50`, {
    headers: githubHeaders(token),
    cache: 'no-store',
  });
  if (!response.ok) return { ok: false as const, status: response.status, runs: [] as any[] };
  const payload = await response.json();
  return { ok: true as const, status: response.status, runs: Array.isArray(payload?.workflow_runs) ? payload.workflow_runs : [] };
}

function findActionRun(runs: any[], actionId: string, operation?: string) {
  return runs.find((item) => {
    const title = `${String(item?.name ?? '')} ${String(item?.display_title ?? '')}`;
    return title.includes(actionId) && (!operation || title.includes(operation));
  });
}

async function readPrivateJson(pathname: string) {
  try {
    const result = await get(pathname, { access: 'private' });
    if (!result || result.statusCode !== 200) return null;
    return await new Response(result.stream).json();
  } catch {
    return null;
  }
}

async function writeActionRecord(pathname: string, record: Record<string, any>) {
  try {
    await put(pathname, JSON.stringify(record, null, 2), {
      access: 'private',
      addRandomSuffix: false,
      allowOverwrite: true,
      contentType: 'application/json',
    });
  } catch (error) {
    console.error('CareerHub could not update action record.', error);
  }
}

async function dispatchMaterialization(
  cfg: Awaited<ReturnType<typeof githubConfig>>,
  actionId: string,
  resultPath: string,
) {
  const validUntil = Date.now() + 15 * 60 * 1000;
  const signed = await issueSignedToken({ pathname: resultPath, operations: ['get'], validUntil });
  const { presignedUrl } = await presignUrl(signed, {
    operation: 'get',
    pathname: resultPath,
    access: 'private',
    useCache: false,
    validUntil,
  });

  return fetch(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}/dispatches`, {
    method: 'POST',
    headers: { ...githubHeaders(cfg.token), 'content-type': 'application/json' },
    body: JSON.stringify({
      ref: cfg.ref,
      inputs: {
        operation: 'materialize_analysis',
        action_id: actionId,
        payload: JSON.stringify({ bundle_url: presignedUrl }),
      },
    }),
  });
}

function stateResponse(
  actionId: string,
  authSource: string,
  state: ActionState,
  message: string,
  extra: Record<string, any> = {},
  status = 200,
) {
  return NextResponse.json({ action_id: actionId, state, authSource, message, ...extra }, { status });
}

export async function GET(request: Request) {
  const actionId = new URL(request.url).searchParams.get('action_id')?.trim() || '';
  if (!/^ACT-[A-Za-z0-9-]+$/.test(actionId)) {
    return NextResponse.json({ error: 'A valid action_id is required.' }, { status: 400 });
  }

  const cfg = await githubConfig();
  if (!cfg.repository || !cfg.token) {
    return stateResponse(
      actionId,
      cfg.authSource,
      'WAITING_FOR_EXECUTION',
      'CareerHub is waiting for its Motor connection before this action can execute.',
      {},
      503,
    );
  }

  const manifest = loadCareerHubManifest();
  const actionRecordPath = `actions/${manifest.profile_id}/${actionId}.json`;
  const record = await readPrivateJson(actionRecordPath);
  const isSemantic = record?.operation === 'analyse_role';

  if (isSemantic) {
    const semanticRepository = String(record.executor_repository || SEMANTIC_REPOSITORY);
    const semanticWorkflow = String(record.executor_workflow || SEMANTIC_WORKFLOW);
    const semanticRuns = await workflowRuns(semanticRepository, semanticWorkflow, cfg.token);
    if (!semanticRuns.ok) {
      return stateResponse(actionId, cfg.authSource, 'FAILED', 'CareerHub could not read the central semantic Motor state.', { detail: `GitHub returned ${semanticRuns.status}.` }, 502);
    }

    const semanticRun = findActionRun(semanticRuns.runs, actionId);
    if (!semanticRun) {
      return stateResponse(actionId, cfg.authSource, 'WAITING_FOR_EXECUTION', 'The action was accepted and is waiting for the central semantic Motor runner.');
    }
    if (['queued', 'waiting', 'requested', 'pending'].includes(semanticRun.status)) {
      return stateResponse(actionId, cfg.authSource, 'WAITING_FOR_EXECUTION', 'The central semantic Motor has the action and is waiting to start it.', { run_url: semanticRun.html_url });
    }
    if (semanticRun.status !== 'completed') {
      return stateResponse(actionId, cfg.authSource, 'RUNNING', 'CareerHub central semantic Motor is running HRDM-R.', { run_url: semanticRun.html_url });
    }
    if (semanticRun.conclusion !== 'success') {
      await writeActionRecord(actionRecordPath, { ...(record || {}), state: 'FAILED', failed_at: new Date().toISOString(), semantic_run_url: semanticRun.html_url });
      return stateResponse(actionId, cfg.authSource, 'FAILED', 'The central semantic Motor started but HRDM-R did not complete successfully.', { conclusion: semanticRun.conclusion, run_url: semanticRun.html_url });
    }

    const resultPath = String(record?.semantic_result_path || '');
    if (!resultPath) {
      return stateResponse(actionId, cfg.authSource, 'FAILED', 'Semantic execution completed but no governed result path was recorded.', { run_url: semanticRun.html_url });
    }

    const bundle = await readPrivateJson(resultPath);
    if (!bundle) {
      return stateResponse(actionId, cfg.authSource, 'RUNNING', 'Semantic execution finished; CareerHub is waiting for the governed result bundle.', { run_url: semanticRun.html_url });
    }
    if (String(bundle.action_id || '') !== actionId) {
      return stateResponse(actionId, cfg.authSource, 'FAILED', 'Semantic result identity did not match the requested CareerHub action.', { run_url: semanticRun.html_url });
    }

    const profileRuns = await workflowRuns(cfg.repository, cfg.workflow, cfg.token);
    if (!profileRuns.ok) {
      return stateResponse(actionId, cfg.authSource, 'FAILED', 'CareerHub could not read profile materialization state.', { detail: `GitHub returned ${profileRuns.status}.` }, 502);
    }

    const materializeRun = findActionRun(profileRuns.runs, actionId, 'materialize_analysis');
    if (!materializeRun) {
      if (!record?.materialization_dispatched_at) {
        const dispatched = await dispatchMaterialization(cfg, actionId, resultPath);
        if (!dispatched.ok) {
          const detail = await dispatched.text();
          return stateResponse(actionId, cfg.authSource, 'FAILED', 'Semantic HRDM completed, but CareerHub could not start profile materialization.', { detail: detail.slice(0, 500) }, 502);
        }
        await writeActionRecord(actionRecordPath, {
          ...(record || {}),
          state: 'RUNNING',
          semantic_run_url: semanticRun.html_url,
          materialization_dispatched_at: new Date().toISOString(),
        });
      }
      return stateResponse(actionId, cfg.authSource, 'RUNNING', 'HRDM-R completed centrally. CareerHub is materializing the governed result into the profile repository.', { run_url: semanticRun.html_url });
    }

    if (['queued', 'waiting', 'requested', 'pending'].includes(materializeRun.status)) {
      return stateResponse(actionId, cfg.authSource, 'WAITING_FOR_EXECUTION', 'HRDM-R completed centrally. Profile materialization is queued.', { run_url: materializeRun.html_url });
    }
    if (materializeRun.status !== 'completed') {
      return stateResponse(actionId, cfg.authSource, 'RUNNING', 'HRDM-R completed centrally. Profile artifacts and state are being materialized.', { run_url: materializeRun.html_url });
    }
    if (materializeRun.conclusion !== 'success') {
      await writeActionRecord(actionRecordPath, {
        ...(record || {}),
        state: 'FAILED',
        failed_at: new Date().toISOString(),
        semantic_run_url: semanticRun.html_url,
        materialization_run_url: materializeRun.html_url,
      });
      return stateResponse(actionId, cfg.authSource, 'FAILED', 'HRDM-R completed, but the profile repository could not materialize the result.', { conclusion: materializeRun.conclusion, run_url: materializeRun.html_url });
    }

    const profileRoot = await resolveRemoteProfileRoot(cfg.repository, cfg.token, cfg.ref);
    if (profileRoot === null) {
      await writeActionRecord(actionRecordPath, { ...(record || {}), state: 'FAILED', failed_at: new Date().toISOString() });
      return stateResponse(actionId, cfg.authSource, 'FAILED', 'Profile materialization finished, but CareerHub could not resolve the profile repository root.', { run_url: materializeRun.html_url });
    }

    const hrdmPath = rooted(profileRoot, `output/${actionId}/HRDM_result.json`);
    const applicationPath = rooted(profileRoot, `output/${actionId}/application_package.json`);
    const hrdm = await readJsonFile(cfg.repository, cfg.token, hrdmPath, cfg.ref);
    const application = await readJsonFile(cfg.repository, cfg.token, applicationPath, cfg.ref);

    if (!hrdm) {
      await writeActionRecord(actionRecordPath, {
        ...(record || {}),
        state: 'FAILED',
        failed_at: new Date().toISOString(),
        semantic_run_url: semanticRun.html_url,
        materialization_run_url: materializeRun.html_url,
        persistence_error: `Missing ${hrdmPath}`,
      });
      return stateResponse(
        actionId,
        cfg.authSource,
        'FAILED',
        'Profile materialization workflow succeeded, but the canonical HRDM result was not persisted to the profile repository.',
        { run_url: materializeRun.html_url, expected_path: hrdmPath },
      );
    }

    await writeActionRecord(actionRecordPath, {
      ...(record || {}),
      state: 'COMPLETED',
      completed_at: new Date().toISOString(),
      semantic_run_url: semanticRun.html_url,
      materialization_run_url: materializeRun.html_url,
      persisted_hrdm_path: hrdmPath,
    });

    return NextResponse.json({
      action_id: actionId,
      state: 'COMPLETED',
      authSource: cfg.authSource,
      message: 'HRDM-R completed and the canonical result was verified in the profile repository.',
      process_id: hrdm.process_id ?? hrdm.trace?.process_id ?? null,
      hrdm,
      application,
      semantic_run_url: semanticRun.html_url,
      run_url: materializeRun.html_url,
      persisted_hrdm_path: hrdmPath,
      result_url: `/analyse/${encodeURIComponent(actionId)}`,
    });
  }

  const response = await workflowRuns(cfg.repository, cfg.workflow, cfg.token);
  if (!response.ok) {
    return stateResponse(actionId, cfg.authSource, 'FAILED', 'CareerHub could not read the Motor execution state.', { detail: `GitHub returned ${response.status}.` }, 502);
  }

  const run = findActionRun(response.runs, actionId);
  if (!run) return stateResponse(actionId, cfg.authSource, 'WAITING_FOR_EXECUTION', 'The action was accepted and is waiting for the Motor runner.');
  if (['queued', 'waiting', 'requested', 'pending'].includes(run.status)) {
    return stateResponse(actionId, cfg.authSource, 'WAITING_FOR_EXECUTION', 'The Motor has the action and is waiting to start it.', { run_url: run.html_url });
  }
  if (run.status !== 'completed') {
    return stateResponse(actionId, cfg.authSource, 'RUNNING', 'CareerHub Motor is running the operation.', { run_url: run.html_url });
  }
  if (run.conclusion !== 'success') {
    return stateResponse(actionId, cfg.authSource, 'FAILED', 'The Motor started but the operation did not complete successfully.', { conclusion: run.conclusion, run_url: run.html_url });
  }

  return stateResponse(actionId, cfg.authSource, 'COMPLETED', 'CareerHub Motor operation completed.', { run_url: run.html_url });
}
