'use client';

import { FormEvent, useState } from 'react';
import ProcessIndicator from '@/app/_components/ProcessIndicator';
import MotorRunIndicator from '@/app/_components/MotorRunIndicator';

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

type ActionFeedback = { message?: string; next_step?: string; action_id?: string; user_state?: string; error?: string };

const STATUSES = ['saved','preparing','ready','applied','contacted','portfolio','interview_1','interview_2','interview_3','interview_4','interview_5','meeting_1','meeting_2','meeting_3','meeting_4','meeting_5','offer','denied','withdrawn','archived'];

async function dispatch(operation: string, payload: Record<string, unknown>) {
  const response = await fetch('/api/action', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ operation, payload }) });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error ?? data.message ?? 'Update could not be sent.');
  return data;
}

export default function TrackClient({ cases }: { cases: Case[] }) {
  const [busy, setBusy] = useState<string>('');
  const [feedback, setFeedback] = useState<ActionFeedback | null>(null);
  const [motorActionId, setMotorActionId] = useState('');

  async function updateStatus(event: FormEvent<HTMLFormElement>, item: Case) {
    event.preventDefault();
    if (!item.issue_number) return;
    const form = new FormData(event.currentTarget);
    setBusy(String(item.issue_number)); setFeedback(null); setMotorActionId('');
    try {
      let data = await dispatch('track_status', {
        issue_number: item.issue_number,
        status: String(form.get('status') ?? ''),
        date: String(form.get('date') ?? ''),
        next_action: String(form.get('next_action') ?? ''),
        next_action_date: String(form.get('next_action_date') ?? ''),
      });
      const priority = Number(form.get('priority') ?? item.priority ?? 3);
      if (priority !== Number(item.priority ?? 3)) data = await dispatch('track_priority', { issue_number: item.issue_number, priority });
      setFeedback(data);
      if (data.user_state === 'running_in_background' && data.action_id) setMotorActionId(String(data.action_id));
    } catch (error) { setFeedback({ message: error instanceof Error ? error.message : 'Update failed.' }); }
    setBusy('');
  }

  if (!cases.length) return <div className="empty-state">The pipeline is empty. Run an HRDM analysis to create the first governed application case.</div>;

  return <div className="section-stack">
    <ProcessIndicator active={Boolean(busy)} label="Updating application…" detail="CareerHub is sending the new status, priority or next action to the governed motor." />
    <MotorRunIndicator actionId={motorActionId} />
    <div className="explainer"><strong>Keep Track current.</strong><p>Status tells CareerHub where the application is. Priority tells it how much attention the case needs. “Next action” records the concrete thing you plan to do next.</p></div>
    {cases.map((item, index) => {
      const key = String(item.issue_number ?? index);
      return <article className="track-card" key={key}>
        <div><p className="meta-label">{item.company || 'Employer'}</p><h3>{item.title ?? item.role ?? `Application ${index + 1}`}</h3></div>
        {item.issue_number ? <form className="action-form action-form--compact" onSubmit={(event) => void updateStatus(event, item)}>
          <div className="action-form__grid">
            <label className="field"><span>Status</span><select name="status" defaultValue={item.status ?? 'saved'}>{STATUSES.map((status) => <option key={status} value={status}>{status.replaceAll('_',' ')}</option>)}</select></label>
            <label className="field"><span>Priority</span><select name="priority" defaultValue={String(item.priority ?? 3)}>{[1,2,3,4,5].map((value) => <option value={value} key={value}>{value}</option>)}</select></label>
            <label className="field"><span>Event date</span><input name="date" type="date" /></label>
            <label className="field"><span>Next action date</span><input name="next_action_date" type="date" defaultValue={(item.next_action_date ?? '').slice(0,10)} /></label>
            <label className="field field--full"><span>Next action</span><input name="next_action" defaultValue={item.next_action ?? ''} placeholder="e.g. Send follow-up email" /></label>
          </div>
          <button className="button button--primary" disabled={busy === key} type="submit">{busy === key ? 'Updating…' : 'Update application'}</button>
        </form> : <p className="muted">This historic item has no motor case identifier and cannot be updated until it is re-registered.</p>}
      </article>;
    })}
    {feedback ? <div className="action-state" role="status"><strong>{feedback.message ?? 'Application update registered.'}</strong>{feedback.next_step ? <small>{feedback.next_step}</small> : null}{feedback.action_id ? <small>Reference for troubleshooting: {feedback.action_id}</small> : null}</div> : null}
  </div>;
}
