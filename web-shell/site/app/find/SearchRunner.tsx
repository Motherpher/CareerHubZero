'use client';

import { FormEvent, useEffect, useState } from 'react';

type Novelty = 'NEW' | 'SEEN' | 'CHANGED' | 'UNKNOWN';
type JobType = 'permanent' | 'temporary' | 'fulltime' | 'parttime' | 'consulting';
type WorkMode = 'onsite' | 'hybrid' | 'remote';
type SearchFilters = {
  jobTypes: JobType[]; workModes: WorkMode[]; publishedFrom: string; publishedTo: string;
  deadlineFrom: string; deadlineTo: string; publishedPresetDays: number | null;
};
type SearchResult = {
  id: string; identityKey: string; title: string; company: string; location: string; published: string; deadline: string; url: string;
  matchedQuery: string; laneId: string; laneName: string; laneBucket: string; score: number; novelty: Novelty; jobType: string; workMode: WorkMode;
};
type SearchResponse = {
  runId: string; currentSearchAt: string; previousSuccessfulSearchAt: string | null; baselineEstablished: boolean; historyAvailable: boolean; persisted: boolean;
  filters: SearchFilters; results: SearchResult[]; dismissedResults: SearchResult[];
  counts: { checked: number; matched: number; visible: number; dismissed: number; new: number; seen: number; changed: number; unknown: number; removed: number };
  searchedQueries: number; source: string; sourceHealth: string; sourceCoverage: string[]; lane: string; overlayUsed: boolean; partialSourceFailure: boolean;
};

const EMPTY_FILTERS: SearchFilters = { jobTypes: [], workModes: [], publishedFrom: '', publishedTo: '', deadlineFrom: '', deadlineTo: '', publishedPresetDays: null };

function analyseHref(result: SearchResult) {
  const params = new URLSearchParams({ job_url: result.url, title: result.title, company: result.company, deadline: (result.deadline ?? '').slice(0, 10), lane: ['core', 'adjacent', 'bridge'].includes(result.laneBucket) ? result.laneBucket : 'core' });
  return `/analyse?${params.toString()}`;
}

function toggleValue<T extends string>(values: T[], value: T): T[] {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
}

