import { list, put } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { assertProfileOwnedPath, ProfileBindingError, resolveRuntimeProfileContext } from '@/lib/profile-context';

export async function POST() {
  try {
    const context = resolveRuntimeProfileContext();
    const result = await list({ prefix: `${context.libraryPrefix}active/` });
    const activeSources = result.blobs.map((blob) => {
      assertProfileOwnedPath(blob.pathname, context.libraryPrefix);
      return { pathname: blob.pathname, size: blob.size, uploaded_at: blob.uploadedAt };
    });
    const index = {
      schema_version: '1.0',
      profile_id: context.profileId,
      repository: context.declaredRepository,
      deployment_id: context.deploymentId,
      rebuilt_at: new Date().toISOString(),
      active_sources: activeSources,
    };
    const indexPath = `${context.libraryPrefix}indexes/latest.json`;
    assertProfileOwnedPath(indexPath, context.libraryPrefix);
    const blob = await put(indexPath, JSON.stringify(index, null, 2), { access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json' });
    return NextResponse.json({ profile_id: context.profileId, reloaded: true, active_sources: activeSources.length, index_pathname: blob.pathname, message: `Library reloaded — ${activeSources.length} active sources indexed.` });
  } catch (error) {
    if (error instanceof ProfileBindingError) {
      return NextResponse.json({ error: error.message, code: 'PROFILE_BINDING_FAILED' }, { status: 409 });
    }
    throw error;
  }
}
