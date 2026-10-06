import { createHash, randomUUID } from 'node:crypto';
import { get, list, put } from '@vercel/blob';
import { NextRequest, NextResponse } from 'next/server';
import { loadSearchProfile } from '@/lib/data';
import { loadCareerHubManifest } from '@/lib/manifest';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type Lane = { lane_id: string; name: string; bucket: string; priority: number; queries?: string[] };
type Novelty = 'NEW' | 'SEEN' | 'CHANGED' | 'UNKNOWN';
type Job = {
  id: string; title: string; company: string; location: string; published: string; deadline: string;
  url: string; description: string; matchedQuery: string; laneId: string; laneName: string; laneBucket: string; score: number;
  identityKey?: string; contentHash?: string; novelty?: Novelty;
};

type StoredJob = { identityKey: string; contentHash: string; title: string; company: string; location: string; url: string; deadline: string };
type SearchSession = {
  schema_version: '1.0'; run_id: string; profile_id: string; comparison_key: string; created_at: string;
  lane: string; query_plan: string[]; source: string; source_health: string; result_count: number; results: StoredJob[];
};

function clean(value: unknown): string {
  return typeof value === 'string' ? value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() : '';
}
function sha(value: string): string { return createHash('sha256').update(value).digest('hex'); }
function queryTerms(query: string): string[] { return query.toLowerCase().match(/[\p{L}\p{N}]+/gu)?.filter((word) => word.length > 2) ?? []; }
function identityKey(job: Job): string { return sha(job.url || `${job.company}|${job.title}|${job.location}`.toLowerCase()); }
function contentHash(job: Job): string { return sha([job.title, job.company, job.location, job.deadline, job.published, job.url].join('|')); }

function scoreJob(job: Omit<Job, 'score'>, lane: Lane, anchors: string[], remoteAllowed: boolean): number {
  const title = job.title.toLowerCase();
  const body = `${job.title} ${job.description}`.toLowerCase();
  const terms = queryTerms(job.matchedQuery);
  const titleHits = terms.filter((term) => title.includes(term)).length;
  const bodyHits = terms.filter((term) => body.includes(term)).length;
  const geographic = anchors.some((anchor) => job.location.toLowerCase().includes(anchor.toLowerCase())) ? 8 : 0;
  const remote = remoteAllowed && /remote|distans|hybrid/i.test(`${job.location} ${job.description}`) ? 4 : 0;
  const priority = Math.max(0, 4 - Number(lane.priority || 3)) * 10;
  return Math.min(100, priority + titleHits * 12 + Math.min(bodyHits, 8) * 2 + geographic + remote);
}

async function searchPlatsbanken(query: string, lane: Lane, anchors: string[], remoteAllowed: boolean): Promise<Job[]> {
  const url = new URL('https://jobsearch.api.jobtechdev.se/search');
  url.searchParams.set('q', query); url.searchParams.set('limit', '20'); url.searchParams.set('offset', '0');
  const response = await fetch(url, {
    headers: { 'User-Agent': 'CareerHub/1.0 (+https://github.com/Motherpher/CareerHubZero)', 'Accept-Language': 'sv,en' },
    cache: 'no-store',
  });
  if (!response.ok) throw new Error(`Platsbanken returned ${response.status}`);
  const payload = await response.json();
  return (payload?.hits ?? []).map((hit: any) => {
    const employer = hit?.employer ?? {}; const address = hit?.workplace_address ?? {}; const application = hit?.application_details ?? {}; const description = hit?.description ?? {};
    const title = clean(hit?.headline || hit?.occupation?.label); const company = clean(employer?.name || employer?.workplace);
    const location = [address?.municipality, address?.region].filter(Boolean).join(', ');
    const targetUrl = hit?.webpage_url || application?.url || (hit?.id ? `https://arbetsformedlingen.se/platsbanken/annonser/${hit.id}` : '');
    const base = { id: String(hit?.id || `${company}-${title}-${location}`), title, company, location, published: String(hit?.publication_date || ''), deadline: String(hit?.last_publication_date || ''), url: targetUrl, description: clean(description?.text_formatted || description?.text), matchedQuery: query, laneId: lane.lane_id, laneName: lane.name, laneBucket: lane.bucket };
    return { ...base, score: scoreJob(base, lane, anchors, remoteAllowed) };
  });
}

async function readPreviousSession(prefix: string): Promise<SearchSession | null> {
  try {
    const found = await list({ prefix, limit: 100 });
    const latest = [...found.blobs].sort((a, b) => String(b.uploadedAt).localeCompare(String(a.uploadedAt)))[0];
    if (!latest) return null;
    const result = await get(latest.url, { access: 'private' });
    if (!result || result.statusCode !== 200) return null;
    return JSON.parse(await new Response(result.stream).text()) as SearchSession;
  } catch {
    return null;
  }
}

