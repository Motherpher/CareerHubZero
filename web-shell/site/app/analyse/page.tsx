import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadHrdmLedger, loadJobVault } from '@/lib/data';

export default function AnalysePage() {
  const ledger = loadHrdmLedger();
  const jobs = loadJobVault()?.jobs ?? [];
  const runs = ledger?.runs ?? ledger?.analyses ?? [];
  return (
    <main className="workspace">
      <WorkspaceHeader current="analyse" title="Analyse" intro="Understand what a role actually asks for before deciding how to position the application." />
      <section className="panel-grid">
        <article className="panel panel--third"><p className="meta-label">Saved roles</p><p className="stat">{jobs.length}</p></article>
        <article className="panel panel--third"><p className="meta-label">HRDM analyses</p><p className="stat">{Array.isArray(runs) ? runs.length : 0}</p></article>
        <article className="panel panel--third"><p className="meta-label">Evidence boundary</p><h2>Verified only</h2><p className="muted">Candidate positioning is constrained by the active profile evidence.</p></article>
        <article className="panel panel--full"><h2>Analysis flow</h2><div className="tag-row"><span className="tag">Signals</span><span className="tag">Meaning map</span><span className="tag">Hidden need</span><span className="tag">Field</span><span className="tag">Function</span><span className="tag">Assessment</span><span className="tag">Candidate positioning</span></div><p className="muted">The full HRDM-R motor remains central; this site is the human-facing analysis surface rather than a second copy of the model.</p></article>
        <article className="panel panel--full"><h2>Recent analyses</h2>{Array.isArray(runs) && runs.length ? <div className="section-stack">{runs.map((run: any, index: number) => <div className="row" key={run.id ?? index}><strong>{run.title ?? run.role ?? run.id ?? `Analysis ${index + 1}`}</strong><span className="status">{run.status ?? 'saved'}</span></div>)}</div> : <div className="empty-state">No HRDM analysis has been written to the site ledger yet.</div>}</article>
      </section>
    </main>
  );
}
