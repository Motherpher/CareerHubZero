import { NextRequest, NextResponse } from 'next/server';
import { loadSearchProfile } from '@/lib/data';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type Lane = { lane_id: string; name: string; bucket: string; priority: number; queries?: string[] };
type Job = {
  id: string;
  title: string;
  company: string;
  location: string;
  published: string;
  deadline: string;
  url: string;
  description: string;
  matchedQuery: string;
  laneId: string;
  laneName: string;
  laneBucket: string;
  score: number;
};

function clean(value: unknown): string {
  return typeof value === 'string' ? value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() : '';
}

function queryTerms(query: string): string[] {
  return query.toLowerCase().match(/[\p{L}\p{N}]+/gu)?.filter((word) => word.length > 2) ?? [];
}

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
  url.searchParams.set('q', query);
  url.searchParams.set('limit', '20');
  url.searchParams.set('offset', '0');

  const response = await fetch(url, {
    headers: { 'User-Agent': 'CareerHub/1.0 (+https://github.com/Motherpher/CareerHubZero)', 'Accept-Language': 'sv,en' },
    cache: 'no-store',
  });
  if (!response.ok) throw new Error(`Platsbanken returned ${response.status}`);
  const payload = await response.json();

  return (payload?.hits ?? []).map((hit: any) => {
    const employer = hit?.employer ?? {};
    const address = hit?.workplace_address ?? {};
    const application = hit?.application_details ?? {};
    const description = hit?.description ?? {};
    const title = clean(hit?.headline || hit?.occupation?.label);
    const company = clean(employer?.name || employer?.workplace);
    const location = [address?.municipality, address?.region].filter(Boolean).join(', ');
    const targetUrl = hit?.webpage_url || application?.url || (hit?.id ? `https://arbetsformedlingen.se/platsbanken/annonser/${hit.id}` : '');
    const base = {
      id: String(hit?.id || `${company}-${title}-${location}`),
      title,
      company,
      location,
      published: String(hit?.publication_date || ''),
      deadline: String(hit?.last_publication_date || ''),
      url: targetUrl,
      description: clean(description?.text_formatted || description?.text),
      matchedQuery: query,
      laneId: lane.lane_id,
      laneName: lane.name,
      laneBucket: lane.bucket,
    };
    return { ...base, score: scoreJob(base, lane, anchors, remoteAllowed) };
  });
}

export async function POST(request: NextRequest) {
  const search = loadSearchProfile();
  if (!search) return NextResponse.json({ error: 'Search Profile could not be loaded.' }, { status: 500 });

  const body = await request.json().catch(() => ({}));
  const requestedLane = typeof body?.lane === 'string' ? body.lane : 'all';
  const overlay = typeof body?.overlay === 'string' ? body.overlay.trim() : '';
  const limit = Math.max(1, Math.min(Number(body?.limit) || 60, 100));
  const lanes: Lane[] = Array.isArray(search?.lanes) ? search.lanes : [];
  const selected = requestedLane === 'all' ? lanes : lanes.filter((lane) => lane.lane_id === requestedLane);
  if (!selected.length) return NextResponse.json({ error: 'No matching search lane is configured.' }, { status: 400 });

  const anchors: string[] = Array.isArray(search?.geographies?.anchors) ? search.geographies.anchors : [];
  const remoteAllowed = Boolean(search?.geographies?.remote_allowed);
  const queryPlan = selected.flatMap((lane) => (lane.queries ?? []).slice(0, requestedLane === 'all' ? 2 : 6).map((raw) => ({
    lane,
    query: overlay ? `${raw} ${overlay}` : raw,
  }))).slice(0, 18);

  const settled = await Promise.allSettled(queryPlan.map(({ query, lane }) => searchPlatsbanken(query, lane, anchors, remoteAllowed)));
  const failures = settled.filter((item) => item.status === 'rejected');
  const jobs = settled.flatMap((item) => item.status === 'fulfilled' ? item.value : []);
  if (!jobs.length && failures.length === settled.length) {
    return NextResponse.json({ error: 'The job source could not be reached. Try again shortly.' }, { status: 502 });
  }

  const deduped = new Map<string, Job>();
  for (const job of jobs) {
    const key = job.url || `${job.company}|${job.title}|${job.location}`.toLowerCase();
    const current = deduped.get(key);
    if (!current || job.score > current.score) deduped.set(key, job);
  }

  const results = [...deduped.values()]
    .filter((job) => job.title && job.url)
    .sort((a, b) => b.score - a.score || b.published.localeCompare(a.published))
    .slice(0, limit)
    .map(({ description: _description, ...job }) => job);

  return NextResponse.json({
    results,
    searchedQueries: queryPlan.length,
    source: 'Arbetsförmedlingen / Platsbanken',
    lane: requestedLane,
    overlayUsed: Boolean(overlay),
    partialSourceFailure: failures.length > 0,
  });
}