export default function SearchRunner({ language = 'en' }: { language?: string }) {
  const sv = language.toLowerCase().startsWith('sv');
  const [overlay, setOverlay] = useState('');
  const [filters, setFilters] = useState<SearchFilters>(EMPTY_FILTERS);
  const [loading, setLoading] = useState(false);
  const [decisionBusy, setDecisionBusy] = useState('');
  const [error, setError] = useState('');
  const [data, setData] = useState<SearchResponse | null>(null);
  const [showSeen, setShowSeen] = useState(false);
  const [showDismissed, setShowDismissed] = useState(false);

  useEffect(() => {
    fetch('/api/search', { cache: 'no-store' })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => { if (payload?.filters) setFilters({ ...EMPTY_FILTERS, ...payload.filters }); })
      .catch(() => undefined);
  }, []);

  async function runSearch(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError('');
    try {
      const response = await fetch('/api/search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lane: 'all', overlay: overlay.trim(), filters, limit: 100 }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload?.error || (sv ? 'Sökningen kunde inte genomföras.' : 'Search could not be completed.'));
      setData(payload); setFilters(payload.filters ?? filters); setShowSeen(false); setShowDismissed(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : (sv ? 'Sökningen kunde inte genomföras.' : 'Search could not be completed.'));
    } finally { setLoading(false); }
  }

  async function dismiss(result: SearchResult) {
    setDecisionBusy(result.identityKey); setError('');
    try {
      const response = await fetch('/api/search/dismiss', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ identityKey: result.identityKey, title: result.title, company: result.company, url: result.url }) });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload?.error || (sv ? 'Jobbet kunde inte döljas.' : 'The role could not be dismissed.'));
      setData((current) => current ? {
        ...current,
        results: current.results.filter((item) => item.identityKey !== result.identityKey),
        dismissedResults: [...current.dismissedResults.filter((item) => item.identityKey !== result.identityKey), result],
        counts: { ...current.counts, visible: Math.max(0, current.counts.visible - 1), dismissed: current.counts.dismissed + 1 },
      } : current);
    } catch (err) { setError(err instanceof Error ? err.message : String(err)); }
    finally { setDecisionBusy(''); }
  }

  async function restore(result: SearchResult) {
    setDecisionBusy(result.identityKey); setError('');
    try {
      const response = await fetch('/api/search/dismiss', { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ identityKey: result.identityKey }) });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload?.error || (sv ? 'Jobbet kunde inte återställas.' : 'The role could not be restored.'));
      setData((current) => current ? {
        ...current,
        results: [...current.results, result].sort((a, b) => b.score - a.score),
        dismissedResults: current.dismissedResults.filter((item) => item.identityKey !== result.identityKey),
        counts: { ...current.counts, visible: current.counts.visible + 1, dismissed: Math.max(0, current.counts.dismissed - 1) },
      } : current);
    } catch (err) { setError(err instanceof Error ? err.message : String(err)); }
    finally { setDecisionBusy(''); }
  }

  const primary = data?.results.filter((result) => result.novelty !== 'SEEN') ?? [];
  const visible = data ? (showSeen ? data.results : primary) : [];
  const jobTypeOptions: Array<[JobType, string]> = [
    ['permanent', sv ? 'Tillsvidare' : 'Permanent'], ['temporary', sv ? 'Visstid / vikariat' : 'Temporary'],
    ['fulltime', sv ? 'Heltid' : 'Full-time'], ['parttime', sv ? 'Deltid' : 'Part-time'], ['consulting', sv ? 'Konsult / uppdrag' : 'Consulting'],
  ];
  const workModeOptions: Array<[WorkMode, string]> = [['onsite', sv ? 'På plats' : 'On-site'], ['hybrid', 'Hybrid'], ['remote', sv ? 'Distans' : 'Remote']];

  return (
    <div className="search-runner">
      <form className="search-controls search-controls--workspace" onSubmit={runSearch}>
        <div className="search-filter-block">
          <span className="meta-label">{sv ? 'Anställningsform / omfattning' : 'Job type / scope'}</span>
          <div className="filter-chip-row">{jobTypeOptions.map(([value, label]) => <label className={`filter-chip ${filters.jobTypes.includes(value) ? 'filter-chip--active' : ''}`} key={value}><input type="checkbox" checked={filters.jobTypes.includes(value)} onChange={() => setFilters((current) => ({ ...current, jobTypes: toggleValue(current.jobTypes, value) }))} />{label}</label>)}</div>
        </div>
        <div className="search-filter-block">
          <span className="meta-label">{sv ? 'Arbetsplats' : 'Work mode'}</span>
          <div className="filter-chip-row">{workModeOptions.map(([value, label]) => <label className={`filter-chip ${filters.workModes.includes(value) ? 'filter-chip--active' : ''}`} key={value}><input type="checkbox" checked={filters.workModes.includes(value)} onChange={() => setFilters((current) => ({ ...current, workModes: toggleValue(current.workModes, value) }))} />{label}</label>)}</div>
        </div>
        <div className="search-filter-block">
          <span className="meta-label">{sv ? 'Publicerad' : 'Published'}</span>
          <div className="filter-chip-row">{[[7, sv ? 'Senaste veckan' : 'Last week'], [30, sv ? 'Senaste månaden' : 'Last month'], [60, sv ? '2 månader' : '2 months'], [90, sv ? '3 månader' : '3 months']].map(([days, label]) => <button className={`filter-chip ${filters.publishedPresetDays === days ? 'filter-chip--active' : ''}`} type="button" key={String(days)} onClick={() => setFilters((current) => ({ ...current, publishedPresetDays: current.publishedPresetDays === days ? null : Number(days), publishedFrom: '', publishedTo: '' }))}>{label}</button>)}</div>
          <div className="date-filter-row"><label><span>{sv ? 'Från' : 'From'}</span><input type="date" value={filters.publishedFrom} onChange={(event) => setFilters((current) => ({ ...current, publishedPresetDays: null, publishedFrom: event.target.value }))} /></label><label><span>{sv ? 'Till' : 'To'}</span><input type="date" value={filters.publishedTo} onChange={(event) => setFilters((current) => ({ ...current, publishedPresetDays: null, publishedTo: event.target.value }))} /></label></div>
        </div>
        <div className="search-filter-block">
          <span className="meta-label">{sv ? 'Sista ansökningsdag' : 'Application deadline'}</span>
          <div className="date-filter-row"><label><span>{sv ? 'Från' : 'From'}</span><input type="date" value={filters.deadlineFrom} onChange={(event) => setFilters((current) => ({ ...current, deadlineFrom: event.target.value }))} /></label><label><span>{sv ? 'Till' : 'To'}</span><input type="date" value={filters.deadlineTo} onChange={(event) => setFilters((current) => ({ ...current, deadlineTo: event.target.value }))} /></label></div>
          <p className="muted">{sv ? 'Om du inte anger ett slutdatum begränsar CareerHub automatiskt orimligt långt framflyttade sista ansökningsdagar.' : 'If you leave the end date blank, CareerHub automatically excludes implausibly far-future deadlines.'}</p>
        </div>
        <label className="search-overlay"><span className="meta-label">{sv ? 'Specifika önskemål för denna sökning' : 'Specific wishes for this search'}</span><input value={overlay} onChange={(event) => setOverlay(event.target.value)} placeholder={sv ? 'Valfritt – påverkar bara den här körningen' : 'Optional — affects this run only'} /></label>
        <div className="inline-actions"><button className="button button--primary" type="submit" disabled={loading}>{loading ? (sv ? 'Söker…' : 'Searching…') : (sv ? 'Sök jobb' : 'Search jobs')}</button><button className="button" type="button" onClick={() => setFilters(EMPTY_FILTERS)}>{sv ? 'Rensa filter' : 'Clear filters'}</button></div>
      </form>
      {loading ? <div className="process-status"><span className="process-status__dot process-status__dot--active" /><div><strong>{sv ? 'Sökning pågår' : 'Search running'}</strong><p>{sv ? 'CareerHub söker i de valda filtren och din sparade sökprofil.' : 'CareerHub is searching with these filters and your saved Search Profile.'}</p></div></div> : null}
      <p className="muted search-note">{sv ? 'Filtren ovan sparas som din senaste sökyta, men ändrar inte din verifierade profil eller din sparade Search Profile.' : 'These filters persist as your latest Search workspace, but do not change your verified profile or saved Search Profile.'}</p>
      {error ? <p className="wish-status wish-status--error" role="alert">{error}</p> : null}

      {data ? <section className="search-results" aria-live="polite">
        <div className="search-results__head"><div><p className="meta-label">{data.sourceHealth === 'HEALTHY' ? (sv ? 'Sökning klar' : 'Search completed') : (sv ? 'Sökning klar med källvarning' : 'Search completed with source warning')}</p><h2>{data.counts.new} {sv ? 'nya' : 'new'} · {data.counts.changed} {sv ? 'ändrade' : 'changed'}</h2></div><span className={`status source-health source-health--${data.sourceHealth.toLowerCase()}`}>{data.sourceHealth}</span></div>

        <div className="search-summary-grid">
          <span><strong>{data.counts.checked}</strong><small>{sv ? 'kontrollerade' : 'checked'}</small></span>
          <span><strong>{data.counts.matched}</strong><small>{sv ? 'matchar filter' : 'match filters'}</small></span>
          <span><strong>{data.counts.new}</strong><small>{sv ? 'nya' : 'new'}</small></span>
          <span><strong>{data.counts.changed}</strong><small>{sv ? 'ändrade' : 'changed'}</small></span>
          <span><strong>{data.counts.dismissed}</strong><small>{sv ? 'dolda' : 'dismissed'}</small></span>
        </div>

        <div className="search-run-meta"><span><strong>{sv ? 'Nu' : 'Current'}:</strong> {new Date(data.currentSearchAt).toLocaleString()}</span><span><strong>{sv ? 'Föregående lyckade' : 'Previous successful'}:</strong> {data.previousSuccessfulSearchAt ? new Date(data.previousSuccessfulSearchAt).toLocaleString() : (sv ? 'ingen registrerad' : 'none recorded')}</span><span><strong>{sv ? 'Källa' : 'Source'}:</strong> {data.sourceCoverage.join(', ')}</span><span><strong>{sv ? 'Sökfrågor' : 'Queries'}:</strong> {data.searchedQueries}</span></div>

        {!data.historyAvailable ? <div className="notice notice--warning">{sv ? 'Sökningen fungerade, men historik och permanenta döljningar är inte anslutna i denna deployment.' : 'The search worked, but history and persistent dismissals are not connected in this deployment.'}</div> : null}
        {data.baselineEstablished ? <div className="notice">{sv ? 'Detta är den första registrerade körningen för dessa sökval. Resultaten etablerar baslinjen.' : 'This is the first recorded run for these search choices. These results establish the baseline.'}</div> : null}
        {data.historyAvailable && !data.baselineEstablished && data.counts.new === 0 && data.counts.changed === 0 ? <div className="notice">{sv ? `Sökningen genomfördes korrekt. ${data.counts.checked} jobb kontrollerades, men inga nya eller ändrade jobb hittades.` : `Search completed successfully. ${data.counts.checked} roles were checked, but no new or changed roles were found.`}</div> : null}

        <div className="inline-actions">{data.counts.seen > 0 ? <button type="button" className="button" onClick={() => setShowSeen((value) => !value)}>{showSeen ? (sv ? 'Dölj redan sedda' : 'Hide seen') : (sv ? `Visa ${data.counts.seen} redan sedda` : `Show ${data.counts.seen} seen`)}</button> : null}{data.dismissedResults.length > 0 ? <button type="button" className="button" onClick={() => setShowDismissed((value) => !value)}>{showDismissed ? (sv ? 'Dölj bortvalda' : 'Hide dismissed') : (sv ? `Visa ${data.dismissedResults.length} bortvalda` : `Show ${data.dismissedResults.length} dismissed`)}</button> : null}</div>

        {visible.length ? <div className="search-result-list">{visible.map((result) => <article className="search-result" key={`${result.id}-${result.laneId}`}>
          <div className="search-result__main"><p className="meta-label"><span className={`novelty novelty--${result.novelty.toLowerCase()}`}>{result.novelty}</span> · {result.laneName} · {sv ? 'poäng' : 'score'} {result.score}</p><h3>{result.title}</h3><p><strong>{result.company || (sv ? 'Arbetsgivare ej angiven' : 'Employer not stated')}</strong>{result.location ? ` · ${result.location}` : ''}</p><p className="muted">{result.jobType} · {result.workMode}{result.published ? ` · ${sv ? 'publicerad' : 'published'} ${result.published.slice(0, 10)}` : ''}{result.deadline ? ` · ${sv ? 'sista dag' : 'deadline'} ${result.deadline.slice(0, 10)}` : ''}</p></div>
          <div className="inline-actions"><button type="button" className="button button--quiet" disabled={decisionBusy === result.identityKey || !data.historyAvailable} onClick={() => dismiss(result)} aria-label={sv ? `Dölj ${result.title}` : `Dismiss ${result.title}`}>×</button><a className="button" href={result.url} target="_blank" rel="noreferrer">{sv ? 'Öppna jobbet' : 'Open role'}</a><a className="button button--primary" href={analyseHref(result)}>{sv ? 'Analysera jobbet' : 'Analyse job'}</a></div>
        </article>)}</div> : <div className="empty-state">{data.historyAvailable ? (sv ? 'Inga nya eller ändrade möjligheter i denna körning.' : 'No new or changed opportunities in this run.') : (sv ? 'Inga matchande möjligheter hittades.' : 'No matching opportunities were returned.')}</div>}

        {showDismissed && data.dismissedResults.length ? <div className="dismissed-results"><h3>{sv ? 'Bortvalda jobb' : 'Dismissed roles'}</h3>{data.dismissedResults.map((result) => <article className="search-result search-result--dismissed" key={`dismissed-${result.identityKey}`}><div className="search-result__main"><h3>{result.title}</h3><p>{result.company}{result.location ? ` · ${result.location}` : ''}</p></div><div className="inline-actions"><button className="button" type="button" disabled={decisionBusy === result.identityKey} onClick={() => restore(result)}>{sv ? 'Återställ' : 'Restore'}</button></div></article>)}</div> : null}
      </section> : null}
    </div>
  );
}
