import { NextResponse } from 'next/server';
import { loadCareerHubManifest } from '@/lib/manifest';
import { loadHubProfile } from '@/lib/profile';

export async function POST(request: Request) {
  const body = await request.json();
  const text = typeof body?.text === 'string' ? body.text.trim() : '';
  const userCategory = typeof body?.category === 'string' ? body.category : null;
  const route = typeof body?.route === 'string' ? body.route : '/';
  const locationNote = typeof body?.location_note === 'string' ? body.location_note.trim() : null;

  if (text.length < 3 || text.length > 4000) {
    return NextResponse.json({ error: 'Wish text must be between 3 and 4000 characters.' }, { status: 400 });
  }

  const endpoint = process.env.CAREERHUB_WISH_ENDPOINT;
  const secret = process.env.CAREERHUB_WISH_SHARED_SECRET;

  if (!endpoint || !secret) {
    return NextResponse.json({ error: 'Wish Bank routing is not configured for this site.' }, { status: 503 });
  }

  const manifest = loadCareerHubManifest();
  const hub = loadHubProfile();
  const payload = {
    source: {
      profile_id: manifest.profile_id,
      display_label: hub.identity.display_name,
      route,
      language: hub.identity.language ?? manifest.ui?.language ?? 'en',
      careerhub_version: process.env.CAREERHUB_VERSION ?? null
    },
    submission: {
      text,
      user_category: userCategory,
      location_note: locationNote
    }
  };

  const upstream = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${secret}`
    },
    body: JSON.stringify(payload),
    cache: 'no-store'
  });

  const responseBody = await upstream.json().catch(() => ({}));

  if (!upstream.ok) {
    return NextResponse.json({ error: 'Wish Bank could not accept the submission.' }, { status: 502 });
  }

  return NextResponse.json({
    accepted: true,
    wish_id: responseBody.wish_id ?? null,
    message: responseBody.message ?? 'Wish submitted.'
  });
}
