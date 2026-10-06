'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import ProcessIndicator from '@/app/_components/ProcessIndicator';
import MotorRunIndicator from '@/app/_components/MotorRunIndicator';

type Job = { id?: string; title?: string; company?: string; url?: string; deadline?: string; lane?: string };
type Lane = { lane_id: string; name: string; bucket: string };
type ActionFeedback = { message?: string; next_step?: string; action_id?: string; user_state?: string; error?: string };

export default function AnalyseClient({ jobs, lanes }: { jobs: Job[]; lanes: Lane[] }) {
  const [selected, setSelected] = useState('');
  const [feedback, setFeedback] = useState<ActionFeedback | null>(null);
  const [busy, setBusy] = useState(false);
  const [motorActionId, setMotorActionId] = useState('');
  const formRef = useRef<HTMLFormElement>(null);

  function setField(name: string, value: string, form = formRef.current) {
    if (!form) return;
    const input = form.elements.namedItem(name) as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | null;
    if (input) input.value = value;
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setField('job_url', params.get('job_url') ?? '');
    setField('title', params.get('title') ?? '');
    setField('company', params.get('company') ?? '');
    setField('deadline', (params.get('deadline') ?? '').slice(0, 10));
    const bucket = params.get('lane');
    if (bucket && ['core', 'adjacent', 'bridge'].includes(bucket)) setField('lane', bucket);
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

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback(null);
    setMotorActionId('');
    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(Array.from(form.entries()).map(([key, value]) => [key, String(value)]));
    if (!String(payload.job_url ?? '').trim() && !String(payload.job_text ?? '').trim()) {
      setFeedback({ message: 'Add a public job URL or paste the vacancy text before starting HRDM-R.' });
      return;
    }
    setBusy(true);
    try {
      const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ operation: 'analyse_role', payload }),
      });
      const data = await response.json().catch(() => ({}));
      setFeedback(response.ok ? data : { ...data, message: data.error ?? data.message ?? 'Analysis could not be started.' });
      if (response.ok && data.user_state === 'running_in_background' && data.action_id) setMotorActionId(String(data.action_id));
    } catch {
      setFeedback({ message: 'CareerHub could not send the analysis request. Try again.' });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form ref={formRef} className="action-form" onSubmit={submit}>
      <ProcessIndicator active={busy} label="Starting HRDM-R…" detail="CareerHub is validating the role and handing the request to the governed analysis path." />
      <MotorRunIndicator actionId={motorActionId} />
      <div className="explainer">
        <strong>What happens when you run HRDM-R?</strong>
        <p>CareerHub analyses this role against the active verified profile, then prepares the governed application package. Search preferences can guide sourcing, but they are not treated as evidence about you.</p>
      </div>
      <div className="action-form__grid">
        <label className="field field--full"><span>Saved role</span><select value={selected} onChange={(event) => chooseJob(event.target.value, event.currentTarget.form)}><option value="">Enter a role manually</option>{jobs.map((job, index) => <option key={String(job.id ?? index)} value={String(job.id ?? index)}>{job.title || 'Untitled role'}{job.company ? ` — ${job.company}` : ''}</option>)}</select></label>
        <label className="field field--full"><span>Job URL</span><input name="job_url" type="url" placeholder="https://…" /></label>
        <label className="field"><span>Role title</span><input name="title" /></label>
        <label className="field"><span>Employer</span><input name="company" /></label>
        <label className="field"><span>Deadline</span><input name="deadline" type="date" /></label>
        <label className="field"><span>Search / application lane</span><select name="lane" defaultValue="core"><option value="core">Core</option><option value="adjacent">Adjacent</option><option value="bridge">Bridge</option></select></label>
        <label className="field"><span>Hybridianesque filter</span><select name="hy_filter" defaultValue="No"><option value="No">No</option><option value="Yes">Yes</option></select></label>
        <label className="field field--full"><span>Paste job text when the URL cannot be read</span><textarea name="job_text" rows={8} placeholder="Use this when the vacancy blocks automated retrieval, or when you want to analyse pasted vacancy text directly." /></label>
      </div>
      <div className="inline-actions"><button className="button button--primary" disabled={busy} type="submit">{busy ? 'Starting analysis…' : 'Run HRDM-R and prepare application'}</button><a className="button" href="/help">Explain HRDM-R</a></div>
      <p className="muted">Provide either the public vacancy URL or pasted vacancy text. The role analysis and application package are one governed run, bounded by the active verified profile.</p>
      {feedback ? <div className="action-state" role="status"><strong>{feedback.message ?? 'Analysis request registered.'}</strong>{feedback.next_step ? <small>{feedback.next_step}</small> : null}{feedback.action_id ? <small>Reference for troubleshooting: {feedback.action_id}</small> : null}</div> : null}
    </form>
  );
}
