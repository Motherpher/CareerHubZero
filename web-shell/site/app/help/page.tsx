import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadHubProfile } from '@/lib/profile';

const QA = [
  ['getting-started','What is CareerHub?','CareerHub is your personal job-search workspace. It keeps your verified career profile, search settings, saved opportunities, analyses, applications and source documents together.'],
  ['profile','What is my Career Profile?','Your Career Profile is the verified baseline CareerHub uses when it evaluates roles and prepares applications. Search wishes do not silently rewrite it.'],
  ['profile','How do I change my profile?','Open Career profile. Add or update evidence in Library, then request a profile review or rebuild. CareerHub should show the request state instead of changing verified facts silently.'],
  ['search','How does Search work?','Search uses your saved search settings plus an optional one-search-only wish. It queries supported job sources, removes duplicates, compares with previous runs and marks new, changed and previously seen roles.'],
  ['search','Why can a search return 0 new jobs?','The search can still have completed correctly. 0 new means CareerHub checked the source but found no roles that were new compared with your previous successful run and current filters.'],
  ['search','How do I change job types?','Open Search and use the job-type selectors in Saved search settings. You can combine more than one type.'],
  ['search','How do date filters work?','Choose whether the time window applies to when a job was published or its application deadline. Use a quick period or custom from/to dates.'],
  ['search','Can I remove a job from my results?','Yes. Use the × on a result card. Dismissed roles stay hidden from later searches for this CareerHub profile unless the dismissal state is reset.'],
  ['analyse','How do I analyse a job opening?','Open a Search result and choose Analyse job opening, or open Analyse and enter a public job URL or paste the job text. CareerHub then runs the analysis in the background.'],
  ['analyse','How long does a job analysis take?','Normally about 2–5 minutes. Complex roles or external service delays can take longer. You can leave the Analyse page; the process continues in the background.'],
  ['analyse','What happens if I change room while an analysis is running?','Nothing is cancelled. The analysis runs independently of the page. A global process bar shows its status and links back to the stable result page.'],
  ['analyse','Where does the finished report appear?','The running process has a stable analysis link. When complete, the same link shows the report and the analysis is also listed under recent analyses.'],
  ['library','What is Library?','Library stores career source documents for this specific CareerHub profile. ACTIVE sources are available to CareerHub analysis and evidence workflows; INACTIVE sources are stored but excluded from active use.'],
  ['library','Does uploading a document change my Career Profile?','No. Uploading a source does not silently rewrite verified profile facts. It makes the source available for review and, when ACTIVE, for governed analysis context.'],
  ['library','What does Reload CareerHub Library do?','It rebuilds the profile-scoped index of ACTIVE uploaded sources. Upload and activate/deactivate actions should also keep the index current automatically.'],
  ['library','Can another CareerHub see my uploaded files?','No. Library paths are scoped by CareerHub profile ID. The normal Library API rejects paths outside the active profile namespace.'],
  ['apply','What is Apply?','Apply contains application packages and next-step material created from analysed roles. Candidate claims remain constrained by the profile evidence boundary.'],
  ['track','What is Track?','Track records application status, priority, events and next actions. Updates are written through the CareerHub operations workflow.'],
  ['status','What does waiting mean?','Waiting means CareerHub accepted the action but the execution runner has not started it yet. It is not the same as failure.'],
  ['status','What does running mean?','Running means the operation has started and is still working. You can continue using other parts of CareerHub.'],
  ['status','What does failed mean?','Failed means the operation started or was submitted but could not finish. CareerHub should keep the reference and show enough information to retry or diagnose it.'],
  ['privacy','What information becomes candidate evidence?','Verified profile evidence and explicitly ACTIVE user-provided career sources may support analysis. Search-only wishes and unrelated private information must not become candidate claims.'],
  ['help','I pressed a button and nothing seems to happen. What should I check?','Look for the global process bar or an inline status message. If neither changes, open Help and search for the page name. A button should always produce a visible state change, success message or actionable error.'],
];

export default async function HelpPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const hub = loadHubProfile();
  const sv = (hub.identity.language ?? 'en').toLowerCase().startsWith('sv');
  const params = await searchParams;
  const q = (params?.q ?? '').trim().toLowerCase();
  const visible = q ? QA.filter(([,question,answer]) => `${question} ${answer}`.toLowerCase().includes(q)) : QA;

  return (
    <main className="workspace">
      <WorkspaceHeader current="help" title={sv ? 'Hjälp & frågor' : 'Help & Q&A'} intro={sv ? 'Sök eller bläddra bland förklaringar för hela CareerHub.' : 'Search or browse explanations for the whole CareerHub workspace.'} />
      <section className="panel-grid">
        <article className="panel panel--full">
          <form action="/help" method="get" className="help-page-search" role="search">
            <label className="field"><span>{sv ? 'Sök i CareerHub-hjälpen' : 'Search CareerHub help'}</span><input name="q" defaultValue={params?.q ?? ''} placeholder={sv ? 'T.ex. analys, sökning, dokument, status…' : 'e.g. analysis, search, documents, status…'} /></label>
            <button className="button button--primary" type="submit">{sv ? 'Sök' : 'Search'}</button>
            {q ? <a className="button" href="/help">{sv ? 'Visa allt' : 'Show all'}</a> : null}
          </form>
        </article>
        <article className="panel panel--full">
          <div className="help-index">
            {['getting-started','profile','search','analyse','library','apply','track','status','privacy','help'].map((section) => <a className="tag" href={`#${section}`} key={section}>{section.replace('-', ' ')}</a>)}
          </div>
        </article>
        <article className="panel panel--full">
          {visible.length ? <div className="section-stack">{visible.map(([section,question,answer], index) => <details className="help-item" id={index === visible.findIndex((item) => item[0] === section) ? section : undefined} key={`${section}-${question}`} open={Boolean(q)}><summary>{question}</summary><p>{answer}</p></details>)}</div> : <div className="empty-state">{sv ? 'Ingen hjälptext matchade sökningen.' : 'No help article matched that search.'}</div>}
        </article>
      </section>
    </main>
  );
}
