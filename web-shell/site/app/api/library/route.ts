import { del as removeBlob, list, put, rename } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { randomUUID } from 'node:crypto';
import { assertProfileOwnedPath, ProfileBindingError, resolveRuntimeProfileContext } from '@/lib/profile-context';

const DOCUMENT_CLASSES = new Set(['cv','certificate','diploma','employment_certificate','role_description','work_sample','portfolio','project_description','reference','course_record','prior_application','other']);
function safeName(name: string) { return name.replace(/[^a-zA-Z0-9._-]+/g, '-').replace(/-+/g, '-').slice(0, 140) || 'document'; }
function bindingFailure(error: unknown) {
  const message = error instanceof Error ? error.message : 'CareerHub profile binding failed.';
  return NextResponse.json({ error: message, code: 'PROFILE_BINDING_FAILED' }, { status: 409 });
}

export async function GET() {
  try {
    const context = resolveRuntimeProfileContext();
    const result = await list({ prefix: context.libraryPrefix });
    const files = result.blobs.filter((blob) => !blob.pathname.includes('/indexes/')).map((blob) => {
      assertProfileOwnedPath(blob.pathname, context.libraryPrefix);
      const relative = blob.pathname.slice(context.libraryPrefix.length);
      const parts = relative.split('/');
      const status = parts[0] === 'active' ? 'ACTIVE' : 'INACTIVE';
      const documentClass = parts.length >= 3 ? parts[1] : 'other';
      const stored = parts[parts.length - 1] ?? blob.pathname;
      return {
        pathname: blob.pathname,
        display_name: stored.replace(/^[a-f0-9-]+--/i, ''),
        active: status === 'ACTIVE',
        status,
        document_class: documentClass,
        uploaded_at: blob.uploadedAt,
        size: blob.size,
      };
    });
    return NextResponse.json({ profile_id: context.profileId, files });
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
    const state = requestedState === 'inactive' ? 'inactive' : 'active';
    const pathname = `${context.libraryPrefix}${state}/${documentClass}/${randomUUID()}--${safeName(file.name)}`;
    assertProfileOwnedPath(pathname, context.libraryPrefix);
    const blob = await put(pathname, file, { access: 'private', addRandomSuffix: false });
    return NextResponse.json({ profile_id: context.profileId, uploaded: true, pathname: blob.pathname, active: state === 'active', document_class: documentClass });
  } catch (error) {
    if (error instanceof ProfileBindingError) return bindingFailure(error);
    throw error;
  }
}

export async function PATCH(request: Request) {
  try {
    const context = resolveRuntimeProfileContext();
    const body = await request.json();
    const pathname = typeof body?.pathname === 'string' ? body.pathname : '';
    const action = body?.action;
    assertProfileOwnedPath(pathname, context.libraryPrefix);
    if (action === 'erase') { await removeBlob(pathname); return NextResponse.json({ profile_id: context.profileId, erased: true }); }
    if (action !== 'activate' && action !== 'deactivate') return NextResponse.json({ error: 'Invalid action.' }, { status: 400 });
    const target = pathname.replace(/\/(active|inactive)\//, `/${action === 'activate' ? 'active' : 'inactive'}/`);
    assertProfileOwnedPath(target, context.libraryPrefix);
    if (target === pathname) return NextResponse.json({ profile_id: context.profileId, updated: true, pathname });
    const blob = await rename(pathname, target, { access: 'private' });
    return NextResponse.json({ profile_id: context.profileId, updated: true, pathname: blob.pathname });
  } catch (error) {
    if (error instanceof ProfileBindingError) return bindingFailure(error);
    throw error;
  }
}
