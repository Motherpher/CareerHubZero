import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadApplications } from '@/lib/data';

export default function ApplyPage() {
  const applications = loadApplications()?.applications ?? [];
  return (
    <main className="workspace">
      <WorkspaceHeader current="apply" title="Apply" intro="Prepare and retrieve applications from the active profile and the current HRDM role analysis, with claims bounded by verified evidence." />
      <section className="panel-grid">
        <article className="panel panel--third"><p className="meta-label">Applications</p><p className="stat">{applications.length}</p></article>
        <article className="panel panel--third"><p className="meta-label">Application rule</p><h2>Evidence first</h2><p className="muted">No stronger claim than the profile sources support.</p></article>
        <article className="panel panel--third"><p className="meta-label">Role context</p><h2>HRDM-linked</h2><p className="muted">Positioning comes from the role analysis, not generic cover-letter language.</p></article>
        <article className="panel panel--full"><h2>Application actions</h2><p className="muted">A new application begins with one governed HRDM-R drill. That run produces the analysis and application package together.</p><div className="inline-actions"><a className="button button--primary" href="/analyse">Analyse a role and prepare application</a><a className="button" href="/library">Review active evidence first</a></div></article>
        <article className="panel panel--full"><h2>Application pipeline</h2>{applications.length ? <div className="section-stack">{applications.map((item: any, index: number) => { const paths = item.application_paths ?? {}; const reports = item.hrdm_report_paths ?? {}; return <div className="row row--stack-mobile" key={item.issue_number ?? item.id ?? index}><div><strong>{item.role ?? item.title ?? `Application ${index + 1}`}</strong><div className="muted">{item.company ?? ''}{item.next_action ? ` · Next: ${item.next_action}` : ''}</div></div><div className="inline-actions"><span className="status">{item.status ?? 'draft'}</span>{paths.docx ? <a className="button button--primary" href={`/api/artifact?path=${encodeURIComponent(paths.docx)}`}>Download application</a> : null}{paths.json ? <a className="button" href={`/api/artifact?path=${encodeURIComponent(paths.json)}`}>Application data</a> : null}{reports.markdown ? <a className="button" href={`/api/artifact?path=${encodeURIComponent(reports.markdown)}`}>HRDM report</a> : null}<a className="button" href="/track">Update status</a></div></div>; })}</div> : <div className="empty-state">No applications are stored yet. Use “Analyse a role and prepare application” to create the first governed application case.</div>}</article>
      </section>
    </main>
  );
}
