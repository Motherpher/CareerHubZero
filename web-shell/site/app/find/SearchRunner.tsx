'use client';

import { FormEvent, useState } from 'react';
import ProcessIndicator from '@/app/_components/ProcessIndicator';

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
    lane: ['core','adjacent','bridge'].includes(result.laneBucket) ? result.laneBucket : 'core',
  });
  return `/analyse?${params.toString()}`;
}

export default function SearchRunner({ lanes }: { lanes: Lane[] }) {
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
      if (!response.ok) throw new Error(payload?.error || 'Search could not be completed.');
      setData(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search could not be completed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="search-runner">
      <ProcessIndicator active={loading} label="Searching for opportunities…" detail="CareerHub is checking the selected lane and search terms. Keep this window open until the results appear." />
      <form className="search-controls" onSubmit={runSearch}>
        <label>
          <span className="meta-label">Search lane</span>
          <select value={lane} onChange={(event) => setLane(event.target.value)}>
            <option value="all">All saved lanes</option>
            {lanes.map((item) => <option key={item.lane_id} value={item.lane_id}>{item.name}</option>)}
          </select>
        </label>
        <label className="search-overlay">
          <span className="meta-label">This-search need</span>
          <input value={overlay} onChange={(event) => setOverlay(event.target.value)} placeholder="Optional: e.g. AI, Uppsala, interim, children’s rights" />
        </label>
        <button className="button button--primary" type="submit" disabled={loading}>{loading ? 'Searching…' : 'Run search'}</button>
      </form>

      <p className="muted search-note">Uses the saved Search Profile as the baseline. Lane and need changes here are session-only and do not rewrite your defaults.</p>
      {error ? <p className="wish-status wish-status--error" role="alert">{error}</p> : null}

      {data ? (
        <section className="search-results" aria-live="polite">
          <div className="search-results__head">
            <div><p className="meta-label">Search complete</p><h2>{data.results.length} opportunities</h2></div>
            <p className="muted">{data.source} · {data.searchedQueries} query runs</p>
          </div>
          {data.results.length ? (
            <div className="search-result-list">
              {data.results.map((result) => (
                <article className="search-result" key={`${result.id}-${result.laneId}`}>
                  <div className="search-result__main">
                    <p className="meta-label">{result.laneName} · score {result.score}</p>
                    <h3>{result.title}</h3>
                    <p><strong>{result.company || 'Employer not stated'}</strong>{result.location ? ` · ${result.location}` : ''}</p>
                    <p className="muted">Matched: {result.matchedQuery}{result.deadline ? ` · deadline ${result.deadline.slice(0, 10)}` : ''}</p>
                  </div>
                  <div className="inline-actions">
                    <a className="button" href={result.url} target="_blank" rel="noreferrer">Open role</a>
                    <a className="button button--primary" href={analyseHref(result)}>Analyse in CareerHub</a>
                  </div>
                </article>
              ))}
            </div>
          ) : <div className="empty-state">No matching opportunities were returned for this run. Broaden the lane or remove the session-only need.</div>}
        </section>
      ) : null}
    </div>
  );
}
