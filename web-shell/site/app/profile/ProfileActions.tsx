'use client';

import { useState } from 'react';

type QueueItem = { id?: string; question?: string; status?: string };

export default function ProfileActions({ queue }: { queue: QueueItem[] }) {
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');

  async function act(operation: 'profile_review' | 'profile_rebuild', payload: Record<string, unknown>, key: string) {
    setBusy(key); setMessage('');
    const response = await fetch('/api/action', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ operation, payload }) });
    const data = await response.json().catch(() => ({}));
    setMessage(response.ok ? `${data.message ?? 'Action registered.'}${data.action_id ? ` Reference: ${data.action_id}` : ''}` : (data.error ?? data.message ?? 'Action could not be registered.'));
    setBusy('');
  }

  return <div className="section-stack">
    <div className="inline-actions">
      <a className="button button--primary" href="/library">Add or update evidence</a>
      <button className="button" type="button" disabled={Boolean(busy)} onClick={() => void act('profile_rebuild', { reason: 'user_requested' }, 'rebuild')}>{busy === 'rebuild' ? 'Requesting…' : 'Request profile rebuild from active sources'}</button>
    </div>
    {queue.length ? queue.map((item, index) => {
      const key = String(item.id ?? index);
      return <div className="row" key={key}><div><strong>{item.question ?? 'Verification question'}</strong><div className="muted">{item.status ?? 'open'}</div></div><div className="inline-actions"><a className="button" href="/library">Add evidence</a><button className="button" disabled={Boolean(busy)} type="button" onClick={() => void act('profile_review', { verification_id: item.id ?? key, question: item.question ?? '' }, key)}>{busy === key ? 'Requesting…' : 'Request review'}</button></div></div>;
    }) : <div className="empty-state">No open verification questions.</div>}
    {message ? <p className="wish-status" role="status">{message}</p> : null}
  </div>;
}
