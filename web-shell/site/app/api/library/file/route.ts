import { get } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { loadCareerHubManifest } from '@/lib/manifest';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const pathname = searchParams.get('pathname') ?? '';
  const profileId = loadCareerHubManifest().profile_id;
  if (!pathname.startsWith(`library/${profileId}/`)) {
    return NextResponse.json({ error: 'Invalid library path.' }, { status: 400 });
  }
  const result = await get(pathname, { access: 'private' });
  if (result?.statusCode !== 200) return new NextResponse('Not found', { status: 404 });
  return new NextResponse(result.stream, {
    headers: {
      'Content-Type': result.blob.contentType,
      'X-Content-Type-Options': 'nosniff'
    }
  });
}
