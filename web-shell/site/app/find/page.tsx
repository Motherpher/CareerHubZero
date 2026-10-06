import SearchRunner from '@/app/find/SearchRunner';
import SearchProfileEditor from '@/app/find/SearchProfileEditor';
import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadSearchProfile } from '@/lib/data';

export default function SearchPage() {
  const search = loadSearchProfile();
  const lanes = search?.lanes ?? [];
  const anchors = search?.geographies?.anchors ?? [];
  const engagement = search?.engagement_types ?? [];
  const savedNeed = search?.user_search_overlay?.specific_wishes_or_needs ?? '';

  return (
    <main className="workspace">
      <WorkspaceHeader current="find" title="Search" intro="Choose whether you are running one search or changing what CareerHub should look for in future searches." />
      <section className="panel-grid">
        <article className="panel panel--full">
          <div className="explainer">
            <strong>Two different kinds of change live here.</strong>
            <ol>
              <li><strong>Run one search:</strong> choose a lane and optionally add a temporary need. Nothing is saved.</li>
              <li><strong>Change future searches:</strong> edit the Search Profile below, including geography, work type and role lanes, then save the defaults.</li>
            </ol>
          </div>
        </article>
        <article className="panel panel--full"><p className="meta-label">Saved search profile</p><h2>{anchors.join(' + ') || 'No geographic anchors configured'}</h2><div className="tag-row">{search?.geographies?.remote_allowed ? <span className="tag">Remote allowed</span> : null}{engagement.map((item: string) => <span className="tag" key={item}>{item.replaceAll('_', ' ')}</span>)}</div></article>
        <article className="panel panel--full"><p className="meta-label">1 · Run one search</p><h2>Search with the current defaults</h2><p className="muted">Choose all lanes or one lane. “This-search need” is temporary and disappears after this run.</p><SearchRunner lanes={lanes} /></article>
        <article className="panel panel--full" id="edit-search-profile"><p className="meta-label">2 · Change future searches</p><h2>Edit the saved Search Profile</h2><p className="muted">These settings persist. You can also rename role lanes and change the terms CareerHub searches for inside each lane.</p><SearchProfileEditor anchors={anchors} remoteAllowed={Boolean(search?.geographies?.remote_allowed)} engagementTypes={engagement} savedNeed={savedNeed} lanes={lanes} /></article>
        <article className="panel panel--full"><h2>Current role lanes at a glance</h2><div className="section-stack">{lanes.map((lane: any) => <div className="row" key={lane.lane_id}><div><strong>{lane.name}</strong><div className="muted">{(lane.queries ?? []).slice(0, 6).join(' · ')}{(lane.queries ?? []).length > 6 ? ' …' : ''}</div></div><span className="status">P{lane.priority} · {lane.bucket}</span></div>)}</div><div className="inline-actions"><a className="button" href="#edit-search-profile">Change role lanes</a><a className="button" href="/help">Explain role lanes</a></div></article>
        <article className="panel"><h2>Geographical widening</h2><p className="muted">CareerHub widens the search progressively when the anchor area is too narrow.</p><ol>{(search?.geographies?.progressive_widening ?? []).map((item: string) => <li key={item}>{item.replaceAll('_', ' ')}</li>)}</ol></article>
        <article className="panel"><h2>One-search overrides</h2><p className="muted">Lane and need changes in the runner affect only that search. They do not rewrite your defaults or your Career Profile.</p><div className="inline-actions"><a className="button" href="/wish">Suggest a search improvement</a></div></article>
      </section>
    </main>
  );
}
