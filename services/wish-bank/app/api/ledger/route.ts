import { get, list } from '@vercel/blob';
import { NextResponse } from 'next/server';

function bearer(request: Request) {
  const header = request.headers.get('authorization') ?? '';
  return header.startsWith('Bearer ') ? header.slice(7) : '';
}

async function readRecord(url: string) {
  const result = await get(url, { access: 'private' });
  if (!result || result.statusCode !== 200) return null;
  try { return JSON.parse(await new Response(result.stream).text()); } catch { return null; }
}

export async function GET(request: Request) {
  const expected = process.env.WISH_BANK_SHARED_SECRET;
  if (!expected || bearer(request) !== expected) return NextResponse.json({ error: 'Unauthorized.' }, { status: 401 });

  const params = new URL(request.url).searchParams;
  const profileId = params.get('profile_id')?.trim() || '';
  const wishId = params.get('wish_id')?.trim() || '';
  const prefix = profileId ? `wishes/${profileId}/` : 'wishes/';
  const found = await list({ prefix, limit: 250 });
  const matching = wishId ? found.blobs.filter((blob) => blob.pathname.endsWith(`/${wishId}.json`)) : found.blobs;
  const records = (await Promise.all(matching.slice(0, 100).map((blob) => readRecord(blob.url)))).filter(Boolean);
  records.sort((a: any, b: any) => String(b?.timestamps?.submitted_at ?? '').localeCompare(String(a?.timestamps?.submitted_at ?? '')));

  return NextResponse.json({
    service: 'careerhub-wish-bank',
    authoritative: true,
    count: records.length,
    profile_id: profileId || null,
    wish_id: wishId || null,
    records,
  });
}
