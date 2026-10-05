import { randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';

function bearer(request: Request) {
  const header = request.headers.get('authorization') ?? '';
  return header.startsWith('Bearer ') ? header.slice(7) : '';
}

export async function POST(request: Request) {
  const expectedSecret = process.env.WISH_BANK_SHARED_SECRET;
  const githubToken = process.env.WISH_BANK_GITHUB_TOKEN;
  const repo = process.env.WISH_BANK_REPOSITORY ?? 'Motherpher/CareerHubZero';

  if (!expectedSecret || !githubToken) {
    return NextResponse.json({ error: 'Wish Bank service is not configured.' }, { status: 503 });
  }

  if (bearer(request) !== expectedSecret) {
    return NextResponse.json({ error: 'Unauthorized.' }, { status: 401 });
  }

  const payload = await request.json();
  const text = typeof payload?.submission?.text === 'string' ? payload.submission.text.trim() : '';
  const profileId = typeof payload?.source?.profile_id === 'string' ? payload.source.profile_id : 'unknown';

  if (text.length < 3 || text.length > 4000) {
    return NextResponse.json({ error: 'Invalid wish text.' }, { status: 400 });
  }

  const wishId = `WISH-${new Date().toISOString().slice(0, 10).replaceAll('-', '')}-${randomUUID().slice(0, 8).toUpperCase()}`;
  const submittedAt = new Date().toISOString();
  const titleSnippet = text.replace(/\s+/g, ' ').slice(0, 90);

  const body = [
    `## ${wishId}`,
    '',
    text,
    '',
    '### Intake metadata',
    '',
    `- **Profile:** ${profileId}`,
    `- **Display label:** ${payload?.source?.display_label ?? ''}`,
    `- **Route:** ${payload?.source?.route ?? '/'}`,
    `- **Language:** ${payload?.source?.language ?? 'en'}`,
    `- **CareerHub version:** ${payload?.source?.careerhub_version ?? 'unknown'}`,
    `- **User category:** ${payload?.submission?.user_category ?? 'none'}`,
    `- **Location note:** ${payload?.submission?.location_note ?? 'none'}`,
    `- **Submitted:** ${submittedAt}`,
    '',
    '### Product-development state',
    '',
    '- **Status:** NEW',
    '- **Scope:** untriaged',
    '- **Severity:** untriaged',
    '- **Development leverage:** untriaged',
    '- **Cluster:** none',
    '- **Candidate WP:** none',
    '- **WP:** none',
    '',
    '<!-- careerhub-wish-bank -->'
  ].join('\n');

  const response = await fetch(`https://api.github.com/repos/${repo}/issues`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${githubToken}`,
      accept: 'application/vnd.github+json',
      'x-github-api-version': '2022-11-28',
      'content-type': 'application/json'
    },
    body: JSON.stringify({
      title: `[WISH] ${profileId}: ${titleSnippet}`,
      body
    })
  });

  if (!response.ok) {
    const detail = await response.text();
    console.error('Wish Bank GitHub intake failed', response.status, detail);
    return NextResponse.json({ error: 'Central Wish Bank write failed.' }, { status: 502 });
  }

  const issue = await response.json();
  return NextResponse.json({
    accepted: true,
    wish_id: wishId,
    issue_number: issue.number,
    message: 'Wish accepted into the CareerHub development bank.'
  });
}
