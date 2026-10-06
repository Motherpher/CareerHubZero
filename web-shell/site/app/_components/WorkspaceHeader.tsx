import { loadHubProfile } from '@/lib/profile';

const fallbackLabels: Record<string, string> = {
  home: 'Overview',
  profile: 'Profile',
  find: 'Search',
  analyse: 'Analyse',
  apply: 'Apply',
  track: 'Track',
  library: 'Library',
  help: 'Q&A',
};

const workflows: Record<string, string[]> = {
  home: ['Check where you are now', 'Continue the next useful step', 'Return here to see what changed'],
  profile: ['Check what CareerHub may use', 'Add or correct evidence in Library', 'Request review or rebuild before stronger claims are used'],
  find: ['Set or review your saved Search Profile', 'Run a search — optionally with a one-search-only need', 'Open a role or continue directly to analysis'],
  analyse: ['Choose or paste the role', 'Run HRDM-R against verified profile evidence', 'Continue with the generated application package'],
  apply: ['Open the prepared application package', 'Review the analysis and wording', 'Apply, then move the case into Track'],
  track: ['Update the application status', 'Set priority and next action', 'Keep the case current until it closes'],
  library: ['Upload or activate a source', 'Request evidence review when it should affect the profile', 'Reload the Library index and review the Profile'],
  help: ['Search the question in plain language', 'Read the short explanation', 'Follow the linked CareerHub step'],
};

export default function WorkspaceHeader({ current, title, intro }: { current: string; title: string; intro?: string }) {
  const hub = loadHubProfile();
  const labels = { ...fallbackLabels, ...(hub.navigation.labels ?? {}) };
  const workflow = workflows[current] ?? [];
  return (
    <header className="workspace-header">
      <div className="breadcrumb"><a href="/">{hub.identity.display_name}</a> / {labels[current] ?? current}</div>
      <div className="workspace-title">
        <div>
          <p className="eyebrow">Career workspace</p>
          <h1>{title}</h1>
          {intro ? <p className="lead">{intro}</p> : null}
          {workflow.length ? (
            <div className="workflow-guide" aria-label="How this section works">
              <div className="workflow-guide__head"><strong>How this works</strong><a href="/help">Open searchable Q&amp;A</a></div>
              <ol>
                {workflow.map((step, index) => <li key={step}><span>{index + 1}</span><p>{step}</p></li>)}
              </ol>
            </div>
          ) : null}
        </div>
        <nav aria-label="Primary" className="nav">
          {hub.navigation.primary.map((item) => (
            <a href={`/${item === 'home' ? '' : item}`} aria-current={item === current ? 'page' : undefined} key={item}>
              {labels[item] ?? item}
            </a>
          ))}
          <a href="/help" aria-current={current === 'help' ? 'page' : undefined}>Q&amp;A</a>
        </nav>
      </div>
    </header>
  );
}
