'use client';

import { FormEvent, useState } from 'react';

type Job = { id?: string; title?: string; company?: string; url?: string; deadline?: string; lane?: string };
type Lane = { lane_id: string; name: string; bucket: string };

export default function AnalyseClient({ jobs, lanes }: { jobs: Job[]; lanes: Lane[] }) {
  const [selected, setSelected] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  function chooseJob(value: string, form: HTMLFormElement | null) {
    setSelected(value);
    if (!form || !value) return;
    const job = jobs.find((item, index) => String(item.id ?? index) === value);
    if (!job) return;
    const set = (name: string, value: string) => {
      const input = form.elements.namedItem(name) as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | null;
      if (input) input.value = value;
    };
    set('job_url', job.url ?? '');
    set('title', job.title ?? '');
    set('company', job.company ?? '');
    set('deadline', (job.deadline ?? '').slice(0, 10));
    if (job.lane) set('lane', job.lane);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setMessage('');
    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(Array.from(form.entries()).map(([key, value]) => [key, String(value)]));
    const response = await fetch('/api/action', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ operation: 'analyse_role', payload }),
    });
    const data = await response.json().catch(() => ({}));
    setMessage(response.ok ? `${data.message ?? 'Analysis started.'}${data.action_id ? ` Reference: ${data.action_id}` : ''}` : (data.error ?? data.message ?? 'Analysis could not be started.'));
    setBusy(false);
  }

  return (
    <form className="action-form" onSubmit={submit}>
      <div className="action-form__grid">
        <label className="field field--full"><span>Saved role</span><select value={selected} onChange={(event) => chooseJob(event.target.value, event.currentTarget.form)}><option value="">Enter a role manually</option>{jobs.map((job, index) => <option key={String(job.id ?? index)} value={String(job.id ?? index)}>{job.title || 'Untitled role'}{job.company ? ` — ${job.company}` : ''}</option>)}</select></label>
        <label className="field field--full"><span>Job URL</span><input name="job_url" type="url" placeholder="https://…" /></label>
        <label className="field"><span>Role title</span><input name="title" /></label>
        <label className="field"><span>Employer</span><input name="company" /></label>
        <label className="field"><span>Deadline</span><input name="deadline" type="date" /></label>
        <label className="field"><span>Search / application lane</span><select name="lane" defaultValue="core"><option value="core">Core</option><option value="adjacent">Adjacent</option><option value="bridge">Bridge</option>{lanes.filter((lane) => !['core','adjacent','bridge'].includes(lane.bucket)).map((lane) => <option key={lane.lane_id} value={lane.lane_id}>{lane.name}</option>)}</select></label>
        <label className="field"><span>Hybridianesque filter</span><select name="hy_filter" defaultValue="No"><option value="No">No</option><option value="Yes">Yes</option></select></label>
        <label className="field field--full"><span>Paste job text when the URL cannot be read</span><textarea name="job_text" rows={8} placeholder="Optional. Use this when the vacancy blocks automated retrieval." /></label>
      </div>
      <div className="inline-actions"><button className="button button--primary" disabled={busy} type="submit">{busy ? 'Starting analysis…' : 'Run HRDM-R and prepare application'}</button></div>
      <p className="muted">The role analysis and application package are one governed run. The active verified profile remains the evidence boundary.</p>
      {message ? <p className="wish-status" role="status">{message}</p> : null}
    </form>
  );
}
