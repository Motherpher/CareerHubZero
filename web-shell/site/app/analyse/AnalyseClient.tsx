'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import HrdmReport from './HrdmReport';

type Job = { id?: string; title?: string; company?: string; url?: string; deadline?: string; lane?: string };
type Lane = { lane_id: string; name: string; bucket: string };
type ProcessState = 'IDLE' | 'PREPARING' | 'WAITING_FOR_EXECUTION' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'BLOCKED';

export default function AnalyseClient({ jobs, lanes }: { jobs: Job[]; lanes: Lane[] }) {
  const [selected, setSelected] = useState('');
  const [message, setMessage] = useState('');
  const [detail, setDetail] = useState('');
  const [state, setState] = useState<ProcessState>('IDLE');
  const [ready, setReady] = useState<boolean | null>(null);
  const [actionId, setActionId] = useState('');
  const [report, setReport] = useState<any>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  function setField(name: string, value: string, form = formRef.current) {
    if (!form) return;
    const input = form.elements.namedItem(name) as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | null;
    if (input) input.value = value;
  }

  async function preflight() {
    try {
      const response = await fetch('/api/action', { cache: 'no-store' });
      const data = await response.json().catch(() => ({}));
      setReady(Boolean(response.ok && data.ready));
      if (!response.ok || !data.ready) {
        setState('BLOCKED');
        setMessage(data.message || 'CareerHub Motor execution is not available from this deployment yet.');
        setDetail(data.detail || 'Execution preflight did not pass.');
        return false;
      }
      if (state === 'BLOCKED') setState('IDLE');
      return true;
    } catch {
      setReady(false);
      setState('BLOCKED');
      setMessage('CareerHub could not verify the Motor connection.');
      setDetail('Execution preflight failed before the analysis was submitted.');
      return false;
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setField('job_url', params.get('job_url') ?? '');
    setField('title', params.get('title') ?? '');
    setField('company', params.get('company') ?? '');
    setField('deadline', (params.get('deadline') ?? '').slice(0, 10));
    const bucket = params.get('lane');
    if (bucket && ['core', 'adjacent', 'bridge'].includes(bucket)) setField('lane', bucket);
    void preflight();
    return () => { if (pollTimer.current) clearTimeout(pollTimer.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function chooseJob(value: string, form: HTMLFormElement | null) {
    setSelected(value);
    if (!form || !value) return;
    const job = jobs.find((item, index) => String(item.id ?? index) === value);
    if (!job) return;
    setField('job_url', job.url ?? '', form);
    setField('title', job.title ?? '', form);
    setField('company', job.company ?? '', form);
    setField('deadline', (job.deadline ?? '').slice(0, 10), form);
    if (job.lane && ['core', 'adjacent', 'bridge'].includes(job.lane)) setField('lane', job.lane, form);
  }

  async function poll(id: string) {
    try {
      const response = await fetch(`/api/action/status?action_id=${encodeURIComponent(id)}`, { cache: 'no-store' });
      const data = await response.json().catch(() => ({}));
      const next = (data.state || 'FAILED') as ProcessState;
      setState(next);
      setMessage(data.message || 'CareerHub is checking the Motor state.');
      setDetail(data.run_url ? `Technical execution: ${data.run_url}` : '');
      if (next === 'COMPLETED' && data.hrdm) {
        setReport(data.hrdm);
        return;
      }
      if (next === 'FAILED') return;
      pollTimer.current = setTimeout(() => { void poll(id); }, 2500);
    } catch {
      setState('FAILED');
      setMessage('CareerHub lost contact with the execution status endpoint.');
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('Checking Motor readiness…');
    setDetail('');
    setReport(null);
    setState('PREPARING');
    if (!(await preflight())) return;

    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(Array.from(form.entries()).map(([key, value]) => [key, String(value)]));
    if (!String(payload.job_url ?? '').trim() && !String(payload.job_text ?? '').trim()) {
      setState('IDLE');
      setMessage('Add a public job URL or paste the vacancy text before starting HRDM-R.');
      return;
    }

    const response = await fetch('/api/action', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ operation: 'analyse_role', payload }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.action_id) {
      setState('FAILED');
      setMessage(data.error || data.message || 'The HRDM-R analysis could not be started.');
      setDetail(data.detail || '');
      return;
    }

    setActionId(data.action_id);
    setState('WAITING_FOR_EXECUTION');
    setMessage(data.message || 'The action was accepted and is waiting for the Motor.');
    setDetail(`Technical reference: ${data.action_id}`);
    void poll(data.action_id);
  }

  const active = ['PREPARING', 'WAITING_FOR_EXECUTION', 'RUNNING'].includes(state);

  return (
    <div className="analysis-runner">
      <div className={`process-status process-status--${state.toLowerCase()}`} aria-live="polite">
        <span className={`process-status__dot ${active ? 'process-status__dot--active' : ''}`} aria-hidden="true" />
        <div>
          <strong>{state === 'IDLE' ? (ready === null ? 'Checking Motor' : ready ? 'Motor ready' : 'Motor unavailable') : state.replaceAll('_', ' ')}</strong>
          {message ? <p>{message}</p> : null}
          {detail ? <p className="muted technical-detail">{detail}</p> : null}
        </div>
      </div>

      <form ref={formRef} className="action-form" onSubmit={submit}>
        <div className="action-form__grid">
          <label className="field field--full"><span>Saved role</span><select value={selected} onChange={(event) => chooseJob(event.target.value, event.currentTarget.form)}><option value="">Enter a role manually</option>{jobs.map((job, index) => <option key={String(job.id ?? index)} value={String(job.id ?? index)}>{job.title || 'Untitled role'}{job.company ? ` — ${job.company}` : ''}</option>)}</select></label>
          <label className="field field--full"><span>Job URL</span><input name="job_url" type="url" placeholder="https://…" /></label>
          <label className="field"><span>Role title</span><input name="title" /></label>
          <label className="field"><span>Employer</span><input name="company" /></label>
          <label className="field"><span>Deadline</span><input name="deadline" type="date" /></label>
          <label className="field"><span>Search / application lane</span><select name="lane" defaultValue="core">{lanes.length ? lanes.map((lane) => <option key={lane.lane_id} value={lane.bucket}>{lane.name}</option>) : <><option value="core">Core</option><option value="adjacent">Adjacent</option><option value="bridge">Bridge</option></>}</select></label>
          <label className="field field--full"><span>Paste job text when the URL cannot be read</span><textarea name="job_text" rows={8} placeholder="Use this when the vacancy blocks automated retrieval, or when you want to analyse pasted vacancy text directly." /></label>
        </div>
        <div className="inline-actions"><button className="button button--primary" disabled={active || ready === false} type="submit">{active ? 'Motor working…' : 'Run HRDM-R and prepare application'}</button></div>
        <p className="muted">Hybridianesque is evaluated automatically inside HRDM-R. When relevant, the report explains why it was activated, what structural work it performs and what it changes in the role interpretation.</p>
      </form>

      {actionId && !report ? <p className="muted">You can reopen this run at <a className="text-link" href={`/analyse/${encodeURIComponent(actionId)}`}>its stable analysis page</a>.</p> : null}
      {report ? <HrdmReport report={report} actionId={actionId} /> : null}
    </div>
  );
}
