'use client';

import { useEffect, useRef, useState } from 'react';
import HrdmReport from '../HrdmReport';

type ProcessState = 'WAITING_FOR_EXECUTION' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export default function AnalysisResultClient({ actionId }: { actionId: string }) {
  const [state, setState] = useState<ProcessState>('WAITING_FOR_EXECUTION');
  const [message, setMessage] = useState('Loading analysis state…');
  const [report, setReport] = useState<any>(null);
  const [runUrl, setRunUrl] = useState('');
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await fetch(`/api/action/status?action_id=${encodeURIComponent(actionId)}`, { cache: 'no-store' });
        const data = await response.json().catch(() => ({}));
        const next = (data.state || 'FAILED') as ProcessState;
        setState(next);
        setMessage(data.message || 'CareerHub is checking this analysis.');
        setRunUrl(data.run_url || '');
        if (next === 'COMPLETED' && data.hrdm) {
          setReport(data.hrdm);
          return;
        }
        if (next !== 'FAILED') timer.current = setTimeout(load, 2500);
      } catch {
        setState('FAILED');
        setMessage('CareerHub could not retrieve this analysis state.');
      }
    }
    void load();
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [actionId]);

  const active = state === 'WAITING_FOR_EXECUTION' || state === 'RUNNING';
  return (
    <>
      <div className={`process-status process-status--${state.toLowerCase()}`} aria-live="polite">
        <span className={`process-status__dot ${active ? 'process-status__dot--active' : ''}`} aria-hidden="true" />
        <div>
          <strong>{state.replaceAll('_', ' ')}</strong>
          <p>{message}</p>
          <p className="muted technical-detail">Technical reference: {actionId}{runUrl ? ` · ${runUrl}` : ''}</p>
        </div>
      </div>
      {report ? <HrdmReport report={report} actionId={actionId} /> : null}
    </>
  );
}
