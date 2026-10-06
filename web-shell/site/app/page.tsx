import CareerOverview from '@/app/_components/CareerOverview';
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

export default function HomePage() {
  const hub = loadHubProfile();
  const shell = hub.profile_shell;

  if (!shell?.enabled) {
    return <CareerOverview />;
  }

  const rooms = shell.rooms ?? [];
  const labels = { ...fallbackLabels, ...(hub.navigation.labels ?? {}) };

  return (
    <main className={`hub hub--profile hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="hero hero--profile">
        <div className="hero-copy">
          <p className="eyebrow">Personal professional workspace</p>
          <h1>{shell.headline ?? hub.identity.display_name}</h1>
          <p className="lead">{shell.intro ?? 'Choose the workspace you want to enter.'}</p>
        </div>
        <nav aria-label="Primary" className="nav nav--profile">
          {hub.navigation.primary.map((item) => (
            <a href={`/${item === 'home' ? '' : item}`} key={item}>{labels[item] ?? item}</a>
          ))}
        </nav>
      </header>

      <section className="room-grid" aria-label="Profile rooms">
        {rooms.map((room, index) => (
          <article className={`room-card room-card--${room.id}`} key={room.id}>
            <div className="room-card__topline">
              <p className="card-kicker">{room.eyebrow ?? 'Workspace'}</p>
              <span className="room-index">0{index + 1}</span>
            </div>
            <div className="room-card__body">
              <h2>{room.label}</h2>
              <p className="room-description">{room.description}</p>
            </div>
            {room.features?.length ? (
              <ul className="room-features">{room.features.map((feature) => <li key={feature}>{feature}</li>)}</ul>
            ) : null}
            <a className="room-cta" href={room.href}><span>{room.cta ?? `Open ${room.label}`}</span><span aria-hidden="true">↗</span></a>
          </article>
        ))}
      </section>

      <section className="profile-utility" aria-label="Profile-level actions">
        <div><p className="meta-label">Shared profile layer</p><p>Verified professional evidence and source material sit beneath both rooms without merging their operational state.</p></div>
        <div className="inline-actions">
          <a className="button" href="/profile">Career evidence</a>
          <a className="button" href="/library">Source library</a>
        </div>
      </section>
    </main>
  );
}
