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
      <WorkspaceHeader current="profile" title="Current profile" intro="This is the profile CareerHub is currently allowed to use. Search and applications start from this evidence base." />
      <section className="panel-grid">
        <article className="panel panel--full"><p className="meta-label">Professional positioning</p><h2>{profile?.positioning?.headline ?? 'No active positioning yet'}</h2><div className="tag-row">{core.map((item: string) => <span className="tag" key={item}>{item}</span>)}</div></article>
        <article className="panel panel--third"><p className="meta-label">Verified evidence</p><p className="stat">{evidence.length}</p><p className="muted">claims currently available for matching and application work.</p></article>
        <article className="panel panel--third"><p className="meta-label">Career sources</p><p className="stat">{sources.length}</p><p className="muted">governed sources behind the active profile.</p></article>
        <article className="panel panel--third"><p className="meta-label">Open verification</p><p className="stat">{queue.filter((item: any) => item.status === 'open').length}</p><p className="muted">questions that constrain stronger claims until resolved.</p></article>
        <article className="panel panel--full"><h2>Evidence map</h2><div className="section-stack">{evidence.length ? evidence.map((item: any) => <div className="row" key={item.id}><strong>{item.claim}</strong><span className="status">{item.status}</span></div>) : <div className="empty-state">No verified evidence is active yet. Add source documents before matching or application work.</div>}</div></article>
        <article className="panel"><h2>Search defaults attached to this profile</h2><dl className="definition-list"><dt>Anchors</dt><dd>{(search?.geographies?.anchors ?? []).join(', ') || 'Not set'}</dd><dt>Remote</dt><dd>{search?.geographies?.remote_allowed ? 'Allowed' : 'Off'}</dd><dt>Role lanes</dt><dd>{(search?.lanes ?? []).length}</dd></dl><div className="inline-actions"><a className="button button--primary" href="/find">Review search setup</a></div></article>
        <article className="panel panel--wide"><h2>Profile actions and verification</h2><ProfileActions queue={queue} /></article>
      </section>
    </main>
  );
}
