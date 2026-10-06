'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import HrdmReport from './HrdmReport';

type Job = { id?: string; title?: string; company?: string; url?: string; deadline?: string; lane?: string };
type Lane = { lane_id: string; name: string; bucket: string };
type ProcessState = 'IDLE' | 'PREPARING' | 'WAITING_FOR_EXECUTION' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'BLOCKED';
const STORAGE_KEY = 'careerhub.active.analysis';

export default function AnalyseClient({ jobs, lanes, language = 'en' }: { jobs: Job[]; lanes: Lane[]; language?: string }) {
  const sv = language.toLowerCase().startsWith('sv');
  const [selected, setSelected] = useState('');
  const [message, setMessage] = useState('');
  const [detail, setDetail] = useState('');
  const [state, setState] = useState<ProcessState>('IDLE');
  const [ready, setReady] = useState<boolean | null>(null);
  const [actionId, setActionId] = useState('');
  const [report, setReport] = useState<any>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  function announceProcess(id: string, title: string) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ actionId: id, title: title || (sv ? 'Jobbanalys' : 'Job analysis'), startedAt: new Date().toISOString() }));
      window.dispatchEvent(new Event('careerhub-process-updated'));
    } catch { /* local storage is optional; execution is server-side */ }
  }

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
        setMessage(sv ? 'Analystjänsten är inte tillgänglig för den här CareerHub-sidan ännu.' : 'The analysis service is not available for this CareerHub yet.');
        setDetail(data.detail || 'Execution connection is incomplete.');
        return false;
      }
      if (state === 'BLOCKED') setState('IDLE');
      return true;
    } catch {
      setReady(false);
      setState('BLOCKED');
      setMessage(sv ? 'CareerHub kunde inte kontrollera analystjänsten.' : 'CareerHub could not verify the analysis service.');
      setDetail(sv ? 'Försök igen om en stund.' : 'Try again in a moment.');
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
      setMessage(data.message || (sv ? 'CareerHub kontrollerar analysstatus.' : 'CareerHub is checking analysis status.'));
      setDetail('');
      if (next === 'COMPLETED' && data.hrdm) {
        setReport(data.hrdm);
        window.dispatchEvent(new Event('careerhub-process-updated'));
        return;
      }
      if (next === 'FAILED') {
        window.dispatchEvent(new Event('careerhub-process-updated'));
        return;
      }
      pollTimer.current = setTimeout(() => { void poll(id); }, 4000);
    } catch {
      setMessage(sv ? 'Statusuppdateringen avbröts tillfälligt. Analysen fortsätter i bakgrunden.' : 'Status updates were interrupted temporarily. The analysis continues in the background.');
      pollTimer.current = setTimeout(() => { void poll(id); }, 8000);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(sv ? 'Kontrollerar analystjänsten…' : 'Checking analysis service…');
    setDetail('');
    setReport(null);
    setState('PREPARING');
    if (!(await preflight())) return;

    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(Array.from(form.entries()).map(([key, value]) => [key, String(value)]));
    if (!String(payload.job_url ?? '').trim() && !String(payload.job_text ?? '').trim()) {
      setState('IDLE');
      setMessage(sv ? 'Lägg till en offentlig annonslänk eller klistra in annonstexten.' : 'Add a public job URL or paste the vacancy text before starting.');
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
      setMessage(data.error || data.message || (sv ? 'Jobbanalysen kunde inte startas.' : 'The job analysis could not be started.'));
      setDetail(data.detail || '');
      return;
    }

    setActionId(data.action_id);
    setState('WAITING_FOR_EXECUTION');
    setMessage(sv ? 'Analysen är startad. Du kan lämna sidan – den fortsätter i bakgrunden.' : 'Analysis started. You can leave this page — it continues in the background.');
    setDetail(sv ? 'Normalt tar en rapport cirka 2–5 minuter.' : 'A report normally takes about 2–5 minutes.');
    announceProcess(data.action_id, String(payload.title ?? ''));
    void poll(data.action_id);
  }

  const active = ['PREPARING', 'WAITING_FOR_EXECUTION', 'RUNNING'].includes(state);
  const stateLabel = state === 'IDLE'
    ? (ready === null ? (sv ? 'Kontrollerar' : 'Checking') : ready ? (sv ? 'Redo' : 'Ready') : (sv ? 'Inte tillgänglig' : 'Unavailable'))
    : state === 'WAITING_FOR_EXECUTION' ? (sv ? 'Väntar på start' : 'Waiting to start')
    : state === 'RUNNING' ? (sv ? 'Analys pågår' : 'Analysis running')
    : state === 'COMPLETED' ? (sv ? 'Klar' : 'Complete')
    : state === 'FAILED' ? (sv ? 'Misslyckades' : 'Failed')
    : state === 'BLOCKED' ? (sv ? 'Blockerad' : 'Blocked')
    : (sv ? 'Förbereder' : 'Preparing');

  return (
    <div className="analysis-runner">
      <div className={`process-status process-status--${state.toLowerCase()}`} aria-live="polite">
        <span className={`process-status__dot ${active ? 'process-status__dot--active' : ''}`} aria-hidden="true" />
        <div>
          <strong>{stateLabel}</strong>
          {message ? <p>{message}</p> : null}
          {detail ? <p className="muted technical-detail">{detail}</p> : null}
        </div>
      </div>

      <form ref={formRef} className="action-form" onSubmit={submit}>
        <div className="action-form__grid">
          <label className="field field--full"><span>{sv ? 'Sparat jobb' : 'Saved role'}</span><select value={selected} onChange={(event) => chooseJob(event.target.value, event.currentTarget.form)}><option value="">{sv ? 'Ange ett jobb manuellt' : 'Enter a role manually'}</option>{jobs.map((job, index) => <option key={String(job.id ?? index)} value={String(job.id ?? index)}>{job.title || (sv ? 'Namnlöst jobb' : 'Untitled role')}{job.company ? ` — ${job.company}` : ''}</option>)}</select></label>
          <label className="field field--full"><span>{sv ? 'Länk till jobbannons' : 'Job URL'}</span><input name="job_url" type="url" placeholder="https://…" /></label>
          <label className="field"><span>{sv ? 'Jobbtitel' : 'Role title'}</span><input name="title" /></label>
          <label className="field"><span>{sv ? 'Arbetsgivare' : 'Employer'}</span><input name="company" /></label>
          <label className="field"><span>{sv ? 'Sista ansökningsdag' : 'Deadline'}</span><input name="deadline" type="date" /></label>
          <label className="field"><span>{sv ? 'Sök-/ansökningsspår' : 'Search / application lane'}</span><select name="lane" defaultValue="core">{lanes.length ? lanes.map((lane) => <option key={lane.lane_id} value={lane.bucket}>{lane.name}</option>) : <><option value="core">Core</option><option value="adjacent">Adjacent</option><option value="bridge">Bridge</option></>}</select></label>
          <label className="field field--full"><span>{sv ? 'Klistra in annonstext om länken inte kan läsas' : 'Paste job text when the URL cannot be read'}</span><textarea name="job_text" rows={8} placeholder={sv ? 'Använd detta om annonsen blockerar automatisk läsning.' : 'Use this when the vacancy blocks automated retrieval.'} /></label>
        </div>
        <div className="inline-actions"><button className="button button--primary" disabled={active || ready === false} type="submit">{active ? (sv ? 'Analys pågår…' : 'Analysis running…') : (sv ? 'Analysera jobbannons' : 'Analyse job opening')}</button></div>
        <p className="muted">{sv ? 'Rapporten tar normalt cirka 2–5 minuter. Du kan byta rum eller lämna sidan – processen fortsätter tills den är klar.' : 'The report normally takes about 2–5 minutes. You can change rooms or leave this page — the process continues until it finishes.'}</p>
      </form>

      {actionId && !report ? <p className="muted">{sv ? 'Stabil resultatsida:' : 'Stable result page:'} <a className="text-link" href={`/analyse/${encodeURIComponent(actionId)}`}>{sv ? 'visa analysen' : 'view analysis'}</a>.</p> : null}
      {report ? <HrdmReport report={report} actionId={actionId} /> : null}
    </div>
  );
}
