import { list, put } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { loadCareerHubManifest } from '@/lib/manifest';

export async function POST() {
  const profileId = loadCareerHubManifest().profile_id;
  const root = `library/${profileId}/`;
  const result = await list({ prefix: `${root}active/` });
  const index = {
    schema_version: '1.0',
    profile_id: profileId,
    rebuilt_at: new Date().toISOString(),
    active_sources: result.blobs.map((blob) => ({ pathname: blob.pathname, size: blob.size, uploaded_at: blob.uploadedAt }))
  };
  const blob = await put(`${root}indexes/latest.json`, JSON.stringify(index, null, 2), { access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json' });
  return NextResponse.json({ reloaded: true, active_sources: index.active_sources.length, index_pathname: blob.pathname, message: `Library reloaded — ${index.active_sources.length} active sources indexed.` });
}
