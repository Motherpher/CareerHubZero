'use client';

import { useState } from 'react';
import ProcessIndicator from '@/app/_components/ProcessIndicator';
import MotorRunIndicator from '@/app/_components/MotorRunIndicator';

type QueueItem = { id?: string; question?: string; status?: string };
type ActionFeedback = { message?: string; next_step?: string; action_id?: string; user_state?: string; error?: string };

export default function ProfileActions({ queue }: { queue: QueueItem[] }) {
  const [busy, setBusy] = useState('');
  const [feedback, setFeedback] = useState<ActionFeedback | null>(null);
  const [motorActionId, setMotorActionId] = useState('');

  async function act(operation: 'profile_review' | 'profile_rebuild', payload: Record<string, unknown>, key: string) {
    setBusy(key); setFeedback(null); setMotorActionId('');
    try {
      const response = await fetch('/api/action', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ operation, payload }) });
      const data = await response.json().catch(() => ({}));
      setFeedback(response.ok ? data : { ...data, message: data.error ?? data.message ?? 'Profile action could not be registered.' });
      if (response.ok && data.user_state === 'running_in_background' && data.action_id) setMotorActionId(String(data.action_id));
    } catch {
      setFeedback({ message: 'CareerHub could not send the profile request. Try again.' });
    } finally {
      setBusy('');
    }
  }

  return <div className="section-stack">
    <ProcessIndicator active={Boolean(busy)} label="Sending profile request…" detail="CareerHub is registering the evidence review or rebuild with the governed motor." />
    <MotorRunIndicator actionId={motorActionId} />
    <div className="inline-actions">
      <a className="button button--primary" href="/library">Add or update evidence</a>
      <button className="button" type="button" disabled={Boolean(busy)} onClick={() => void act('profile_rebuild', { reason: 'user_requested' }, 'rebuild')}>{busy === 'rebuild' ? 'Requesting…' : 'Rebuild profile from active sources'}</button>
      <a className="button" href="/help">How do profile changes work?</a>
    </div>
    {queue.length ? queue.map((item, index) => {
      const key = String(item.id ?? index);
      return <div className="row" key={key}><div><strong>{item.question ?? 'Verification question'}</strong><div className="muted">{item.status ?? 'open'}</div></div><div className="inline-actions"><a className="button" href="/library">Add evidence</a><button className="button" disabled={Boolean(busy)} type="button" onClick={() => void act('profile_review', { verification_id: item.id ?? key, question: item.question ?? '' }, key)}>{busy === key ? 'Requesting…' : 'Request review'}</button></div></div>;
    }) : <div className="empty-state">No open verification questions.</div>}
    {feedback ? <div className="action-state" role="status"><strong>{feedback.message ?? 'Profile request registered.'}</strong>{feedback.next_step ? <small>{feedback.next_step}</small> : null}{feedback.action_id ? <small>Reference for troubleshooting: {feedback.action_id}</small> : null}</div> : null}
  </div>;
}
