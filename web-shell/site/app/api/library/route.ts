import { NextResponse } from 'next/server';
import { randomUUID } from 'node:crypto';
import { eraseSource, ingestUpload, listLibrarySources, setSourceStatus } from '@/lib/library-evidence';
import { ProfileBindingError, resolveRuntimeProfileContext } from '@/lib/profile-context';

const DOCUMENT_CLASSES = new Set(['cv','certificate','diploma','employment_certificate','role_description','work_sample','portfolio','project_description','reference','course_record','prior_application','other']);
function bindingFailure(error: unknown) {
  const message = error instanceof Error ? error.message : 'CareerHub profile binding failed.';
  return NextResponse.json({ error: message, code: 'PROFILE_BINDING_FAILED' }, { status: 409 });
}

export async function GET() {
  try {
    const context = resolveRuntimeProfileContext();
    const sources = await listLibrarySources(context);
    return NextResponse.json({
      profile_id: context.profileId,
      files: sources.map(source => ({
        source_id: source.source_id,
        pathname: source.storage.pathname,
        display_name: source.filename,
        active: source.status === 'ACTIVE',
        status: source.status,
        document_class: source.document_class,
        uploaded_at: source.uploaded_at,
        updated_at: source.updated_at,
        size: source.size,
        hash: source.hash,
        ingestion: source.extraction.state,
        char_count: source.extraction.char_count,
        ingestion_error: source.extraction.error,
      })),
    });
  } catch (error) {
    if (error instanceof ProfileBindingError) return bindingFailure(error);
    return NextResponse.json({ files: [], error: 'Library storage is not connected yet.' }, { status: 503 });
  }
}

export async function POST(request: Request) {
  try {
    const context = resolveRuntimeProfileContext();
    const form = await request.formData();
    const file = form.get('file');
    const requestedClass = String(form.get('document_class') ?? 'other');
    const requestedState = String(form.get('initial_state') ?? 'active');
    if (!(file instanceof File)) return NextResponse.json({ error: 'Missing file.' }, { status: 400 });
    if (file.size > 4_300_000) return NextResponse.json({ error: 'Server upload currently supports files up to about 4.3 MB.' }, { status: 413 });
    const documentClass = DOCUMENT_CLASSES.has(requestedClass) ? requestedClass : 'other';
    const source = await ingestUpload(context, randomUUID(), file, documentClass, requestedState !== 'inactive');
    const ok = source.status === 'ACTIVE' || source.status === 'INACTIVE';
    return NextResponse.json({
      profile_id: context.profileId,
      uploaded: true,
      indexed: source.extraction.state === 'COMPLETE',
      source_id: source.source_id,
      pathname: source.storage.pathname,
      status: source.status,
      active: source.status === 'ACTIVE',
      document_class: source.document_class,
      hash: source.hash,
      char_count: source.extraction.char_count,
      error: source.extraction.error,
    }, { status: ok ? 201 : 422 });
  } catch (error) {
    if (error instanceof ProfileBindingError) return bindingFailure(error);
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Library ingestion failed.' }, { status: 500 });
  }
}

export async function PATCH(request: Request) {
  try {
    const context = resolveRuntimeProfileContext();
    const body = await request.json().catch(() => ({}));
    const sourceId = typeof body?.source_id === 'string' ? body.source_id.trim() : '';
    const action = body?.action;
    if (!sourceId || !/^[A-Za-z0-9-]+$/.test(sourceId)) return NextResponse.json({ error: 'A valid source_id is required.' }, { status: 400 });
    if (action === 'erase') {
      await eraseSource(context, sourceId);
      return NextResponse.json({ profile_id: context.profileId, source_id: sourceId, status: 'ERASED', erased: true });
    }
    if (action !== 'activate' && action !== 'deactivate') return NextResponse.json({ error: 'Invalid action.' }, { status: 400 });
    const source = await setSourceStatus(context, sourceId, action);
    return NextResponse.json({ profile_id: context.profileId, source_id: source.source_id, status: source.status, active: source.status === 'ACTIVE', updated: true });
  } catch (error) {
    if (error instanceof ProfileBindingError) return bindingFailure(error);
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Library update failed.' }, { status: 409 });
  }
}