export async function POST(request: NextRequest) {
  const search = loadSearchProfile();
  if (!search) return NextResponse.json({ error: 'Search Profile could not be loaded.' }, { status: 500 });
  const manifest = loadCareerHubManifest();
  const body = await request.json().catch(() => ({}));
  const requestedLane = typeof body?.lane === 'string' ? body.lane : 'all';
  const overlay = typeof body?.overlay === 'string' ? body.overlay.trim() : '';
  const limit = Math.max(1, Math.min(Number(body?.limit) || 60, 100));
  const lanes: Lane[] = Array.isArray(search?.lanes) ? search.lanes : [];
  const selected = requestedLane === 'all' ? lanes : lanes.filter((lane) => lane.lane_id === requestedLane);
  if (!selected.length) return NextResponse.json({ error: 'No matching search lane is configured.' }, { status: 400 });

  const anchors: string[] = Array.isArray(search?.geographies?.anchors) ? search.geographies.anchors : [];
  const remoteAllowed = Boolean(search?.geographies?.remote_allowed);
  const queryPlan = selected.flatMap((lane) => (lane.queries ?? []).slice(0, requestedLane === 'all' ? 2 : 6).map((raw) => ({ lane, query: overlay ? `${raw} ${overlay}` : raw }))).slice(0, 18);
  const startedAt = new Date().toISOString();
  const runId = `SEARCH-${startedAt.replace(/[-:.TZ]/g, '').slice(0, 14)}-${randomUUID().slice(0, 8)}`;
  const comparisonKey = sha(JSON.stringify({ requestedLane, queries: queryPlan.map((x) => x.query), anchors, remoteAllowed })).slice(0, 20);
  const prefix = `search-sessions/${manifest.profile_id}/${comparisonKey}/`;

  const settled = await Promise.allSettled(queryPlan.map(({ query, lane }) => searchPlatsbanken(query, lane, anchors, remoteAllowed)));
  const failures = settled.filter((item) => item.status === 'rejected');
  const jobs = settled.flatMap((item) => item.status === 'fulfilled' ? item.value : []);
  if (!jobs.length && failures.length === settled.length) {
    return NextResponse.json({ error: 'The job source could not be reached. No result delta was recorded.', runId, sourceHealth: 'FAILED' }, { status: 502 });
  }

  const deduped = new Map<string, Job>();
  for (const job of jobs) {
    const key = job.url || `${job.company}|${job.title}|${job.location}`.toLowerCase();
    const current = deduped.get(key);
    if (!current || job.score > current.score) deduped.set(key, job);
  }
  const current = [...deduped.values()].filter((job) => job.title && job.url).sort((a, b) => b.score - a.score || b.published.localeCompare(a.published)).slice(0, limit);
  current.forEach((job) => { job.identityKey = identityKey(job); job.contentHash = contentHash(job); });

  const storageAvailable = Boolean(process.env.BLOB_READ_WRITE_TOKEN);
  const previous = storageAvailable ? await readPreviousSession(prefix) : null;
  const previousMap = new Map((previous?.results ?? []).map((job) => [job.identityKey, job]));
  for (const job of current) {
    if (!storageAvailable) job.novelty = 'UNKNOWN';
    else if (!previousMap.has(job.identityKey!)) job.novelty = 'NEW';
    else if (previousMap.get(job.identityKey!)?.contentHash !== job.contentHash) job.novelty = 'CHANGED';
    else job.novelty = 'SEEN';
  }

  const nowKeys = new Set(current.map((job) => job.identityKey));
  const removed = previous?.results.filter((job) => !nowKeys.has(job.identityKey)) ?? [];
  const sourceHealth = failures.length ? 'DEGRADED' : 'HEALTHY';
  let persisted = false;
  if (storageAvailable) {
    const session: SearchSession = {
      schema_version: '1.0', run_id: runId, profile_id: manifest.profile_id, comparison_key: comparisonKey, created_at: new Date().toISOString(), lane: requestedLane,
      query_plan: queryPlan.map((x) => x.query), source: 'Arbetsförmedlingen / Platsbanken', source_health: sourceHealth, result_count: current.length,
      results: current.map((job) => ({ identityKey: job.identityKey!, contentHash: job.contentHash!, title: job.title, company: job.company, location: job.location, url: job.url, deadline: job.deadline })),
    };
    try {
      await put(`${prefix}${runId}.json`, JSON.stringify(session, null, 2), { access: 'private', addRandomSuffix: false, contentType: 'application/json' });
      persisted = true;
    } catch {
      persisted = false;
    }
  }

  const results = current.map(({ description: _description, contentHash: _contentHash, ...job }) => job);
  const counts = {
    new: results.filter((job) => job.novelty === 'NEW').length,
    seen: results.filter((job) => job.novelty === 'SEEN').length,
    changed: results.filter((job) => job.novelty === 'CHANGED').length,
    unknown: results.filter((job) => job.novelty === 'UNKNOWN').length,
    removed: removed.length,
  };

  return NextResponse.json({
    runId, currentSearchAt: startedAt, previousSuccessfulSearchAt: previous?.created_at ?? null,
    baselineEstablished: storageAvailable && !previous, historyAvailable: storageAvailable, persisted,
    results, counts, searchedQueries: queryPlan.length, source: 'Arbetsförmedlingen / Platsbanken', sourceHealth,
    sourceCoverage: ['Arbetsförmedlingen / Platsbanken'], lane: requestedLane, overlayUsed: Boolean(overlay), partialSourceFailure: failures.length > 0,
  });
}
