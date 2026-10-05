import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadApplications } from '@/lib/data';

export default function TrackPage() {
  const applications = loadApplications()?.applications ?? [];
  const states = ['saved', 'applied', 'contact', 'interview', 'decision'];
  return (
    <main className="workspace">
      <WorkspaceHeader current="track" title="Track" intro="Follow applications, contacts, interviews, decisions and the next action without losing the role context." />
      <section className="panel-grid">
        {states.map((state) => { const items = applications.filter((item: any) => String(item.status ?? '').toLowerCase() === state); return <article className="panel panel--third" key={state}><p className="meta-label">{state}</p><p className="stat">{items.length}</p></article>; })}
        <article className="panel panel--full"><h2>Current pipeline</h2>{applications.length ? <div className="section-stack">{applications.map((item: any, index: number) => <div className="row" key={item.id ?? index}><strong>{item.role ?? item.title ?? `Application ${index + 1}`}</strong><span className="status">{item.status ?? 'unknown'}</span></div>)}</div> : <div className="empty-state">The pipeline is empty. Once applications are generated or registered, their state will appear here.</div>}</article>
      </section>
    </main>
  );
}
