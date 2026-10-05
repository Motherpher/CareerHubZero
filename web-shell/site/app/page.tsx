import { loadHubProfile } from '@/lib/profile';

const defaultLabels: Record<string, string> = {
  home: 'Home',
  find: 'Find',
  analyse: 'Analyse',
  apply: 'Apply',
  track: 'Track',
  profile: 'Profile',
  library: 'Library'
};

const slotCopy: Record<string, { title: string; text: string }> = {
  identity: { title: 'Direction', text: 'Your current professional direction and positioning.' },
  priority: { title: 'Priority', text: 'What matters most in the current job-search cycle.' },
  next_action: { title: 'Next action', text: 'The most useful next move based on your active pipeline.' },
  opportunities: { title: 'Opportunities', text: 'Saved and ranked roles from your search raster.' },
  pipeline: { title: 'Pipeline', text: 'Applications across applied, contact, interview and decision states.' },
  hrdm: { title: 'Role analyses', text: 'Recent HRDM reverse reads and candidate positioning work.' },
  profile_health: { title: 'Profile health', text: 'Verified evidence coverage and source status.' },
  search_coverage: { title: 'Search coverage', text: 'Current geography, job families and sourcing coverage.' },
  artifacts: { title: 'Library', text: 'CVs, letters, reports and generated application artifacts.' }
};

export default function HomePage() {
  const hub = loadHubProfile();
  const labels = { ...defaultLabels, ...(hub.navigation.labels ?? {}) };

  return (
    <main className={`hub hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="hero">
        <div>
          <p className="eyebrow">CareerHub</p>
          <h1>{hub.home.headline ?? hub.identity.display_name}</h1>
          <p className="lead">{hub.home.intro ?? hub.identity.strapline}</p>
        </div>
        <nav aria-label="Primary" className="nav">
          {hub.navigation.primary.map((item) => (
            <a href={`/${item === 'home' ? '' : item}`} key={item}>{labels[item] ?? item}</a>
          ))}
        </nav>
      </header>

      <section className="action-band" aria-label="Primary CareerHub actions">
        <a className="action action--primary" href="/find">Find jobs</a>
        <a className="action" href="/analyse">Analyse?</a>
        <a className="action" href="/apply">Apply</a>
      </section>

      <section className="grid" aria-label="CareerHub dashboard">
        {hub.home.slots.map((slot) => {
          const copy = slotCopy[slot] ?? { title: slot, text: '' };
          return (
            <article className={`card card--${slot}`} key={slot}>
              <p className="card-kicker">{slot.replaceAll('_', ' ')}</p>
              <h2>{copy.title}</h2>
              <p>{copy.text}</p>
            </article>
          );
        })}
      </section>
    </main>
  );
}
