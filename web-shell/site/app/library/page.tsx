import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import LibraryClient from './LibraryClient';
import { careerSourceCount } from '@/lib/data';

export default function LibraryPage() {
  const governedSources = careerSourceCount();
  return (
    <main className="workspace">
      <WorkspaceHeader current="library" title="Library" intro="Manage the documents CareerHub is allowed to use. Uploaded material becomes a source only when it is active; source ingestion never silently rewrites the active profile." />
      <section className="panel-grid">
        <article className="panel panel--third"><p className="meta-label">Governed profile sources</p><p className="stat">{governedSources}</p><p className="muted">verified sources already represented in the active profile.</p></article>
        <article className="panel panel--wide"><h2>Source rules</h2><ul><li>ACTIVE sources are available for extraction, profile rebuilds and evidence checks.</li><li>INACTIVE sources remain in your private library but are excluded from active use.</li><li>Extracted evidence should be reviewed before it changes the current profile.</li></ul></article>
        <article className="panel panel--full"><h2>My uploaded documents</h2><LibraryClient /></article>
      </section>
    </main>
  );
}
