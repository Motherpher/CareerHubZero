'use client';

import { FormEvent, useState } from 'react';

type Lane = { lane_id: string; name: string; bucket: string; priority: number };
type SearchResult = {
  id: string;
  title: string;
  company: string;
  location: string;
  published: string;
  deadline: string;
  url: string;
  matchedQuery: string;
  laneId: string;
  laneName: string;
  laneBucket: string;
  score: number;
};

type SearchResponse = {
  results: SearchResult[];
  searchedQueries: number;
  source: string;
  lane: string;
  overlayUsed: boolean;
};

function analyseHref(result: SearchResult) {
  const params = new URLSearchParams({
    job_url: result.url,
    title: result.title,
    company: result.company,
    deadline: (result.deadline ?? '').slice(0, 10),
    lane: ['core', 'adjacent', 'bridge'].includes(result.laneBucket) ? result.laneBucket : 'core',
  });
  return `/analyse?${params.toString()}`;
}

export default function SearchRunner({ lanes, language = 'en' }: { lanes: Lane[]; language?: string }) {
  const sv = language.toLowerCase().startsWith('sv');
  const [lane, setLane] = useState('all');
  const [overlay, setOverlay] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState<SearchResponse | null>(null);

  async function runSearch(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lane, overlay: overlay.trim(), limit: 60 }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload?.error || (sv ? 'Sökningen kunde inte genomföras.' : 'Search could not be completed.'));
      setData(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : (sv ? 'Sökningen kunde inte genomföras.' : 'Search could not be completed.'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="search-runner">
      <form className="search-controls" onSubmit={runSearch}>
        <label>
          <span className="meta-label">{sv ? 'Sökspår' : 'Search lane'}</span>
          <select value={lane} onChange={(event) => setLane(event.target.value)}>
            <option value="all">{sv ? 'Alla sparade spår' : 'All saved lanes'}</option>
            {lanes.map((item) => <option key={item.lane_id} value={item.lane_id}>{item.name}</option>)}
          </select>
        </label>
        <label className="search-overlay">
          <span className="meta-label">{sv ? 'Specifika önskemål eller behov' : 'Specific wishes or needs'}</span>
          <input
            value={overlay}
            onChange={(event) => setOverlay(event.target.value)}
            placeholder={sv ? 'Valfritt – skriv vad just den här sökningen ska ta hänsyn till' : 'Optional — add what this search should take into account'}
          />
        </label>
        <button className="button button--primary" type="submit" disabled={loading}>
          {loading ? (sv ? 'Söker…' : 'Searching…') : (sv ? 'Sök jobb' : 'Run search')}
        </button>
      </form>

      <p className="muted search-note">
        {sv
          ? 'Din verifierade karriärprofil är basen. Texten i rutan ovan är ett sökraster för just denna sökning och blir aldrig kandidatfakta.'
          : 'Your verified career profile is the baseline. The field above is a search-only raster for this run and never becomes candidate evidence.'}
      </p>
      {error ? <p className="wish-status wish-status--error" role="alert">{error}</p> : null}

      {data ? (
        <section className="search-results" aria-live="polite">
          <div className="search-results__head">
            <div>
              <p className="meta-label">{sv ? 'Sökning klar' : 'Search complete'}</p>
              <h2>{data.results.length} {sv ? 'möjligheter' : 'opportunities'}</h2>
            </div>
            <p className="muted">{data.source} · {data.searchedQueries} {sv ? 'sökkörningar' : 'query runs'}</p>
          </div>
          {data.results.length ? (
            <div className="search-result-list">
              {data.results.map((result) => (
                <article className="search-result" key={`${result.id}-${result.laneId}`}>
                  <div className="search-result__main">
                    <p className="meta-label">{result.laneName} · {sv ? 'poäng' : 'score'} {result.score}</p>
                    <h3>{result.title}</h3>
                    <p><strong>{result.company || (sv ? 'Arbetsgivare ej angiven' : 'Employer not stated')}</strong>{result.location ? ` · ${result.location}` : ''}</p>
                    <p className="muted">{sv ? 'Träff' : 'Matched'}: {result.matchedQuery}{result.deadline ? ` · ${sv ? 'sista dag' : 'deadline'} ${result.deadline.slice(0, 10)}` : ''}</p>
                  </div>
                  <div className="inline-actions">
                    <a className="button" href={result.url} target="_blank" rel="noreferrer">{sv ? 'Öppna jobbet' : 'Open role'}</a>
                    <a className="button button--primary" href={analyseHref(result)}>{sv ? 'Analysera i CareerHub' : 'Analyse in CareerHub'}</a>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              {sv ? 'Inga matchande möjligheter hittades i den här sökningen. Justera sökrastret eller sökspåret och försök igen.' : 'No matching opportunities were returned for this run. Adjust the search raster or lane and try again.'}
            </div>
          )}
        </section>
      ) : null}
    </div>
  );
}
