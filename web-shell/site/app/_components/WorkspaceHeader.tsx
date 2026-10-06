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
  help: 'Help'
};

export default function WorkspaceHeader({ current, title, intro }: { current: string; title: string; intro?: string }) {
  const hub = loadHubProfile();
  const language = hub.identity.language ?? 'en';
  const sv = language.toLowerCase().startsWith('sv');
  const labels = { ...fallbackLabels, ...(hub.navigation.labels ?? {}) };
  return (
    <header className="workspace-header">
      <div className="breadcrumb"><a href="/">{hub.identity.display_name}</a> / {labels[current] ?? current}</div>
      <div className="workspace-title">
        <div>
          <p className="eyebrow">Career workspace</p>
          <h1>{title}</h1>
          {intro ? <p className="lead">{intro}</p> : null}
        </div>
        <div className="workspace-header__tools">
          <form action="/help" method="get" className="help-search" role="search">
            <input name="q" aria-label={sv ? 'Sök i hjälpen' : 'Search help'} placeholder={sv ? 'Sök hjälp…' : 'Search help…'} />
            <button className="button" type="submit">{sv ? 'Hjälp' : 'Help'}</button>
          </form>
          <nav aria-label="Primary" className="nav">
            {hub.navigation.primary.map((item) => (
              <a href={`/${item === 'home' ? '' : item}`} aria-current={item === current ? 'page' : undefined} key={item}>
                {labels[item] ?? item}
              </a>
            ))}
            <a href="/help" aria-current={current === 'help' ? 'page' : undefined}>{sv ? 'Hjälp' : 'Help'}</a>
          </nav>
        </div>
      </div>
    </header>
  );
}
