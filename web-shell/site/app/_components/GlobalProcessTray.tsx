'use client';

import { useEffect, useState } from 'react';

type SavedProcess = { actionId: string; title?: string; startedAt: string };
type ProcessState = 'WAITING_FOR_EXECUTION' | 'RUNNING' | 'COMPLETED' | 'FAILED';
const STORAGE_KEY = 'careerhub.active.analysis';

function readSaved(): SavedProcess | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) as SavedProcess : null;
  } catch { return null; }
}

export default function GlobalProcessTray({ language = 'en' }: { language?: string }) {
  const sv = language.toLowerCase().startsWith('sv');
  const [process, setProcess] = useState<SavedProcess | null>(null);
  const [state, setState] = useState<ProcessState | null>(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const sync = () => setProcess(readSaved());
    sync();
    window.addEventListener('storage', sync);
    window.addEventListener('careerhub-process-updated', sync as EventListener);
    return () => {
      window.removeEventListener('storage', sync);
      window.removeEventListener('careerhub-process-updated', sync as EventListener);
    };
  }, []);

  useEffect(() => {
    if (!process?.actionId) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;
    async function check() {
      try {
        const response = await fetch(`/api/action/status?action_id=${encodeURIComponent(process!.actionId)}`, { cache: 'no-store' });
        const data = await response.json().catch(() => ({}));
        if (cancelled) return;
        const next = (data.state || 'FAILED') as ProcessState;
        setState(next);
        setMessage(data.message || '');
        if (next === 'WAITING_FOR_EXECUTION' || next === 'RUNNING') timer = setTimeout(check, 5000);
      } catch {
        if (!cancelled) timer = setTimeout(check, 8000);
      }
    }
    void check();
    return () => { cancelled = true; if (timer) clearTimeout(timer); };
  }, [process?.actionId]);

  if (!process) return null;
  const active = state === 'WAITING_FOR_EXECUTION' || state === 'RUNNING' || state === null;
  const title = process.title || (sv ? 'Jobbanalys' : 'Job analysis');
  function dismiss() {
    window.localStorage.removeItem(STORAGE_KEY);
    setProcess(null);
  }

  return (
    <aside className={`global-process global-process--${(state ?? 'running').toLowerCase()}`} aria-live="polite">
      <div className="global-process__status">
        <span className={`process-status__dot ${active ? 'process-status__dot--active' : ''}`} aria-hidden="true" />
        <div>
          <strong>{active ? (sv ? 'Analys pågår' : 'Analysis running') : state === 'COMPLETED' ? (sv ? 'Analysen är klar' : 'Analysis complete') : (sv ? 'Analysen behöver uppmärksamhet' : 'Analysis needs attention')}</strong>
          <span>{title}</span>
          {active ? <small>{sv ? 'Du kan fortsätta använda CareerHub. Analysen fortsätter i bakgrunden och tar normalt cirka 2–5 minuter.' : 'You can keep using CareerHub. The analysis continues in the background and normally takes about 2–5 minutes.'}</small> : message ? <small>{message}</small> : null}
        </div>
      </div>
      <div className="global-process__actions">
        <a className="button button--primary" href={`/analyse/${encodeURIComponent(process.actionId)}`}>{state === 'COMPLETED' ? (sv ? 'Öppna rapport' : 'Open report') : (sv ? 'Visa status' : 'View status')}</a>
        {!active ? <button className="button" type="button" onClick={dismiss}>{sv ? 'Stäng' : 'Dismiss'}</button> : null}
      </div>
    </aside>
  );
}
