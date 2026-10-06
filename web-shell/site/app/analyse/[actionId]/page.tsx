import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import AnalysisResultClient from './AnalysisResultClient';

export default async function AnalysisResultPage({ params }: { params: Promise<{ actionId: string }> }) {
  const { actionId } = await params;
  return (
    <main className="workspace">
      <WorkspaceHeader current="analyse" title="HRDM-R analysis" intro="This page keeps one Motor run addressable while it executes and after its report is complete." />
      <section className="panel-grid">
        <article className="panel panel--full">
          <AnalysisResultClient actionId={actionId} />
        </article>
      </section>
    </main>
  );
}
