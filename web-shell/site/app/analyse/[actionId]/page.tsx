import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import AnalysisResultClient from './AnalysisResultClient';
import { loadHubProfile } from '@/lib/profile';

export default async function AnalysisResultPage({ params }: { params: Promise<{ actionId: string }> }) {
  const { actionId } = await params;
  const hub = loadHubProfile();
  const language = hub.identity.language ?? 'en';
  const sv = language.toLowerCase().startsWith('sv');
  return (
    <main className="workspace">
      <WorkspaceHeader current="analyse" title={sv ? 'Jobbanalys' : 'Job analysis'} intro={sv ? 'Den här adressen följer analysen från start tills resultatet är varaktigt sparat och går att öppna igen.' : 'This address follows the analysis from launch until the result is durably stored and can be reopened.'} />
      <section className="panel-grid">
        <article className="panel panel--full">
          <AnalysisResultClient actionId={actionId} language={language} />
        </article>
      </section>
    </main>
  );
}
