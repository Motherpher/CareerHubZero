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
  library: 'Library',
  help: 'Help',
};

const helpAnchors: Record<string, string> = {
  profile: 'profile',
  find: 'search',
  analyse: 'analyse',
  apply: 'apply',
  track: 'track',
  library: 'library',
};

export default function WorkspaceHeader({ current, title, intro }: { current: string; title: string; intro?: string }) {
  const hub = loadHubProfile();
  const labels = { ...fallbackLabels, ...(hub.navigation.labels ?? {}) };
  const sv = (hub.identity.language ?? 'en').toLowerCase().startsWith('sv');
  const helpHref = current === 'help' ? '/help' : `/help#${helpAnchors[current] ?? current}`;

  return (
    <header className="workspace-header">
      <div className="breadcrumb"><a href="/">{hub.identity.display_name}</a> / {labels[current] ?? current}</div>
      <div className="workspace-title">
        <div>
          <p className="eyebrow">Career workspace</p>
          <h1>{title}</h1>
          {intro ? <p className="lead">{intro}</p> : null}
        </div>
        <nav aria-label="Primary" className="nav">
          {hub.navigation.primary.map((item) => (
            <a href={`/${item === 'home' ? '' : item}`} aria-current={item === current ? 'page' : undefined} key={item}>
              {labels[item] ?? item}
            </a>
          ))}
          <a href={helpHref} aria-current={current === 'help' ? 'page' : undefined}>{sv ? 'Hjälp' : 'Help'}</a>
        </nav>
      </div>
    </header>
  );
}
