import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadApplications } from '@/lib/data';

export default function ApplyPage() {
  const applications = loadApplications()?.applications ?? [];
  return (
    <main className="workspace">
      <WorkspaceHeader current="apply" title="Apply" intro="Build applications from the active profile and the current role analysis, with claims bounded by verified evidence." />
      <section className="panel-grid">
        <article className="panel panel--third"><p className="meta-label">Applications</p><p className="stat">{applications.length}</p></article>
        <article className="panel panel--third"><p className="meta-label">Application rule</p><h2>Evidence first</h2><p className="muted">No stronger claim than the profile sources support.</p></article>
        <article className="panel panel--third"><p className="meta-label">Role context</p><h2>HRDM-linked</h2><p className="muted">Positioning should come from the role analysis, not generic cover-letter language.</p></article>
        <article className="panel panel--full"><h2>Application pipeline</h2>{applications.length ? <div className="section-stack">{applications.map((item: any, index: number) => <div className="row" key={item.id ?? index}><strong>{item.role ?? item.title ?? `Application ${index + 1}`}</strong><span className="status">{item.status ?? 'draft'}</span></div>)}</div> : <div className="empty-state">No applications are currently stored. A role analysis can become an application once the central motor hand-off is connected.</div>}</article>
      </section>
    </main>
  );
}
