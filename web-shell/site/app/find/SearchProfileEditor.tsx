'use client';

import { FormEvent, useState } from 'react';

export default function SearchProfileEditor({ anchors, remoteAllowed, engagementTypes, savedNeed }: { anchors: string[]; remoteAllowed: boolean; engagementTypes: string[]; savedNeed: string }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setMessage('');
    const form = new FormData(event.currentTarget);
    const payload = {
      anchors: String(form.get('anchors') ?? ''),
      remote_allowed: form.get('remote_allowed') === 'on' ? 'true' : 'false',
      engagement_types: String(form.get('engagement_types') ?? ''),
      saved_need: String(form.get('saved_need') ?? ''),
    };
    const response = await fetch('/api/action', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ operation: 'search_profile_update', payload }),
    });
    const data = await response.json().catch(() => ({}));
    setMessage(response.ok ? `${data.message ?? 'Search Profile update sent.'}${data.action_id ? ` Reference: ${data.action_id}` : ''}` : (data.error ?? data.message ?? 'Search Profile could not be updated.'));
    setBusy(false);
  }

  return <form className="action-form" onSubmit={submit}>
    <div className="action-form__grid">
      <label className="field"><span>Geographic anchors</span><input name="anchors" defaultValue={anchors.join(', ')} placeholder="Stockholm, Uppsala" /></label>
      <label className="field field--checkbox"><span>Remote work</span><span><input name="remote_allowed" type="checkbox" defaultChecked={remoteAllowed} /> Allow remote roles</span></label>
      <label className="field field--full"><span>Engagement types</span><textarea name="engagement_types" rows={3} defaultValue={engagementTypes.join(', ')} placeholder="Permanent employment, consulting assignment" /></label>
      <label className="field field--full"><span>Saved search need</span><input name="saved_need" defaultValue={savedNeed} placeholder="Optional persistent search-only preference" /></label>
    </div>
    <div className="inline-actions"><button className="button button--primary" disabled={busy} type="submit">{busy ? 'Saving…' : 'Save Search Profile defaults'}</button></div>
    <p className="muted">These settings affect future searches only. They do not become candidate evidence.</p>
    {message ? <p className="wish-status" role="status">{message}</p> : null}
  </form>;
}
