import { Buffer } from 'node:buffer';
import { get, issueSignedToken, presignUrl, put } from '@vercel/blob';
import { getToken } from '@vercel/connect';
import { NextResponse } from 'next/server';
import { loadCareerHubManifest } from '@/lib/manifest';

const DEFAULT_GITHUB_CONNECTOR = 'github/amber-bell';
const SEMANTIC_REPOSITORY = process.env.CAREERHUB_SEMANTIC_REPOSITORY || 'Motherpher/CareerHubZero';
const SEMANTIC_WORKFLOW = process.env.CAREERHUB_SEMANTIC_WORKFLOW || 'careerhub-semantic.yml';

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

async function pathExists(repository: string, token: string, path: string, ref: string) {
  const response = await fetch(`https://api.github.com/repos/${repository}/contents/${path.split('/').map(encodeURIComponent).join('/')}?ref=${encodeURIComponent(ref)}`, {
    headers: headers(token),
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
    headers: headers(token),
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

async function dispatchMaterialization(cfg: Awaited<ReturnType<typeof githubConfig>>, actionId: string, resultPath: string) {
  const validUntil = Date.now() + 15 * 60 * 1000;
  const signed = await issueSignedToken({
    pathname: resultPath,
    operations: ['get'],
    validUntil,
  });
  const { presignedUrl } = await presignUrl(signed, {
    operation: 'get',
    pathname: resultPath,
    access: 'private',
    useCache: false,
    validUntil,
  });

  return fetch(`https://api.github.com/repos/${cfg.repository}/actions/workflows/${encodeURIComponent(cfg.workflow)}/dispatches`, {
    method: 'POST',
    headers: {
      ...headers(cfg.token),
      'content-type': 'application/json',
    },
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

function waiting(actionId: string, authSource: string, message: string, runUrl?: string) {
  return NextResponse.json({
    action_id: actionId,
    state: 'WAITING_FOR_EXECUTION',
    authSource,
    message,
    ...(runUrl ? { run_url: runUrl } : {}),
  });
}

function running(actionId: string, authSource: string, message: string, runUrl?: string) {
  return NextResponse.json({
    action_id: actionId,
    state: 'RUNNING',
    authSource,
    message,
    ...(runUrl ? { run_url: runUrl } : {}),
  });
}

export async function GET(request: Request) {
  const actionId = new URL(request.url).searchParams.get('action_id')?.trim() || '';
  if (!/^ACT-[A-Za-z0-9-]+$/.test(actionId)) {
    return NextResponse.json({ error: 'A valid action_id is required.' }, { status: 400 });
  }

  const cfg = await githubConfig();
  if (!cfg.repository || !cfg.token) {
    return NextResponse.json({
      action_id: actionId,
      state: 'WAITING_FOR_EXECUTION',
      authSource: cfg.authSource,
      message: 'CareerHub is waiting for its Motor connection before this action can execute.',
    }, { status: 503 });
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
      return NextResponse.json({
        action_id: actionId,
        state: 'FAILED',
        authSource: cfg.authSource,
        message: 'CareerHub could not read the central semantic Motor state.',
        detail: `GitHub returned ${semanticRuns.status}.`,
      }, { status: 502 });
    }

    const semanticRun = findActionRun(semanticRuns.runs, actionId);
    if (!semanticRun) return waiting(actionId, cfg.authSource, 'The action was accepted and is waiting for the central semantic Motor runner.');
    if (semanticRun.status === 'queued' || semanticRun.status === 'waiting' || semanticRun.status === 'requested' || semanticRun.status === 'pending') {
      return waiting(actionId, cfg.authSource, 'The central semantic Motor has the action and is waiting to start it.', semanticRun.html_url);
    }
    if (semanticRun.status !== 'completed') {
      return running(actionId, cfg.authSource, 'CareerHub central semantic Motor is running HRDM-R.', semanticRun.html_url);
    }
    if (semanticRun.conclusion !== 'success') {
      const failedRecord = { ...(record || {}), state: 'FAILED', failed_at: new Date().toISOString(), semantic_run_url: semanticRun.html_url };
      await writeActionRecord(actionRecordPath, failedRecord);
      return NextResponse.json({
        action_id: actionId,
        state: 'FAILED',
        authSource: cfg.authSource,
        message: 'The central semantic Motor started but HRDM-R did not complete successfully.',
        conclusion: semanticRun.conclusion,
        run_url: semanticRun.html_url,
      });
    }

    const resultPath = String(record?.semantic_result_path || '');
    if (!resultPath) {
      return NextResponse.json({
        action_id: actionId,
        state: 'FAILED',
        authSource: cfg.authSource,
        message: 'Semantic execution completed but no governed result path was recorded.',
        run_url: semanticRun.html_url,
      });
    }

    const bundle = await readPrivateJson(resultPath);
    if (!bundle) {
      return running(actionId, cfg.authSource, 'Semantic execution finished; CareerHub is waiting for the governed result bundle.', semanticRun.html_url);
    }
    if (String(bundle.action_id || '') !== actionId) {
      return NextResponse.json({
        action_id: actionId,
        state: 'FAILED',
        authSource: cfg.authSource,
        message: 'Semantic result identity did not match the requested CareerHub action.',
        run_url: semanticRun.html_url,
      });
    }

    const profileRuns = await workflowRuns(cfg.repository, cfg.workflow, cfg.token);
    if (!profileRuns.ok) {
      return NextResponse.json({
        action_id: actionId,
        state: 'FAILED',
        authSource: cfg.authSource,
        message: 'CareerHub could not read profile materialization state.',
        detail: `GitHub returned ${profileRuns.status}.`,
      }, { status: 502 });
    }
    const materializeRun = findActionRun(profileRuns.runs, actionId, 'materialize_analysis');

    if (!materializeRun) {
      if (!record?.materialization_dispatched_at) {
        const dispatched = await dispatchMaterialization(cfg, actionId, resultPath);
        if (!dispatched.ok) {
          const detail = await dispatched.text();
          return NextResponse.json({
            action_id: actionId,
            state: 'FAILED',
            authSource: cfg.authSource,
            message: 'Semantic HRDM completed, but CareerHub could not start profile materialization.',
            detail: detail.slice(0, 500),
          }, { status: 502 });
        }
        await writeActionRecord(actionRecordPath, {
          ...(record || {}),
          state: 'RUNNING',
          semantic_run_url: semanticRun.html_url,
          materialization_dispatched_at: new Date().toISOString(),
        });
      }
      return running(actionId, cfg.authSource, 'HRDM-R completed centrally. CareerHub is materializing the governed result into the profile repository.', semanticRun.html_url);
    }

    if (materializeRun.status === 'queued' || materializeRun.status === 'waiting' || materializeRun.status === 'requested' || materializeRun.status === 'pending') {
      return waiting(actionId, cfg.authSource, 'HRDM-R completed centrally. Profile materialization is queued.', materializeRun.html_url);
    }
    if (materializeRun.status !== 'completed') {
      return running(actionId, cfg.authSource, 'HRDM-R completed centrally. Profile artifacts and state are being materialized.', materializeRun.html_url);
    }
    if (materializeRun.conclusion !== 'success') {
      await writeActionRecord(actionRecordPath, {
        ...(record || {}),
        state: 'FAILED',
        failed_at: new Date().toISOString(),
        semantic_run_url: semanticRun.html_url,
        materialization_run_url: materializeRun.html_url,
      });
      return NextResponse.json({
        action_id: actionId,
        state: 'FAILED',
        authSource: cfg.authSource,
        message: 'HRDM-R completed, but the profile repository could not materialize the result.',
        conclusion: materializeRun.conclusion,
        run_url: materializeRun.html_url,
      });
    }

    const profileRoot = await resolveRemoteProfileRoot(cfg.repository, cfg.token, cfg.ref);
    const hrdm = profileRoot === null
      ? bundle.hrdm || null
      : await readJsonFile(cfg.repository, cfg.token, rooted(profileRoot, `output/${actionId}/HRDM_result.json`), cfg.ref) || bundle.hrdm || null;
    const application = profileRoot === null
      ? bundle.application || null
      : await readJsonFile(cfg.repository, cfg.token, rooted(profileRoot, `output/${actionId}/application_package.json`), cfg.ref) || bundle.application || null;

    if (!hrdm) {
      return running(actionId, cfg.authSource, 'Profile materialization finished; CareerHub is waiting for the generated report to become readable.', materializeRun.html_url);
    }

    await writeActionRecord(actionRecordPath, {
      ...(record || {}),
      state: 'COMPLETED',
      completed_at: new Date().toISOString(),
      semantic_run_url: semanticRun.html_url,
      materialization_run_url: materializeRun.html_url,
    });

    return NextResponse.json({
      action_id: actionId,
      state: 'COMPLETED',
      authSource: cfg.authSource,
      message: 'HRDM-R completed and was materialized into the profile repository.',
      process_id: hrdm.process_id ?? hrdm.trace?.process_id ?? null,
      hrdm,
      application,
      semantic_run_url: semanticRun.html_url,
      run_url: materializeRun.html_url,
      result_url: `/analyse/${encodeURIComponent(actionId)}`,
    });
  }

  const response = await workflowRuns(cfg.repository, cfg.workflow, cfg.token);
  if (!response.ok) {
    return NextResponse.json({
      action_id: actionId,
      state: 'FAILED',
      authSource: cfg.authSource,
      message: 'CareerHub could not read the Motor execution state.',
      detail: `GitHub returned ${response.status}.`,
    }, { status: 502 });
  }

  const run = findActionRun(response.runs, actionId);
  if (!run) return waiting(actionId, cfg.authSource, 'The action was accepted and is waiting for the Motor runner.');
  if (run.status === 'queued' || run.status === 'waiting' || run.status === 'requested' || run.status === 'pending') {
    return waiting(actionId, cfg.authSource, 'The Motor has the action and is waiting to start it.', run.html_url);
  }
  if (run.status !== 'completed') return running(actionId, cfg.authSource, 'CareerHub Motor is running the operation.', run.html_url);
  if (run.conclusion !== 'success') {
    return NextResponse.json({
      action_id: actionId,
      state: 'FAILED',
      authSource: cfg.authSource,
      message: 'The Motor started but the operation did not complete successfully.',
      conclusion: run.conclusion,
      run_url: run.html_url,
    });
  }

  return NextResponse.json({
    action_id: actionId,
    state: 'COMPLETED',
    authSource: cfg.authSource,
    message: 'CareerHub Motor operation completed.',
    run_url: run.html_url,
  });
}
