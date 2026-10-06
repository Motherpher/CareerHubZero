import { loadCareerHubManifest } from '@/lib/manifest';

export type ProfileBindingState = 'BOUND' | 'UNBOUND_LOCAL' | 'MISMATCH';

export type RuntimeProfileContext = {
  profileId: string;
  declaredRepository: string | null;
  runtimeRepository: string | null;
  deploymentId: string;
  bindingState: ProfileBindingState;
  libraryPrefix: string;
  actionPrefix: string;
  semanticResultPrefix: string;
};

function cleanRepository(value: string | undefined | null): string | null {
  const text = (value ?? '').trim().replace(/^https?:\/\/github\.com\//i, '').replace(/\.git$/i, '');
  return text ? text.toLowerCase() : null;
}

function runtimeRepository(): string | null {
  const explicit = cleanRepository(process.env.CAREERHUB_GITHUB_REPOSITORY);
  if (explicit) return explicit;
  const owner = (process.env.VERCEL_GIT_REPO_OWNER || '').trim();
  const slug = (process.env.VERCEL_GIT_REPO_SLUG || '').trim();
  return owner && slug ? cleanRepository(`${owner}/${slug}`) : null;
}

export class ProfileBindingError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ProfileBindingError';
  }
}

export function resolveRuntimeProfileContext(options: { requireBinding?: boolean } = {}): RuntimeProfileContext {
  const manifest = loadCareerHubManifest();
  const profileId = String(manifest.profile_id || '').trim();
  if (!profileId || !/^[a-z0-9][a-z0-9._-]*$/i.test(profileId)) {
    throw new ProfileBindingError('CareerHub manifest has an invalid profile_id.');
  }

  const declaredRepository = cleanRepository(manifest.binding?.repository);
  const actualRepository = runtimeRepository();
  const requireBinding = options.requireBinding ?? process.env.NODE_ENV === 'production';

  let bindingState: ProfileBindingState = 'UNBOUND_LOCAL';
  if (declaredRepository && actualRepository) {
    bindingState = declaredRepository === actualRepository ? 'BOUND' : 'MISMATCH';
  } else if (requireBinding) {
    throw new ProfileBindingError('CareerHub production profile is missing its repository binding.');
  }

  if (bindingState === 'MISMATCH') {
    throw new ProfileBindingError(
      `CareerHub profile/repository mismatch: manifest=${declaredRepository}; runtime=${actualRepository}.`,
    );
  }

  const deploymentId =
    (process.env.VERCEL_PROJECT_ID || process.env.VERCEL_PROJECT_PRODUCTION_URL || manifest.binding?.deployment || '').trim() ||
    `profile:${profileId}`;
  const namespace = encodeURIComponent(profileId);

  return {
    profileId,
    declaredRepository,
    runtimeRepository: actualRepository,
    deploymentId,
    bindingState,
    libraryPrefix: `library/${namespace}/`,
    actionPrefix: `actions/${namespace}/`,
    semanticResultPrefix: `semantic-results/${namespace}/`,
  };
}

export function assertProfileOwnedPath(pathname: string, prefix: string): string {
  const value = String(pathname || '');
  if (!value.startsWith(prefix)) throw new ProfileBindingError('Path is outside the active CareerHub profile namespace.');
  const relative = value.slice(prefix.length);
  if (!relative || relative.startsWith('/') || relative.includes('..')) {
    throw new ProfileBindingError('Path is not a valid profile-owned object path.');
  }
  return value;
}
