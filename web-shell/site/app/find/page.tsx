import SearchRunner from '@/app/find/SearchRunner';
import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadSearchProfile } from '@/lib/data';

export default function SearchPage() {
  const search = loadSearchProfile();
  const lanes = search?.lanes ?? [];
  const anchors = search?.geographies?.anchors ?? [];
  const engagement = search?.engagement_types ?? [];

  return (
    <main className="workspace">
      <WorkspaceHeader current="find" title="Search" intro="Start from your saved Search Profile, activate a search, and narrow this run without rewriting your defaults." />
      <section className="panel-grid">
        <article className="panel panel--full"><p className="meta-label">Saved search profile</p><h2>{anchors.join(' + ') || 'No geographic anchors configured'}</h2><div className="tag-row">{search?.geographies?.remote_allowed ? <span className="tag">Remote allowed</span> : null}{engagement.map((item: string) => <span className="tag" key={item}>{item}</span>)}</div></article>
        <article className="panel panel--full"><p className="meta-label">Activate search</p><h2>Run the saved profile now</h2><SearchRunner lanes={lanes} /></article>
        <article className="panel panel--full"><h2>Role lanes</h2><div className="section-stack">{lanes.map((lane: any) => <div className="row" key={lane.lane_id}><strong>{lane.name}</strong><span className="status">P{lane.priority} · {lane.bucket}</span></div>)}</div></article>
        <article className="panel"><h2>Geographical widening</h2><ol>{(search?.geographies?.progressive_widening ?? []).map((item: string) => <li key={item}>{item.replaceAll('_', ' ')}</li>)}</ol></article>
        <article className="panel"><h2>This-search overrides</h2><p className="muted">Lane and need changes in the runner apply only to this search session. Saved defaults remain unchanged.</p><div className="inline-actions"><a className="button" href="/wish">Suggest a search improvement</a></div></article>
      </section>
    </main>
  );
}
