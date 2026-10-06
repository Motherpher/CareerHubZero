import { loadHubProfile } from '@/lib/profile';

const fallbackLabels: Record<string, string> = {
  home: 'Home',
  writer: 'Portfolio',
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
    <main className="workspace portfolio-room">
      <header className="portfolio-masthead">
        <div className="breadcrumb"><a href="/">{hub.identity.display_name}</a> / {room?.label ?? 'Portfolio'}</div>
        <nav aria-label="Primary" className="nav nav--profile">
          {hub.navigation.primary.map((item) => (
            <a href={`/${item === 'home' ? '' : item}`} aria-current={item === 'writer' ? 'page' : undefined} key={item}>{labels[item] ?? item}</a>
          ))}
        </nav>
        <div className="portfolio-title-block">
          <p className="eyebrow">Writing · reporting · editorial work</p>
          <h1>{room?.label ?? 'Portfolio'}</h1>
          <p className="lead">{room?.description ?? 'Writing, reporting, research, editorial development, archive and portfolio.'}</p>
        </div>
      </header>

      <section className="portfolio-intro">
        <div>
          <p className="meta-label">Practice</p>
          <h2>Work in motion and work already published.</h2>
        </div>
        <p className="portfolio-intro__copy">This space holds the professional body of work itself: active stories, pitches, research, editorial development, publication records and the curated public portfolio. CareerHub remains a separate room for employment search and applications.</p>
      </section>

      <section className="portfolio-departments" aria-label="Portfolio areas">
        <article className="portfolio-department portfolio-department--lead"><span>01</span><p className="meta-label">Work desk</p><h2>Ideas, pitches, reporting and drafts</h2><p>Active writing, commissions and editorial development live here.</p></article>
        <article className="portfolio-department"><span>02</span><p className="meta-label">Reporting</p><h2>Research, interviews and source work</h2><p>Story questions, evidence and reporting material stay attached to the work they support.</p></article>
        <article className="portfolio-department"><span>03</span><p className="meta-label">Publication archive</p><h2>Published work and provenance</h2><p>The reconstructed bibliography remains the evidence base behind the portfolio.</p></article>
        <article className="portfolio-department"><span>04</span><p className="meta-label">Selected work</p><h2>Curated public portfolio</h2><p>Not everything in the archive needs to represent Weronika publicly.</p></article>
      </section>

      <section className="portfolio-links">
        <div>
          <p className="meta-label">Working surfaces</p>
          <h2>Open the material behind the portfolio</h2>
        </div>
        <div className="portfolio-link-list">
          {(room?.links ?? []).map((link, index) => (
            <a href={link.href} key={link.href}><span>0{index + 1}</span><strong>{link.label}</strong><span aria-hidden="true">↗</span></a>
          ))}
        </div>
      </section>

      <section className="portfolio-boundary">
        <p className="meta-label">Career bridge</p>
        <h2>Portfolio evidence can support CareerHub. The rooms do not merge.</h2>
        <p>Only explicitly approved, verified material crosses into CareerHub. Drafts, private reporting notes, confidential sources and unresolved archive leads remain outside the employment-search workflow.</p>
        <a className="text-link" href="/career">Open CareerHub ↗</a>
      </section>
    </main>
  );
}
