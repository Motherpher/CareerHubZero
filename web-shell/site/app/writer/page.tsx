import { loadHubProfile } from '@/lib/profile';

const fallbackLabels: Record<string, string> = {
  home: 'Home',
  writer: 'Writer Room',
  career: 'CareerHub',
  profile: 'Profile',
  find: 'Search',
  analyse: 'Analyse',
  apply: 'Apply',
  track: 'Track',
  library: 'Library'
};

export default function WriterRoomPage() {
  const hub = loadHubProfile();
  const room = hub.profile_shell?.rooms?.find((item) => item.id === 'writer');
  const labels = { ...fallbackLabels, ...(hub.navigation.labels ?? {}) };

  return (
    <main className="workspace">
      <header className="workspace-header">
        <div className="breadcrumb"><a href="/">{hub.identity.display_name}</a> / {room?.label ?? 'Writer Room'}</div>
        <div className="workspace-title">
          <div>
            <p className="eyebrow">Professional workroom</p>
            <h1>{room?.label ?? 'Writer & Journalism Room'}</h1>
            <p className="lead">{room?.description ?? 'Writing, reporting, research, editorial development, archive and portfolio.'}</p>
          </div>
          <nav aria-label="Primary" className="nav">
            {hub.navigation.primary.map((item) => (
              <a href={`/${item === 'home' ? '' : item}`} aria-current={item === 'writer' ? 'page' : undefined} key={item}>{labels[item] ?? item}</a>
            ))}
          </nav>
        </div>
      </header>

      <section className="panel-grid">
        <article className="panel panel--full">
          <p className="meta-label">Room scope</p>
          <h2>The work itself</h2>
          <p className="muted">This room is separate from CareerHub. It is the home for writing and journalism work, not vacancy or application state.</p>
          {room?.features?.length ? <div className="tag-row">{room.features.map((feature) => <span className="tag" key={feature}>{feature}</span>)}</div> : null}
        </article>

        <article className="panel panel--third"><p className="meta-label">Work desk</p><h2>Ideas → pitches → reporting → drafts</h2><p className="muted">Active work and commissions belong here.</p></article>
        <article className="panel panel--third"><p className="meta-label">Archive</p><h2>Published work and evidence</h2><p className="muted">The reconstructed bibliography and publication evidence remain the archive layer.</p></article>
        <article className="panel panel--third"><p className="meta-label">Portfolio</p><h2>Selective public presentation</h2><p className="muted">Portfolio choices are editorial, not automatic archive exposure.</p></article>

        <article className="panel panel--full">
          <h2>Writer Room tools</h2>
          <div className="inline-actions">
            {(room?.links ?? []).map((link) => <a className="button" href={link.href} key={link.href}>{link.label}</a>)}
          </div>
        </article>

        <article className="panel panel--full">
          <p className="meta-label">Boundary</p>
          <h2>WriterRoom ↔ CareerHub</h2>
          <p className="muted">Only explicitly approved, verified evidence crosses into CareerHub. Drafts, private reporting notes, confidential sources and unresolved archive leads do not transfer automatically.</p>
        </article>
      </section>
    </main>
  );
}
