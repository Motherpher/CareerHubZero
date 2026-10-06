import CareerOverview from '@/app/_components/CareerOverview';
import MotorGuide from '@/app/_components/MotorGuide';
import { loadSearchProfile } from '@/lib/data';
import { loadHubProfile } from '@/lib/profile';

const fallbackLabels: Record<string, string> = {
  home: 'Home', writer: 'Writer Room', career: 'CareerHub', profile: 'Profile', find: 'Search', analyse: 'Analyse', apply: 'Apply', track: 'Track', library: 'Library'
};

export default function HomePage() {
  const hub = loadHubProfile();
  const search = loadSearchProfile();
  const shell = hub.profile_shell;

  if (!shell?.enabled) return <CareerOverview />;

  const rooms = shell.rooms ?? [];
  const labels = { ...fallbackLabels, ...(hub.navigation.labels ?? {}) };
  const lanes = Array.isArray(search?.lanes) ? search.lanes : [];

  return (
    <main className={`hub hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="hero">
        <div><p className="eyebrow">Profile workspace</p><h1>{shell.headline ?? hub.identity.display_name}</h1><p className="lead">{shell.intro ?? 'Choose the workspace you want to enter.'}</p></div>
        <nav aria-label="Primary" className="nav">{hub.navigation.primary.map((item) => <a href={`/${item === 'home' ? '' : item}`} key={item}>{labels[item] ?? item}</a>)}</nav>
      </header>

      <MotorGuide profileName={hub.identity.display_name} lanes={lanes} />

      <section className="grid" aria-label="Profile rooms">
        {rooms.map((room) => <article className="card card--wide" key={room.id}>
          <p className="card-kicker">{room.eyebrow ?? 'Workspace'}</p><h2>{room.label}</h2><p>{room.description}</p>
          {room.features?.length ? <div className="tag-row">{room.features.map((feature) => <span className="tag" key={feature}>{feature}</span>)}</div> : null}
          <div className="inline-actions"><a className="button button--primary" href={room.href}>{room.cta ?? `Open ${room.label}`}</a></div>
        </article>)}
      </section>

      <section className="action-band" aria-label="Profile-level actions"><a className="action" href="/profile">Career evidence profile</a><a className="action" href="/find">Search profile and lanes</a><a className="action" href="/library">Source library</a></section>
    </main>
  );
}
