'use client';

import { useMemo, useState } from 'react';

type HelpItem = {
  question: string;
  answer: string;
  tags: string[];
  href?: string;
  linkLabel?: string;
};

const ITEMS: HelpItem[] = [
  {
    question: 'What is the Career Profile?',
    answer: 'The Career Profile is the evidence CareerHub is currently allowed to use when it assesses fit, writes applications and makes candidate-facing claims. It is deliberately stricter than a normal CV draft.',
    tags: ['profile', 'evidence', 'claims'],
    href: '/profile',
    linkLabel: 'Open Profile',
  },
  {
    question: 'How do I change my Career Profile?',
    answer: 'Start in Library. Add, replace, activate or deactivate the source that supports the change. Then request evidence review or a profile rebuild. CareerHub does not let an unsupported claim become true just because it was typed into the interface.',
    tags: ['profile', 'edit', 'change', 'library', 'review'],
    href: '/library',
    linkLabel: 'Open Library',
  },
  {
    question: 'Why can’t I directly rewrite a verified profile claim?',
    answer: 'Because the profile is an evidence-governed layer. Direct free-text editing would make it easy to turn a preference or assumption into a factual career claim. Use source evidence plus review instead.',
    tags: ['profile', 'verified', 'governance'],
    href: '/profile',
    linkLabel: 'Review Profile',
  },
  {
    question: 'What is the Search Profile?',
    answer: 'The Search Profile tells CareerHub what to look for. Geography, work format, engagement types, search needs and role lanes belong here. Search preferences do not automatically become facts about the candidate.',
    tags: ['search', 'profile', 'preferences'],
    href: '/find',
    linkLabel: 'Open Search',
  },
  {
    question: 'What is a role lane?',
    answer: 'A role lane is a search direction. It groups a role family with search terms so CareerHub can look in several coherent directions without mixing them together. A lane is not a claim that you already hold every skill found in that lane.',
    tags: ['search', 'lane', 'role lane', 'keywords'],
    href: '/find',
    linkLabel: 'Review role lanes',
  },
  {
    question: 'How do I change a role lane?',
    answer: 'In Search, open “Edit saved Search Profile”. Rename the lane or edit the search terms beneath it, then save. Those changes become the defaults for future searches. The lane bucket and priority remain governed by the existing search architecture.',
    tags: ['search', 'lane', 'edit', 'keywords'],
    href: '/find#edit-search-profile',
    linkLabel: 'Edit Search Profile',
  },
  {
    question: 'What is the difference between a saved Search Profile and “This-search need”?',
    answer: 'Saved Search Profile settings persist into future searches. “This-search need” changes only the current run, which is useful for experiments such as “AI”, “part-time”, or a particular city without rewriting your defaults.',
    tags: ['search', 'session', 'override', 'saved'],
    href: '/find',
    linkLabel: 'Open Search',
  },
  {
    question: 'What does the blinking red dot mean?',
    answer: 'CareerHub is actively waiting on a process in this window: for example a search, an analysis request or another operation. Do not interpret the dot as an error. The text beside it tells you what CareerHub is currently doing.',
    tags: ['red dot', 'working', 'waiting', 'process'],
  },
  {
    question: 'What does “saved but not started” mean?',
    answer: 'CareerHub accepted and stored your request, but the secure connection that starts the central motor is not available on that deployment. Nothing is analysing or changing yet. The reference is kept so the request can be identified.',
    tags: ['queued', 'dispatcher', 'motor', 'action', 'reference'],
  },
  {
    question: 'What does “started — motor working in the background” mean?',
    answer: 'The site successfully handed the request to the CareerHub motor. The motor can continue after the web request returns. Generated analysis, application or state changes appear after the motor commits the result and the site updates.',
    tags: ['running', 'motor', 'background', 'action'],
  },
  {
    question: 'What is an ACT reference?',
    answer: 'An ACT reference is the unique identifier for a motor request. It is useful for tracing what happened if an action fails, takes longer than expected or needs review. It is not a score or application number.',
    tags: ['act', 'reference', 'action id'],
  },
  {
    question: 'What does HRDM-R do?',
    answer: 'HRDM-R analyses a specific role against the active verified profile. It produces the governed role analysis used before candidate positioning and application generation. It does not treat search preference as evidence.',
    tags: ['hrdm', 'analysis', 'role'],
    href: '/analyse',
    linkLabel: 'Open Analyse',
  },
  {
    question: 'What does ACTIVE mean in Library?',
    answer: 'ACTIVE means the source is available for governed CareerHub use. It does not mean every statement in the file is automatically verified or copied into the Career Profile.',
    tags: ['library', 'active', 'evidence'],
    href: '/library',
    linkLabel: 'Open Library',
  },
  {
    question: 'What happens after I upload a document?',
    answer: 'The document is stored privately and classified. If it should affect your profile, request evidence review. Uploading by itself does not silently rewrite the Career Profile.',
    tags: ['library', 'upload', 'document', 'profile'],
    href: '/library',
    linkLabel: 'Open Library',
  },
  {
    question: 'What is the normal CareerHub workflow?',
    answer: 'Profile → Search → Analyse → Apply → Track. Library supports the evidence base, and Improve my CareerHub is where you can propose changes to the product or your profile experience.',
    tags: ['workflow', 'steps', 'process'],
    href: '/',
    linkLabel: 'Open Overview',
  },
  {
    question: 'Where do I find my prepared application?',
    answer: 'Open Apply. CareerHub lists generated application packages and analysis artifacts that have been bound to application cases.',
    tags: ['apply', 'application', 'document'],
    href: '/apply',
    linkLabel: 'Open Apply',
  },
  {
    question: 'When should I use Track?',
    answer: 'Use Track after a role becomes a governed application case. Keep status, priority, next action and dates current so CareerHub can show what needs attention next.',
    tags: ['track', 'application', 'status'],
    href: '/track',
    linkLabel: 'Open Track',
  },
  {
    question: 'What happens when I submit “Improve my CareerHub”?',
    answer: 'Your wish is routed into the Wish Bank. Profile-specific improvements stay with your CareerHub. Reusable motor improvements can become central CareerHub development work so other profiles may benefit as well.',
    tags: ['wish', 'improve', 'wish bank'],
    href: '/wish',
    linkLabel: 'Improve my CareerHub',
  },
];

export default function HelpSearch() {
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return ITEMS;
    return ITEMS.filter((item) => [item.question, item.answer, ...item.tags].join(' ').toLowerCase().includes(needle));
  }, [query]);

  return (
    <div className="help-search">
      <label className="help-search__field">
        <span className="meta-label">Search Q&amp;A</span>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Try: change profile, role lane, red dot, ACT reference…" />
      </label>
      <p className="muted help-search__count">{filtered.length} explanation{filtered.length === 1 ? '' : 's'} shown</p>
      <div className="help-list">
        {filtered.length ? filtered.map((item) => (
          <details className="help-item" key={item.question} open={Boolean(query.trim())}>
            <summary>{item.question}</summary>
            <div className="help-item__body">
              <p>{item.answer}</p>
              {item.href ? <a className="button" href={item.href}>{item.linkLabel ?? 'Open section'}</a> : null}
            </div>
          </details>
        )) : <div className="empty-state">No exact match. Try a shorter word such as “profile”, “lane”, “search”, “HRDM” or “Library”.</div>}
      </div>
    </div>
  );
}
