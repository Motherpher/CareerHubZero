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
      <WorkspaceHeader current="find" title="Search" intro="Run the saved Search Profile, make session-only changes for one search, or update the defaults used by future searches." />
      <section className="panel-grid">
        <article className="panel panel--full"><p className="meta-label">Saved search profile</p><h2>{anchors.join(' + ') || 'No geographic anchors configured'}</h2><div className="tag-row">{search?.geographies?.remote_allowed ? <span className="tag">Remote allowed</span> : null}{engagement.map((item: string) => <span className="tag" key={item}>{item}</span>)}</div></article>
        <article className="panel panel--full"><p className="meta-label">Activate search</p><h2>Run the saved profile now</h2><SearchRunner lanes={lanes} /></article>
        <article className="panel panel--full"><h2>Edit saved Search Profile</h2><SearchProfileEditor anchors={anchors} remoteAllowed={Boolean(search?.geographies?.remote_allowed)} engagementTypes={engagement} savedNeed={savedNeed} /></article>
        <article className="panel panel--full"><h2>Role lanes</h2><div className="section-stack">{lanes.map((lane: any) => <div className="row" key={lane.lane_id}><strong>{lane.name}</strong><span className="status">P{lane.priority} · {lane.bucket}</span></div>)}</div></article>
        <article className="panel"><h2>Geographical widening</h2><ol>{(search?.geographies?.progressive_widening ?? []).map((item: string) => <li key={item}>{item.replaceAll('_', ' ')}</li>)}</ol></article>
        <article className="panel"><h2>This-search overrides</h2><p className="muted">Lane and need changes in the runner apply only to the current search. Use the saved-profile editor when the preference should persist.</p><div className="inline-actions"><a className="button" href="/wish">Suggest a search improvement</a></div></article>
      </section>
    </main>
  );
}
