import CareerOverview from '@/app/_components/CareerOverview';
import { loadHubProfile, loadProfileShell } from '@/lib/profile';

export default function HomePage() {
  const hub = loadHubProfile();
  const shell = loadProfileShell();
  const sv = (hub.identity.language ?? 'en').toLowerCase().startsWith('sv');

  if (!shell?.enabled) return <CareerOverview />;

  const rooms = shell.rooms ?? [];

  return (
    <main className={`hub hub--profile hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="hero hero--profile">
        <div className="hero-copy">
          <p className="eyebrow">Personal professional workspace</p>
          <h1>{shell.headline ?? hub.identity.display_name}</h1>
          <p className="lead">{shell.intro ?? 'Choose the workspace you want to enter.'}</p>
        </div>
        <nav aria-label="Primary" className="nav nav--profile">
          <a href="/" aria-current="page">Home</a>
          {rooms.map((room) => <a href={room.href} key={room.id}>{room.label}</a>)}
          <a href="/help">{sv ? 'Hjälp' : 'Help'}</a>
        </nav>
      </header>

      <section className="room-grid" aria-label="Profile rooms">
        {rooms.map((room, index) => (
          <article className={`room-card room-card--${room.id}`} key={room.id}>
            <div className="room-card__topline"><p className="card-kicker">{room.eyebrow ?? 'Workspace'}</p><span className="room-index">0{index + 1}</span></div>
            <div className="room-card__body"><h2>{room.label}</h2><p className="room-description">{room.description}</p></div>
            {room.features?.length ? <ul className="room-features">{room.features.map((feature) => <li key={feature}>{feature}</li>)}</ul> : null}
            <a className="room-cta" href={room.href}><span>{room.cta ?? `Open ${room.label}`}</span><span aria-hidden="true">↗</span></a>
          </article>
        ))}
      </section>

      <section className="profile-utility" aria-label="Profile architecture">
        <div>
          <p className="meta-label">One profile · separate workspaces</p>
          <p>The profile supplies verified professional context. Each room owns its own operational state and only receives information through its permitted boundary.</p>
        </div>
        <a className="text-link" href="/help">{sv ? 'Öppna hjälp och vanliga frågor' : 'Open Help and common questions'}</a>
      </section>
    </main>
  );
}
