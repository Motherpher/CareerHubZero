import { loadHubProfile } from '@/lib/profile';
import { candidateEvidenceCount, careerSourceCount, loadApplications, loadJobVault, loadSearchProfile } from '@/lib/data';

const defaultLabels: Record<string, string> = {
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

type Copy = {
  nav: string;
  actions: { find: string; profile: string; library: string };
  currentDirection: string;
  profileState: string;
  profileStateText: (evidence: number, sources: number) => string;
  searchGeography: string;
  notConfigured: string;
  remoteOn: string;
  remoteOff: string;
  opportunities: string;
  opportunitiesText: string;
  applications: string;
  applicationsText: string;
  nextAction: string;
  nextActionTitle: string;
  nextActionText: string;
  preparedMaterial: string;
  preparedMaterialTitle: string;
  preparedMaterialText: string;
  analysis: string;
  analysisTitle: string;
  analysisText: string;
};

function copyFor(language?: string): Copy {
  const sv = (language ?? 'en').toLowerCase().startsWith('sv');
  if (sv) {
    return {
      nav: 'Huvudnavigation',
      actions: { find: 'Hitta jobb', profile: 'Min profil', library: 'Mina underlag' },
      currentDirection: 'Din riktning',
      profileState: 'Profilunderlag',
      profileStateText: (evidence, sources) => `${evidence} verifierade uppgifter från ${sources} godkända karriärkällor.`,
      searchGeography: 'Sökområde',
      notConfigured: 'Inte inställt ännu',
      remoteOn: 'Även distansmöjligheter ingår.',
      remoteOff: 'Distanssökning är inte vald.',
      opportunities: 'Möjligheter',
      opportunitiesText: 'jobb finns just nu sparade för dig att titta på.',
      applications: 'Pågående',
      applicationsText: 'processer finns samlade i din uppföljning.',
      nextAction: 'När du vill',
      nextActionTitle: 'Se vad som är aktuellt och välj vad du vill titta närmare på.',
      nextActionText: 'Du väljer tempot. Vi håller ihop analys, underlag och nästa steg.',
      preparedMaterial: 'Förberett för dig',
      preparedMaterialTitle: 'Dina underlag finns samlade på ett ställe.',
      preparedMaterialText: 'När du vill kan du öppna, granska och använda det som redan är förberett.',
      analysis: 'Analyser',
      analysisTitle: 'Titta närmare på ett jobb när något känns intressant.',
      analysisText: 'Analysen hjälper dig att förstå rollen, kraven och hur din verifierade erfarenhet möter dem.'
    };
  }
  return {
    nav: 'Primary',
    actions: { find: 'Find jobs', profile: 'My profile', library: 'My materials' },
    currentDirection: 'Your direction',
    profileState: 'Profile evidence',
    profileStateText: (evidence, sources) => `${evidence} verified evidence claims from ${sources} governed career sources.`,
    searchGeography: 'Search area',
    notConfigured: 'Not configured yet',
    remoteOn: 'Remote opportunities are included.',
    remoteOff: 'Remote search is not selected.',
    opportunities: 'Opportunities',
    opportunitiesText: 'roles are currently saved for you to review.',
    applications: 'In progress',
    applicationsText: 'application processes are currently being tracked.',
    nextAction: 'Whenever you are ready',
    nextActionTitle: 'See what is current and choose what you want to explore.',
    nextActionText: 'You set the pace. We keep the analysis, material and next step together.',
    preparedMaterial: 'Prepared for you',
    preparedMaterialTitle: 'Your materials are collected in one place.',
    preparedMaterialText: 'Open, review and use what has already been prepared whenever you want.',
    analysis: 'Analyses',
    analysisTitle: 'Look closer at a role when something catches your interest.',
    analysisText: 'The analysis helps you understand the role, requirements and how your verified experience meets them.'
  };
}

export default function CareerOverview() {
  const hub = loadHubProfile();
  const search = loadSearchProfile();
  const jobs = loadJobVault()?.jobs ?? [];
  const applications = loadApplications()?.applications ?? [];
  const anchors = search?.geographies?.anchors ?? [];
  const lanes = search?.lanes ?? [];
  const evidence = candidateEvidenceCount();
  const sources = careerSourceCount();
  const navLabels = { ...defaultLabels, ...(hub.navigation.labels ?? {}) };
  const copy = copyFor(hub.identity.language);

  const cards: Record<string, React.ReactNode> = {
    identity: (
      <article className="card card--wide" key="identity">
        <p className="card-kicker">{copy.currentDirection}</p>
        <h2>{hub.identity.strapline}</h2>
        {lanes.length ? <div className="tag-row">{lanes.slice(0, 6).map((lane: any) => <span className="tag" key={lane.lane_id}>{lane.name}</span>)}</div> : null}
      </article>
    ),
    next_action: (
      <article className="card card--wide card--next_action" key="next_action">
        <p className="card-kicker">{copy.nextAction}</p>
        <h2>{copy.nextActionTitle}</h2>
        <p>{copy.nextActionText}</p>
      </article>
    ),
    opportunities: (
      <article className="card card--opportunities" key="opportunities">
        <p className="card-kicker">{copy.opportunities}</p>
        <p className="stat">{jobs.length}</p>
        <p>{copy.opportunitiesText}</p>
      </article>
    ),
    pipeline: (
      <article className="card" key="pipeline">
        <p className="card-kicker">{copy.applications}</p>
        <p className="stat">{applications.length}</p>
        <p>{copy.applicationsText}</p>
      </article>
    ),
    artifacts: (
      <article className="card card--wide" key="artifacts">
        <p className="card-kicker">{copy.preparedMaterial}</p>
        <h2>{copy.preparedMaterialTitle}</h2>
        <p>{copy.preparedMaterialText}</p>
      </article>
    ),
    profile_health: (
      <article className="card" key="profile_health">
        <p className="card-kicker">{copy.profileState}</p>
        <p className="stat">{evidence}</p>
        <p>{copy.profileStateText(evidence, sources)}</p>
      </article>
    ),
    search_coverage: (
      <article className="card" key="search_coverage">
        <p className="card-kicker">{copy.searchGeography}</p>
        <h2>{anchors.join(' + ') || copy.notConfigured}</h2>
        <p>{search?.geographies?.remote_allowed ? copy.remoteOn : copy.remoteOff}</p>
      </article>
    ),
    hrdm: (
      <article className="card card--wide" key="hrdm">
        <p className="card-kicker">{copy.analysis}</p>
        <h2>{copy.analysisTitle}</h2>
        <p>{copy.analysisText}</p>
      </article>
    )
  };

  const orderedCards = hub.home.slots.map((slot) => cards[slot]).filter(Boolean);

  return (
    <main className={`hub hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="hero">
        <div>
          <p className="eyebrow">{hub.identity.display_name}</p>
          <h1>{hub.home.headline ?? 'Career workspace'}</h1>
          <p className="lead">{hub.home.intro ?? hub.identity.strapline}</p>
        </div>
        <nav aria-label={copy.nav} className="nav">
          {hub.navigation.primary.map((item) => (
            <a href={`/${item === 'home' ? '' : item}`} key={item}>{navLabels[item] ?? item}</a>
          ))}
        </nav>
      </header>
      <section className="action-band" aria-label={copy.nav}>
        <a className="action action--primary" href="/find">{copy.actions.find}</a>
        <a className="action" href="/profile">{copy.actions.profile}</a>
        <a className="action" href="/library">{copy.actions.library}</a>
      </section>
      <section className="grid" aria-label="CareerHub">
        {orderedCards}
      </section>
    </main>
  );
}
