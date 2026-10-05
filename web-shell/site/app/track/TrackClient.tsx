'use client';

import { FormEvent, useState } from 'react';

type Case = {
  issue_number?: number;
  title?: string;
  role?: string;
  company?: string;
  status?: string;
  priority?: number;
  next_action?: string;
  next_action_date?: string;
};

const STATUSES = ['saved','preparing','ready','applied','contacted','portfolio','interview_1','interview_2','interview_3','interview_4','interview_5','meeting_1','meeting_2','meeting_3','meeting_4','meeting_5','offer','denied','withdrawn','archived'];

async function dispatch(operation: string, payload: Record<string, unknown>) {
  const response = await fetch('/api/action', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ operation, payload }) });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error ?? data.message ?? 'Update could not be sent.');
  return data;
}

export default function TrackClient({ cases }: { cases: Case[] }) {
  const [busy, setBusy] = useState<string>('');
  const [message, setMessage] = useState('');

  async function updateStatus(event: FormEvent<HTMLFormElement>, item: Case) {
    event.preventDefault();
    if (!item.issue_number) return;
    const form = new FormData(event.currentTarget);
    setBusy(String(item.issue_number)); setMessage('');
    try {
      const data = await dispatch('track_status', {
        issue_number: item.issue_number,
        status: String(form.get('status') ?? ''),
        date: String(form.get('date') ?? ''),
        next_action: String(form.get('next_action') ?? ''),
        next_action_date: String(form.get('next_action_date') ?? ''),
      });
      const priority = Number(form.get('priority') ?? item.priority ?? 3);
      if (priority !== Number(item.priority ?? 3)) await dispatch('track_priority', { issue_number: item.issue_number, priority });
      setMessage(`${data.message ?? 'Application updated.'}${data.action_id ? ` Reference: ${data.action_id}` : ''}`);
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Update failed.'); }
    setBusy('');
  }

  if (!cases.length) return <div className="empty-state">The pipeline is empty. Run an HRDM analysis to create the first governed application case.</div>;

  return <div className="section-stack">{cases.map((item, index) => {
    const key = String(item.issue_number ?? index);
    return <article className="track-card" key={key}>
      <div><p className="meta-label">{item.company || 'Employer'}</p><h3>{item.title ?? item.role ?? `Application ${index + 1}`}</h3></div>
      {item.issue_number ? <form className="action-form action-form--compact" onSubmit={(event) => void updateStatus(event, item)}>
        <div className="action-form__grid">
          <label className="field"><span>Status</span><select name="status" defaultValue={item.status ?? 'saved'}>{STATUSES.map((status) => <option key={status} value={status}>{status.replaceAll('_',' ')}</option>)}</select></label>
          <label className="field"><span>Priority</span><select name="priority" defaultValue={String(item.priority ?? 3)}>{[1,2,3,4,5].map((value) => <option value={value} key={value}>{value}</option>)}</select></label>
          <label className="field"><span>Event date</span><input name="date" type="date" /></label>
          <label className="field"><span>Next action date</span><input name="next_action_date" type="date" defaultValue={(item.next_action_date ?? '').slice(0,10)} /></label>
          <label className="field field--full"><span>Next action</span><input name="next_action" defaultValue={item.next_action ?? ''} /></label>
        </div>
        <button className="button button--primary" disabled={busy === key} type="submit">{busy === key ? 'Updating…' : 'Update application'}</button>
      </form> : <p className="muted">This historic item has no motor case identifier and cannot be updated until it is re-registered.</p>}
    </article>;
  })}{message ? <p className="wish-status" role="status">{message}</p> : null}</div>;
}
