'use client';

import { FormEvent, useState } from 'react';

type Novelty = 'NEW' | 'SEEN' | 'CHANGED' | 'UNKNOWN';
type SearchResult = {
  id: string; title: string; company: string; location: string; published: string; deadline: string; url: string;
  matchedQuery: string; laneId: string; laneName: string; laneBucket: string; score: number; novelty: Novelty;
};
type SearchResponse = {
  runId: string; currentSearchAt: string; previousSuccessfulSearchAt: string | null; baselineEstablished: boolean; historyAvailable: boolean; persisted: boolean;
  results: SearchResult[]; counts: { new: number; seen: number; changed: number; unknown: number; removed: number };
  searchedQueries: number; source: string; sourceHealth: string; sourceCoverage: string[]; lane: string; overlayUsed: boolean; partialSourceFailure: boolean;
};

function analyseHref(result: SearchResult) {
  const params = new URLSearchParams({ job_url: result.url, title: result.title, company: result.company, deadline: (result.deadline ?? '').slice(0, 10), lane: ['core', 'adjacent', 'bridge'].includes(result.laneBucket) ? result.laneBucket : 'core' });
  return `/analyse?${params.toString()}`;
}

export default function SearchRunner({ language = 'en' }: { language?: string }) {
  const sv = language.toLowerCase().startsWith('sv');
  const [overlay, setOverlay] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState<SearchResponse | null>(null);
  const [showSeen, setShowSeen] = useState(false);

  async function runSearch(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError('');
    try {
      const response = await fetch('/api/search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lane: 'all', overlay: overlay.trim(), limit: 60 }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload?.error || (sv ? 'Sökningen kunde inte genomföras.' : 'Search could not be completed.'));
      setData(payload); setShowSeen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : (sv ? 'Sökningen kunde inte genomföras.' : 'Search could not be completed.'));
    } finally { setLoading(false); }
  }

  const primary = data?.results.filter((result) => result.novelty !== 'SEEN') ?? [];
  const visible = data ? (showSeen ? data.results : primary) : [];

  return (
    <div className="search-runner">
      <form className="search-controls" onSubmit={runSearch}>
        <label className="search-overlay"><span className="meta-label">{sv ? 'Specifika önskemål eller behov' : 'Specific wishes or needs'}</span><input value={overlay} onChange={(event) => setOverlay(event.target.value)} placeholder={sv ? 'Valfritt – skriv vad just den här sökningen ska ta hänsyn till' : 'Optional — add what this search should take into account'} /></label>
        <button className="button button--primary" type="submit" disabled={loading}>{loading ? (sv ? 'Söker…' : 'Searching…') : (sv ? 'Sök jobb' : 'Run search')}</button>
      </form>
      {loading ? <div className="process-status"><span className="process-status__dot process-status__dot--active" /><div><strong>{sv ? 'Sökning pågår' : 'Search running'}</strong><p>{sv ? 'CareerHub kör den aktiva sökplanen.' : 'CareerHub is executing the active query plan.'}</p></div></div> : null}
      <p className="muted search-note">{sv ? 'Din verifierade karriärprofil är basen. Texten ovan är ett extra raster för just denna sökning och blir aldrig kandidatfakta.' : 'Your verified career profile is the baseline. The field above is an extra raster for this search and never becomes candidate evidence.'}</p>
      {error ? <p className="wish-status wish-status--error" role="alert">{error}</p> : null}

      {data ? <section className="search-results" aria-live="polite">
        <div className="search-results__head">
          <div>
            <p className="meta-label">{data.sourceHealth === 'HEALTHY' ? (sv ? 'Sökning klar' : 'Search completed') : (sv ? 'Sökning klar med källvarning' : 'Search completed with source warning')}</p>
            <h2>{data.historyAvailable ? `${data.counts.new} ${sv ? 'nya' : 'new'} · ${data.counts.changed} ${sv ? 'ändrade' : 'changed'}` : `${data.results.length} ${sv ? 'träffar' : 'results'}`}</h2>
          </div>
          <span className={`status source-health source-health--${data.sourceHealth.toLowerCase()}`}>{data.sourceHealth}</span>
        </div>

        <div className="search-run-meta">
          <span><strong>{sv ? 'Nu' : 'Current'}:</strong> {new Date(data.currentSearchAt).toLocaleString()}</span>
          <span><strong>{sv ? 'Föregående lyckade' : 'Previous successful'}:</strong> {data.previousSuccessfulSearchAt ? new Date(data.previousSuccessfulSearchAt).toLocaleString() : (sv ? 'ingen registrerad' : 'none recorded')}</span>
          <span><strong>{sv ? 'Källa' : 'Source'}:</strong> {data.sourceCoverage.join(', ')}</span>
          <span><strong>{sv ? 'Sökfrågor' : 'Queries'}:</strong> {data.searchedQueries}</span>
          <span><strong>{sv ? 'Totalt' : 'Total'}:</strong> {data.results.length}</span>
          {data.historyAvailable ? <span><strong>{sv ? 'Sedda' : 'Seen'}:</strong> {data.counts.seen}</span> : null}
        </div>

        {!data.historyAvailable ? <div className="notice notice--warning">{sv ? 'Sökningen fungerade, men körhistorik är inte ansluten i denna deployment. CareerHub markerar därför inte träffar som nya eller tidigare sedda.' : 'The search worked, but run-history storage is not connected in this deployment. CareerHub therefore does not label results as new or previously seen.'}</div> : null}
        {data.historyAvailable && !data.baselineEstablished && data.counts.new === 0 && data.counts.changed === 0 ? <div className="notice">{sv ? 'Sökningen genomfördes korrekt. Inga nya jobb hittades sedan föregående lyckade sökning.' : 'Search completed successfully. No new roles were found since the previous successful search.'}</div> : null}
        {data.baselineEstablished ? <div className="notice">{sv ? 'Detta är den första registrerade körningen för denna sökplan. Resultaten etablerar baslinjen.' : 'This is the first recorded run for this search plan. These results establish the baseline.'}</div> : null}

        {data.counts.seen > 0 ? <div className="inline-actions"><button type="button" className="button" onClick={() => setShowSeen((value) => !value)}>{showSeen ? (sv ? 'Dölj redan sedda' : 'Hide seen') : (sv ? `Visa ${data.counts.seen} redan sedda` : `Show ${data.counts.seen} seen`)}</button></div> : null}

        {visible.length ? <div className="search-result-list">{visible.map((result) => <article className="search-result" key={`${result.id}-${result.laneId}`}>
          <div className="search-result__main">
            <p className="meta-label"><span className={`novelty novelty--${result.novelty.toLowerCase()}`}>{result.novelty}</span> · {result.laneName} · {sv ? 'poäng' : 'score'} {result.score}</p>
            <h3>{result.title}</h3>
            <p><strong>{result.company || (sv ? 'Arbetsgivare ej angiven' : 'Employer not stated')}</strong>{result.location ? ` · ${result.location}` : ''}</p>
            <p className="muted">{sv ? 'Träff' : 'Matched'}: {result.matchedQuery}{result.deadline ? ` · ${sv ? 'sista dag' : 'deadline'} ${result.deadline.slice(0, 10)}` : ''}</p>
          </div>
          <div className="inline-actions"><a className="button" href={result.url} target="_blank" rel="noreferrer">{sv ? 'Öppna jobbet' : 'Open role'}</a><a className="button button--primary" href={analyseHref(result)}>{sv ? 'Analysera i CareerHub' : 'Analyse in CareerHub'}</a></div>
        </article>)}</div> : <div className="empty-state">{data.historyAvailable ? (sv ? 'Inga nya eller ändrade möjligheter i denna körning.' : 'No new or changed opportunities in this run.') : (sv ? 'Inga matchande möjligheter hittades.' : 'No matching opportunities were returned.')}</div>}
      </section> : null}
    </div>
  );
}
