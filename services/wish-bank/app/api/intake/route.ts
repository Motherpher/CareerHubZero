import { randomUUID } from 'node:crypto';
import { put } from '@vercel/blob';
import { NextResponse } from 'next/server';

function bearer(request: Request) {
  const header = request.headers.get('authorization') ?? '';
  return header.startsWith('Bearer ') ? header.slice(7) : '';
}

type Target = 'MOTOR' | 'PROFILE' | 'BOTH' | 'UNTRIAGED';
type Domain = 'PROFILE' | 'SEARCH' | 'GEOGRAPHY' | 'ANALYSE' | 'APPLY' | 'TRACK' | 'LIBRARY' | 'UX' | 'ACCESSIBILITY' | 'PERFORMANCE' | 'NEW_CAPABILITY' | 'OTHER';

function classify(text: string, userCategory?: string | null): { target: Target; domain: Domain; tags: string[] } {
  const value = `${userCategory ?? ''} ${text}`.toLowerCase();
  let domain: Domain = 'OTHER';
  if (/profile|cv|resume|kompetens|experience|merit/.test(value)) domain = 'PROFILE';
  else if (/search|find|job|role|filter/.test(value)) domain = 'SEARCH';
  else if (/geograph|location|city|region|kommun|distance|commute/.test(value)) domain = 'GEOGRAPHY';
  else if (/analyse|analysis|hrdm|fit|match/.test(value)) domain = 'ANALYSE';
  else if (/apply|application|letter|cover/.test(value)) domain = 'APPLY';
  else if (/track|pipeline|interview|status/.test(value)) domain = 'TRACK';
  else if (/library|upload|document|file/.test(value)) domain = 'LIBRARY';
  else if (/accessib|contrast|keyboard|screen reader/.test(value)) domain = 'ACCESSIBILITY';
  else if (/slow|performance|error|crash|reliab/.test(value)) domain = 'PERFORMANCE';
  else if (/new capability|new feature|would like to be able/.test(value)) domain = 'NEW_CAPABILITY';
  else if (/ux|navigate|navigation|understand|clear|layout|design|button/.test(value)) domain = 'UX';

  const explicitProfile = /only me|my profile|for me|personal to me|my hub|my careerhub/.test(value);
  const explicitMotor = /everyone|all users|all hubs|motor|central|every careerhub/.test(value);
  let target: Target = 'UNTRIAGED';
  if (explicitProfile && explicitMotor) target = 'BOTH';
  else if (explicitProfile) target = 'PROFILE';
  else if (explicitMotor) target = 'MOTOR';

  return { target, domain, tags: [`target:${target.toLowerCase()}`, `domain:${domain.toLowerCase()}`] };
}

export async function POST(request: Request) {
  const expectedSecret = process.env.WISH_BANK_SHARED_SECRET;
  if (!expectedSecret || bearer(request) !== expectedSecret) {
    return NextResponse.json({ error: 'Unauthorized.' }, { status: 401 });
  }

  const payload = await request.json();
  const text = typeof payload?.submission?.text === 'string' ? payload.submission.text.trim() : '';
  const profileId = typeof payload?.source?.profile_id === 'string' ? payload.source.profile_id : 'unknown';
  if (text.length < 3 || text.length > 4000) return NextResponse.json({ error: 'Invalid wish text.' }, { status: 400 });

  const wishId = `WISH-${new Date().toISOString().slice(0, 10).replaceAll('-', '')}-${randomUUID().slice(0, 8).toUpperCase()}`;
  const submittedAt = new Date().toISOString();
  const segmentation = classify(text, payload?.submission?.user_category ?? null);
  const record = {
    schema_version: '1.1',
    wish_id: wishId,
    source: {
      profile_id: profileId,
      display_label: payload?.source?.display_label ?? '',
      route: payload?.source?.route ?? '/',
      language: payload?.source?.language ?? 'en',
      careerhub_version: payload?.source?.careerhub_version ?? null
    },
    submission: {
      text,
      user_category: payload?.submission?.user_category ?? null,
      location_note: payload?.submission?.location_note ?? null
    },
    segmentation: {
      target: segmentation.target,
      domain: segmentation.domain,
      tags: segmentation.tags,
      confidence: segmentation.target === 'UNTRIAGED' ? 'LOW' : 'MEDIUM',
      review_required: true
    },
    triage: { status: 'NEW' },
    development: {
      motor_wishlist: segmentation.target === 'MOTOR' || segmentation.target === 'BOTH',
      profile_wishlist: segmentation.target === 'PROFILE' || segmentation.target === 'BOTH',
      profile_id: segmentation.target === 'PROFILE' || segmentation.target === 'BOTH' ? profileId : null,
      candidate_wp_id: null,
      wp_id: null
    },
    timestamps: { submitted_at: submittedAt }
  };

  const blob = await put(`wishes/${profileId}/${wishId}.json`, JSON.stringify(record, null, 2), {
    access: 'private', contentType: 'application/json', addRandomSuffix: false
  });

  const githubToken = process.env.WISH_BANK_GITHUB_TOKEN;
  const repo = process.env.WISH_BANK_REPOSITORY ?? 'Motherpher/CareerHubZero';
  let issueNumber: number | null = null;
  if (githubToken) {
    const body = [
      `## ${wishId}`, '', text, '',
      '### Segmentation',
      `- **Target:** ${segmentation.target}`,
      `- **Domain:** ${segmentation.domain}`,
      `- **Profile:** ${profileId}`,
      `- **Tags:** ${segmentation.tags.join(', ')}`,
      '- **Review required:** yes', '',
      '### Development routing',
      `- **Motor wishlist:** ${record.development.motor_wishlist}`,
      `- **Profile wishlist:** ${record.development.profile_wishlist}`,
      `- **Profile development line:** ${record.development.profile_id ?? 'none'}`,
      '- **Status:** NEW', '- **Candidate WP:** none', '- **WP:** none', '',
      `Blob record: ${blob.pathname}`,
      '<!-- careerhub-wish-bank -->'
    ].join('\n');
    const response = await fetch(`https://api.github.com/repos/${repo}/issues`, {
      method: 'POST',
      headers: { authorization: `Bearer ${githubToken}`, accept: 'application/vnd.github+json', 'x-github-api-version': '2022-11-28', 'content-type': 'application/json' },
      body: JSON.stringify({ title: `[WISH][${segmentation.target}][${segmentation.domain}] ${profileId}: ${text.replace(/\s+/g, ' ').slice(0, 70)}`, body })
    });
    if (response.ok) issueNumber = (await response.json()).number;
  }

  return NextResponse.json({
    accepted: true,
    wish_id: wishId,
    segmentation,
    issue_number: issueNumber,
    message: 'Wish accepted. It can improve your CareerHub and, when relevant, CareerHub for everyone.'
  });
}
