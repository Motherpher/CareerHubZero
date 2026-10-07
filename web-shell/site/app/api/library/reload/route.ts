import { put } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { listLibrarySources } from '@/lib/library-evidence';
import { assertProfileOwnedPath, ProfileBindingError, resolveRuntimeProfileContext } from '@/lib/profile-context';

export async function POST() {
  try {
    const context = resolveRuntimeProfileContext();
    const sources = await listLibrarySources(context);
    const activeSources = sources
      .filter(source => source.status === 'ACTIVE' && source.extraction.state === 'COMPLETE' && source.extraction.extracted_text_ref)
      .map(source => ({
        source_id: source.source_id,
        filename: source.filename,
        document_class: source.document_class,
        hash: source.hash,
        status: source.status,
        extracted_text_ref: source.extraction.extracted_text_ref,
        char_count: source.extraction.char_count,
      }));
    const index = {
      schema_version: '2.0',
      profile_id: context.profileId,
      repository: context.declaredRepository,
      deployment_id: context.deploymentId,
      rebuilt_at: new Date().toISOString(),
      index_state: { status: 'CURRENT', active_source_count: activeSources.length, active_source_ids: activeSources.map(source => source.source_id) },
      active_sources: activeSources,
    };
    const indexPath = `${context.libraryPrefix}indexes/latest.json`;
    assertProfileOwnedPath(indexPath, context.libraryPrefix);
    const blob = await put(indexPath, JSON.stringify(index, null, 2), { access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json' });
    return NextResponse.json({
      profile_id: context.profileId,
      reloaded: true,
      active_sources: activeSources.length,
      active_source_ids: activeSources.map(source => source.source_id),
      index_pathname: blob.pathname,
      message: `Library evidence index rebuilt — ${activeSources.length} ACTIVE, successfully ingested sources available to analysis.`,
    });
  } catch (error) {
    if (error instanceof ProfileBindingError) return NextResponse.json({ error: error.message, code: 'PROFILE_BINDING_FAILED' }, { status: 409 });
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Library evidence index failed.' }, { status: 500 });
  }
}
