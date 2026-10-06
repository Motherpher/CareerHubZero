import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import HelpSearch from './HelpSearch';

export default function HelpPage() {
  return (
    <main className="workspace">
      <WorkspaceHeader
        current="help"
        title="CareerHub Q&A"
        intro="Search plain-language explanations for how CareerHub works, what each step means, and what to do when something is unclear."
      />
      <section className="panel-grid">
        <article className="panel panel--full">
          <HelpSearch />
        </article>
      </section>
    </main>
  );
}
