import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import TrackClient from './TrackClient';
import { loadApplications } from '@/lib/data';

export default function TrackPage() {
  const applications = loadApplications()?.applications ?? [];
  const states = ['saved', 'preparing', 'ready', 'applied', 'contacted', 'portfolio', 'interview_1', 'offer', 'denied'];
  return (
    <main className="workspace">
      <WorkspaceHeader current="track" title="Track" intro="Follow applications, update their state and priority, and set the next action without losing the role context." />
      <section className="panel-grid">
        {states.map((state) => { const items = applications.filter((item: any) => String(item.status ?? '').toLowerCase() === state); return <article className="panel panel--third" key={state}><p className="meta-label">{state.replaceAll('_',' ')}</p><p className="stat">{items.length}</p></article>; })}
        <article className="panel panel--full"><h2>Current pipeline</h2><TrackClient cases={applications} /></article>
      </section>
    </main>
  );
}
