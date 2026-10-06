import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import ProfileActions from './ProfileActions';
import { loadCandidateProfile, loadSearchProfile } from '@/lib/data';

export default function ProfilePage() {
  const profile = loadCandidateProfile();
  const search = loadSearchProfile();
  const evidence = Array.isArray(profile?.evidence) ? profile.evidence : [];
  const sources = Array.isArray(profile?.career_sources) ? profile.career_sources : [];
  const core = profile?.positioning?.functional_core ?? [];
  const queue = profile?.verification_queue ?? [];

  return (
    <main className="workspace">
      <WorkspaceHeader current="profile" title="Current profile" intro="This is the evidence-governed profile CareerHub is currently allowed to use for matching, analysis and applications." />
      <section className="panel-grid">
        <article className="panel panel--full">
          <div className="explainer">
            <strong>How do I change this profile?</strong>
            <ol>
              <li><strong>Change the evidence:</strong> add, replace, activate or deactivate the relevant source in Library.</li>
              <li><strong>Ask CareerHub to review it:</strong> request evidence review, or rebuild the profile from the active sources.</li>
              <li><strong>Use the reviewed result:</strong> CareerHub only strengthens or changes candidate claims when the source base supports them.</li>
            </ol>
            <div className="inline-actions"><a className="button button--primary" href="/library">Change profile evidence</a><a className="button" href="/help">Read profile Q&amp;A</a></div>
          </div>
        </article>
        <article className="panel panel--full"><p className="meta-label">Professional positioning</p><h2>{profile?.positioning?.headline ?? 'No active positioning yet'}</h2><div className="tag-row">{core.map((item: string) => <span className="tag" key={item}>{item}</span>)}</div></article>
        <article className="panel panel--third"><p className="meta-label">Verified evidence</p><p className="stat">{evidence.length}</p><p className="muted">claims currently available for matching and application work.</p></article>
        <article className="panel panel--third"><p className="meta-label">Career sources</p><p className="stat">{sources.length}</p><p className="muted">governed sources behind the active profile.</p></article>
        <article className="panel panel--third"><p className="meta-label">Open verification</p><p className="stat">{queue.filter((item: any) => item.status === 'open').length}</p><p className="muted">questions that constrain stronger claims until resolved.</p></article>
        <article className="panel panel--full"><h2>Evidence map</h2><p className="muted">These are the candidate claims CareerHub can currently trace to the governed profile evidence.</p><div className="section-stack">{evidence.length ? evidence.map((item: any) => <div className="row" key={item.id}><strong>{item.claim}</strong><span className="status">{item.status}</span></div>) : <div className="empty-state">No verified evidence is active yet. Add source documents before matching or application work.</div>}</div></article>
        <article className="panel"><h2>Search defaults attached to this profile</h2><p className="muted">Search settings tell CareerHub what to look for; they do not change your career evidence.</p><dl className="definition-list"><dt>Anchors</dt><dd>{(search?.geographies?.anchors ?? []).join(', ') || 'Not set'}</dd><dt>Remote</dt><dd>{search?.geographies?.remote_allowed ? 'Allowed' : 'Off'}</dd><dt>Role lanes</dt><dd>{(search?.lanes ?? []).length}</dd></dl><div className="inline-actions"><a className="button button--primary" href="/find#edit-search-profile">Change search setup</a></div></article>
        <article className="panel panel--wide"><h2>Profile actions and verification</h2><p className="muted">Use these controls after you have added or changed evidence. A request does not silently create a new claim; it starts the governed review path.</p><ProfileActions queue={queue} /></article>
      </section>
    </main>
  );
}
