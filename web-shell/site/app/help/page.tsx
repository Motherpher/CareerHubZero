import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import HelpClient from '@/app/help/HelpClient';
import { loadHubProfile } from '@/lib/profile';

export default function HelpPage() {
  const hub = loadHubProfile();
  const language = hub.identity.language ?? 'en';
  const sv = language.toLowerCase().startsWith('sv');

  return (
    <main className="workspace">
      <WorkspaceHeader
        current="help"
        title={sv ? 'Hjälp' : 'Help'}
        intro={sv
          ? 'Sök svar om hur CareerHub fungerar i praktiken – från Profil och Sök till Jobbanalys, Bibliotek, status och fel.'
          : 'Search practical answers about how CareerHub works — from Profile and Search to Job Analysis, Library, statuses and errors.'}
      />
      <section className="panel-grid">
        <article className="panel panel--full">
          <HelpClient language={language} />
        </article>
      </section>
    </main>
  );
}
