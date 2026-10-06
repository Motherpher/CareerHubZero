import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import AnalyseClient from './AnalyseClient';
import { loadHrdmLedger, loadJobVault, loadSearchProfile } from '@/lib/data';
import { loadHubProfile } from '@/lib/profile';

export default function AnalysePage() {
  const ledger = loadHrdmLedger();
  const jobs = loadJobVault()?.jobs ?? [];
  const search = loadSearchProfile();
  const hub = loadHubProfile();
  const language = hub.identity.language ?? 'en';
  const sv = language.toLowerCase().startsWith('sv');
  const lanes = search?.lanes ?? [];
  const rawRuns = ledger?.runs ?? ledger?.analyses ?? [];
  const runs = Array.isArray(rawRuns) ? rawRuns.filter((run: any) => !/WP\d+.*(?:End-to-End|Test Role)/i.test(String(run?.title ?? run?.role ?? ''))) : [];
  return (
    <main className="workspace">
      <WorkspaceHeader current="analyse" title={sv ? 'Analysera jobb' : 'Analyse'} intro={sv ? 'Analysera en jobbannons mot din verifierade karriärprofil och få en rapport för positionering och ansökan.' : 'Analyse a job opening against your verified career profile and get a report for positioning and application decisions.'} />
      <section className="panel-grid">
        <article className="panel panel--third"><p className="meta-label">{sv ? 'Sparade jobb' : 'Saved roles'}</p><p className="stat">{jobs.length}</p></article>
        <article className="panel panel--third"><p className="meta-label">{sv ? 'Jobbanalyser' : 'Job analyses'}</p><p className="stat">{runs.length}</p></article>
        <article className="panel panel--third"><p className="meta-label">{sv ? 'Underlag' : 'Evidence boundary'}</p><h2>{sv ? 'Verifierat + aktiva källor' : 'Verified + active sources'}</h2><p className="muted">{sv ? 'Analysen använder din verifierade profil och aktiva dokument i ditt CareerHub-bibliotek.' : 'Analysis uses your verified profile and active documents in your CareerHub library.'}</p></article>
        <article className="panel panel--full"><h2>{sv ? 'Analysera jobbannons' : 'Analyse job opening'}</h2><AnalyseClient jobs={jobs} lanes={lanes} language={language} /></article>
        <article className="panel panel--full"><h2>{sv ? 'Vad analysen gör' : 'What the analysis does'}</h2><div className="tag-row"><span className="tag">{sv ? 'Signaler' : 'Signals'}</span><span className="tag">{sv ? 'Behov' : 'Needs'}</span><span className="tag">{sv ? 'Rollens logik' : 'Role logic'}</span><span className="tag">{sv ? 'Bedömning' : 'Assessment'}</span><span className="tag">{sv ? 'Matchning' : 'Fit'}</span><span className="tag">{sv ? 'Positionering' : 'Positioning'}</span><span className="tag">{sv ? 'Ansökningsstrategi' : 'Application strategy'}</span></div></article>
        <article className="panel panel--full"><h2>{sv ? 'Senaste analyser' : 'Recent analyses'}</h2>{runs.length ? <div className="section-stack">{runs.map((run: any, index: number) => <div className="row" key={run.id ?? index}><strong>{run.title ?? run.role ?? run.id ?? `${sv ? 'Analys' : 'Analysis'} ${index + 1}`}</strong><span className="status">{run.status ?? 'saved'}</span></div>)}</div> : <div className="empty-state">{sv ? 'Inga sparade jobbanalyser ännu.' : 'No saved job analyses yet.'}</div>}</article>
      </section>
    </main>
  );
}
