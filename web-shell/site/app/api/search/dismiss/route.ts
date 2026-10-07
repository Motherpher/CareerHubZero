import { get, put } from '@vercel/blob';
import { NextRequest, NextResponse } from 'next/server';
import { resolveRuntimeProfileContext } from '@/lib/profile-context';
import { DismissalState, dismissalStatePath } from '@/lib/search-workspace';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function readState(profileId: string): Promise<DismissalState> {
  const pathname = dismissalStatePath(profileId);
  try {
    const result = await get(pathname, { access: 'private' });
    if (!result || result.statusCode !== 200) throw new Error('missing');
    const parsed = JSON.parse(await new Response(result.stream).text()) as DismissalState;
    return parsed?.profile_id === profileId && Array.isArray(parsed.jobs)
      ? parsed
      : { schema_version: '1.0', profile_id: profileId, updated_at: new Date().toISOString(), jobs: [] };
  } catch {
    return { schema_version: '1.0', profile_id: profileId, updated_at: new Date().toISOString(), jobs: [] };
  }
}

async function writeState(state: DismissalState) {
  await put(dismissalStatePath(state.profile_id), JSON.stringify(state, null, 2), {
    access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json',
  });
}

export async function GET() {
  const context = resolveRuntimeProfileContext();
  if (!process.env.BLOB_READ_WRITE_TOKEN) return NextResponse.json({ profileId: context.profileId, persisted: false, jobs: [] });
  const state = await readState(context.profileId);
  return NextResponse.json({ profileId: context.profileId, persisted: true, jobs: state.jobs });
}

export async function POST(request: NextRequest) {
  const context = resolveRuntimeProfileContext();
  if (!process.env.BLOB_READ_WRITE_TOKEN) return NextResponse.json({ error: 'Search decisions storage is not connected.' }, { status: 503 });
  const body = await request.json().catch(() => ({}));
  const identityKey = typeof body?.identityKey === 'string' ? body.identityKey.trim() : '';
  if (!/^[a-f0-9]{64}$/i.test(identityKey)) return NextResponse.json({ error: 'Invalid vacancy identity.' }, { status: 400 });
  const state = await readState(context.profileId);
  const next = state.jobs.filter((job) => job.identityKey !== identityKey);
  next.push({
    identityKey,
    title: typeof body?.title === 'string' ? body.title.slice(0, 300) : '',
    company: typeof body?.company === 'string' ? body.company.slice(0, 300) : '',
    url: typeof body?.url === 'string' ? body.url.slice(0, 2000) : '',
    dismissed_at: new Date().toISOString(),
  });
  const updated: DismissalState = { ...state, updated_at: new Date().toISOString(), jobs: next.slice(-1000) };
  await writeState(updated);
  return NextResponse.json({ profileId: context.profileId, dismissed: true, dismissedCount: updated.jobs.length });
}

export async function DELETE(request: NextRequest) {
  const context = resolveRuntimeProfileContext();
  if (!process.env.BLOB_READ_WRITE_TOKEN) return NextResponse.json({ error: 'Search decisions storage is not connected.' }, { status: 503 });
  const body = await request.json().catch(() => ({}));
  const identityKey = typeof body?.identityKey === 'string' ? body.identityKey.trim() : '';
  if (!/^[a-f0-9]{64}$/i.test(identityKey)) return NextResponse.json({ error: 'Invalid vacancy identity.' }, { status: 400 });
  const state = await readState(context.profileId);
  const jobs = state.jobs.filter((job) => job.identityKey !== identityKey);
  const updated: DismissalState = { ...state, updated_at: new Date().toISOString(), jobs };
  await writeState(updated);
  return NextResponse.json({ profileId: context.profileId, restored: true, dismissedCount: jobs.length });
}
