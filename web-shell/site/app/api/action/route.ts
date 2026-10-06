import { issueSignedToken, presignUrl, put } from '@vercel/blob';
import { getToken } from '@vercel/connect';
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

const DEFAULT_GITHUB_CONNECTOR = 'github/amber-bell';
const SEMANTIC_REPOSITORY = process.env.CAREERHUB_SEMANTIC_REPOSITORY || 'Motherpher/CareerHubZero';
const SEMANTIC_WORKFLOW = process.env.CAREERHUB_SEMANTIC_WORKFLOW || 'careerhub-semantic.yml';
const SEMANTIC_REF = process.env.CAREERHUB_SEMANTIC_REF || 'main';

type AuthSource = 'environment' | 'vercel-connect' | 'none';

async function resolveGitHubToken(): Promise<{
  token: string;
  authSource: AuthSource;
  connector: string | null;
}> {
  const explicit = (process.env.CAREERHUB_GITHUB_TOKEN || '').trim();
  if (explicit) {
    return { token: explicit, authSource: 'environment', connector: null };
  }

  const connector = (process.env.CAREERHUB_GITHUB_CONNECTOR || DEFAULT_GITHUB_CONNECTOR).trim();
  if (!connector) return { token: '', authSource: 'none', connector: null };

  try {
    const token = await getToken(connector, { subject: { type: 'app' } });
    return {
      token: typeof token === 'string' ? token : '',
      authSource: token ? 'vercel-connect' : 'none',
      connector,
    };
  } catch (error) {
    console.error('CareerHub Vercel Connect GitHub token exchange failed.', error);
    return { token: '', authSource: 'none', connector };
  }
}

function githubConfig(token: string) {
  return {
    repository: process.env.CAREERHUB_GITHUB_REPOSITORY || '',
    token,
    workflow: process.env.CAREERHUB_GITHUB_WORKFLOW || 'careerhub-operations.yml',
    ref: process.env.CAREERHUB_GITHUB_REF || 'main',
  };
}

function githubHeaders(token: string, userAgent: string) {
  return {
    accept: 'application/vnd.github+json',
    authorization: `Bearer ${token}`,
    'x-github-api-version': '2022-11-28',
    'user-agent': userAgent,
  };
}

async function workflowReachable(repository: string, workflow: string, token: string) {
  if (!repository || !workflow || !token) return false;
  const response = await fetch(`https://api.github.com/repos/${repository}/actions/workflows/${encodeURIComponent(workflow)}`, {
    headers: githubHeaders(token, 'CareerHub-action-preflight'),
    cache: 'no-store',
  });
  return response.ok;
}

