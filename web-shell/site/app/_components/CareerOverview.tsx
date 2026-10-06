import { loadHubProfile } from '@/lib/profile';
import { candidateEvidenceCount, careerSourceCount, loadApplications, loadJobVault, loadSearchProfile } from '@/lib/data';

const labels: Record<string, string> = {
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

export default function CareerOverview() {
  const hub = loadHubProfile();
  const search = loadSearchProfile();
  const jobs = loadJobVault()?.jobs ?? [];
  const applications = loadApplications()?.applications ?? [];
  const anchors = search?.geographies?.anchors ?? [];
  const lanes = search?.lanes ?? [];
  const evidence = candidateEvidenceCount();
  const sources = careerSourceCount();
  const navLabels = { ...labels, ...(hub.navigation.labels ?? {}) };

  return (
    <main className={`hub hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="hero">
        <div>
          <p className="eyebrow">{hub.identity.display_name}</p>
          <h1>{hub.home.headline ?? 'Career workspace'}</h1>
          <p className="lead">{hub.home.intro ?? hub.identity.strapline}</p>
        </div>
        <nav aria-label="Primary" className="nav">
          {hub.navigation.primary.map((item) => (
            <a href={`/${item === 'home' ? '' : item}`} key={item}>{navLabels[item] ?? item}</a>
          ))}
        </nav>
      </header>
      <section className="action-band" aria-label="Primary CareerHub actions">
        <a className="action action--primary" href="/profile">See current profile</a>
        <a className="action" href="/find">Search with my settings</a>
        <a className="action" href="/library">Update my sources</a>
      </section>
      <section className="grid" aria-label="CareerHub dashboard">
        <article className="card card--wide">
          <p className="card-kicker">Current direction</p>
          <h2>{hub.identity.strapline}</h2>
          <div className="tag-row">{lanes.slice(0, 6).map((lane: any) => <span className="tag" key={lane.lane_id}>{lane.name}</span>)}</div>
        </article>
        <article className="card"><p className="card-kicker">Profile state</p><p className="stat">{evidence}</p><p>verified evidence claims from {sources} governed career sources.</p></article>
        <article className="card"><p className="card-kicker">Search geography</p><h2>{anchors.join(' + ') || 'Not configured'}</h2><p>{search?.geographies?.remote_allowed ? 'Remote opportunities are also allowed.' : 'Remote search is off.'}</p></article>
        <article className="card"><p className="card-kicker">Opportunity queue</p><p className="stat">{jobs.length}</p><p>roles currently stored in the job vault.</p></article>
        <article className="card"><p className="card-kicker">Applications</p><p className="stat">{applications.length}</p><p>applications currently tracked.</p></article>
        <article className="card card--wide"><p className="card-kicker">Next useful move</p><h2>Check the profile, confirm search scope, then search.</h2><p>The site keeps the active evidence profile visible before job discovery so matching never becomes a black box.</p></article>
      </section>
    </main>
  );
}
