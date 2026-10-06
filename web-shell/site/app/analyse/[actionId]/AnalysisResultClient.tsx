'use client';

import { useEffect, useRef, useState } from 'react';
import HrdmReport from '../HrdmReport';

type ProcessState = 'WAITING_FOR_EXECUTION' | 'RUNNING' | 'COMPLETED' | 'FAILED';
const STORAGE_KEY = 'careerhub.active.analysis';

export default function AnalysisResultClient({ actionId, language = 'en' }: { actionId: string; language?: string }) {
  const sv = language.toLowerCase().startsWith('sv');
  const [state, setState] = useState<ProcessState>('WAITING_FOR_EXECUTION');
  const [message, setMessage] = useState(sv ? 'Hämtar analysstatus…' : 'Loading analysis state…');
  const [report, setReport] = useState<any>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    try {
      const current = window.localStorage.getItem(STORAGE_KEY);
      const parsed = current ? JSON.parse(current) : null;
      if (!parsed || parsed.actionId !== actionId) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ actionId, title: sv ? 'Jobbanalys' : 'Job analysis', startedAt: new Date().toISOString() }));
        window.dispatchEvent(new Event('careerhub-process-updated'));
      }
    } catch { /* optional UI persistence */ }

    async function load() {
      try {
        const response = await fetch(`/api/action/status?action_id=${encodeURIComponent(actionId)}`, { cache: 'no-store' });
        const data = await response.json().catch(() => ({}));
        const next = (data.state || 'FAILED') as ProcessState;
        setState(next);
        setMessage(data.message || (sv ? 'CareerHub kontrollerar analysen.' : 'CareerHub is checking this analysis.'));
        if (next === 'COMPLETED' && data.hrdm) {
          setReport(data.hrdm);
          window.dispatchEvent(new Event('careerhub-process-updated'));
          return;
        }
        if (next !== 'FAILED') timer.current = setTimeout(load, 4000);
      } catch {
        setMessage(sv ? 'Statuskontakten avbröts tillfälligt. Analysen fortsätter i bakgrunden.' : 'Status contact was interrupted temporarily. The analysis continues in the background.');
        timer.current = setTimeout(load, 8000);
      }
    }
    void load();
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [actionId, sv]);

  const active = state === 'WAITING_FOR_EXECUTION' || state === 'RUNNING';
  const stateLabel = active ? (sv ? 'Analys pågår' : 'Analysis running') : state === 'COMPLETED' ? (sv ? 'Analysen är klar' : 'Analysis complete') : (sv ? 'Analysen misslyckades' : 'Analysis failed');
  return (
    <>
      <div className={`process-status process-status--${state.toLowerCase()}`} aria-live="polite">
        <span className={`process-status__dot ${active ? 'process-status__dot--active' : ''}`} aria-hidden="true" />
        <div>
          <strong>{stateLabel}</strong>
          <p>{message}</p>
          {active ? <p className="muted">{sv ? 'Du kan lämna sidan. Processen fortsätter och tar normalt cirka 2–5 minuter.' : 'You can leave this page. Processing continues and normally takes about 2–5 minutes.'}</p> : null}
        </div>
      </div>
      {report ? <>
        <HrdmReport report={report} actionId={actionId} />
        <div className="inline-actions"><a className="button" href={`/api/artifact?path=${encodeURIComponent(`output/${actionId}/evidence_use_manifest.json`)}`}>{sv ? 'Visa använda bibliotekskällor' : 'View Library evidence used'}</a></div>
      </> : null}
    </>
  );
}