async function executionPreflight() {
  const auth = await resolveGitHubToken();
  const cfg = githubConfig(auth.token);

  if (!cfg.repository) {
    return {
      ready: false,
      dispatcherConfigured: false,
      workflowReachable: false,
      profileWorkflowReachable: false,
      semanticWorkflowReachable: false,
      authSource: auth.authSource,
      connector: auth.connector,
      state: 'WAITING_FOR_EXECUTION',
      message: 'CareerHub cannot execute Motor actions from this deployment yet.',
      detail: 'The profile deployment is missing its GitHub repository binding.',
      cfg,
    };
  }

  if (!cfg.token) {
    return {
      ready: false,
      dispatcherConfigured: false,
      workflowReachable: false,
      profileWorkflowReachable: false,
      semanticWorkflowReachable: false,
      authSource: auth.authSource,
      connector: auth.connector,
      state: 'WAITING_FOR_EXECUTION',
      message: 'CareerHub cannot execute Motor actions from this deployment yet.',
      detail: auth.connector
        ? 'The profile is connected to GitHub, but Vercel Connect could not issue a GitHub App token.'
        : 'The profile deployment has no GitHub dispatcher credential.',
      cfg,
    };
  }

  const [profileWorkflow, semanticWorkflow] = await Promise.all([
    workflowReachable(cfg.repository, cfg.workflow, cfg.token),
    workflowReachable(SEMANTIC_REPOSITORY, SEMANTIC_WORKFLOW, cfg.token),
  ]);
  const ready = profileWorkflow && semanticWorkflow;

  return {
    ready,
    dispatcherConfigured: true,
    workflowReachable: ready,
    profileWorkflowReachable: profileWorkflow,
    semanticWorkflowReachable: semanticWorkflow,
    authSource: auth.authSource,
    connector: auth.connector,
    state: ready ? 'READY' : 'WAITING_FOR_EXECUTION',
    message: ready
      ? 'CareerHub Motor execution is available.'
      : 'CareerHub is connected, but one of its governed Motor workflows cannot be reached.',
    detail: ready
      ? 'Profile operations and central semantic HRDM execution are both reachable.'
      : `Profile workflow reachable: ${profileWorkflow}; central semantic workflow reachable: ${semanticWorkflow}.`,
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
    profileWorkflowReachable: probe.profileWorkflowReachable,
    semanticWorkflowReachable: probe.semanticWorkflowReachable,
    authSource: probe.authSource,
    state: probe.state,
    message: probe.message,
    detail: probe.detail,
    repository: probe.cfg.repository || null,
    semanticRepository: SEMANTIC_REPOSITORY,
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
      authSource: preflight.authSource,
      message: preflight.message,
      detail: preflight.detail,
    }, { status: 503 });
  }

  const manifest = loadCareerHubManifest();
  const actionId = `ACT-${new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)}-${randomUUID().slice(0, 8)}`;
  const semanticResultPath = operation === 'analyse_role'
    ? `semantic-results/${manifest.profile_id}/${actionId}.json`
    : null;

  let resultUploadUrl = '';
  if (semanticResultPath) {
    try {
      const validUntil = Date.now() + 60 * 60 * 1000;
      const signed = await issueSignedToken({
        pathname: semanticResultPath,
        operations: ['put'],
        allowedContentTypes: ['application/json'],
        maximumSizeInBytes: 25 * 1024 * 1024,
        validUntil,
      });
      const presigned = await presignUrl(signed, {
        operation: 'put',
        pathname: semanticResultPath,
        access: 'private',
        allowedContentTypes: ['application/json'],
        maximumSizeInBytes: 25 * 1024 * 1024,
        addRandomSuffix: false,
        allowOverwrite: true,
        validUntil,
      });
      resultUploadUrl = presigned.presignedUrl;
    } catch (error) {
      console.error('CareerHub could not prepare semantic result storage.', error);
      return NextResponse.json({
        action_id: actionId,
        state: 'FAILED',
        dispatched: false,
        message: 'CareerHub could not prepare secure semantic result storage.',
      }, { status: 502 });
    }
  }

  const record = {
    schema_version: '1.2',
    action_id: actionId,
    profile_id: manifest.profile_id,
    operation,
    payload,
    requested_at: new Date().toISOString(),
    state: 'PREPARING',
    dispatcher_auth: preflight.authSource,
    semantic_result_path: semanticResultPath,
    executor_repository: operation === 'analyse_role' ? SEMANTIC_REPOSITORY : preflight.cfg.repository,
    executor_workflow: operation === 'analyse_role' ? SEMANTIC_WORKFLOW : preflight.cfg.workflow,
  };

  let stored = false;
  try {
    await put(`actions/${manifest.profile_id}/${actionId}.json`, JSON.stringify(record, null, 2), {
      access: 'private',
      addRandomSuffix: false,
      allowOverwrite: true,
      contentType: 'application/json',
    });
    stored = true;
  } catch {
    stored = false;
  }

  const cfg = preflight.cfg;
  const targetRepository = operation === 'analyse_role' ? SEMANTIC_REPOSITORY : cfg.repository;
  const targetWorkflow = operation === 'analyse_role' ? SEMANTIC_WORKFLOW : cfg.workflow;
  const targetRef = operation === 'analyse_role' ? SEMANTIC_REF : cfg.ref;
  const inputs = operation === 'analyse_role'
    ? {
        action_id: actionId,
        profile_repository: cfg.repository,
        payload: JSON.stringify(payload),
        result_upload_url: resultUploadUrl,
      }
    : {
        operation,
        action_id: actionId,
        payload: JSON.stringify(payload),
      };

  const response = await fetch(`https://api.github.com/repos/${targetRepository}/actions/workflows/${encodeURIComponent(targetWorkflow)}/dispatches`, {
    method: 'POST',
    headers: {
      ...githubHeaders(cfg.token, 'CareerHub-action-gateway'),
      'content-type': 'application/json',
    },
    body: JSON.stringify({ ref: targetRef, inputs }),
  });

  if (!response.ok) {
    const detail = await response.text();
    return NextResponse.json({
      error: 'CareerHub could not start this Motor action.',
      action_id: actionId,
      state: 'FAILED',
      dispatched: false,
      stored,
      authSource: preflight.authSource,
      detail: detail.slice(0, 500),
    }, { status: 502 });
  }

  return NextResponse.json({
    action_id: actionId,
    state: 'WAITING_FOR_EXECUTION',
    dispatched: true,
    stored,
    authSource: preflight.authSource,
    executor: operation === 'analyse_role' ? 'central-semantic-motor' : 'profile-motor',
    message: 'The action was accepted and is waiting for the Motor to begin execution.',
    technical_reference: actionId,
    status_url: `/api/action/status?action_id=${encodeURIComponent(actionId)}`,
    result_url: operation === 'analyse_role' ? `/analyse/${encodeURIComponent(actionId)}` : null,
  }, { status: 202 });
}
