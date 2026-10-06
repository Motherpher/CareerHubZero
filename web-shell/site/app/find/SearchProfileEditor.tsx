'use client';

import { FormEvent, useState } from 'react';

type Props = {
  anchors: string[];
  remoteAllowed: boolean;
  engagementTypes: string[];
  savedNeed: string;
  language?: string;
};

export default function SearchProfileEditor({ anchors, remoteAllowed, engagementTypes, savedNeed, language = 'en' }: Props) {
  const sv = language.toLowerCase().startsWith('sv');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage('');
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
    const okFallback = sv ? 'Sökinställningarna har skickats för uppdatering.' : 'Search Profile update sent.';
    const failFallback = sv ? 'Sökinställningarna kunde inte uppdateras.' : 'Search Profile could not be updated.';
    setMessage(response.ok ? `${data.message ?? okFallback}${data.action_id ? ` · ${sv ? 'Referens' : 'Reference'}: ${data.action_id}` : ''}` : (data.error ?? data.message ?? failFallback));
    setBusy(false);
  }

  return (
    <form className="action-form" onSubmit={submit}>
      <div className="action-form__grid">
        <label className="field">
          <span>{sv ? 'Geografiska områden' : 'Geographic anchors'}</span>
          <input name="anchors" defaultValue={anchors.join(', ')} placeholder="Stockholm, Uppsala" />
        </label>
        <label className="field field--checkbox">
          <span>{sv ? 'Distansarbete' : 'Remote work'}</span>
          <span><input name="remote_allowed" type="checkbox" defaultChecked={remoteAllowed} /> {sv ? 'Ta med distansroller' : 'Allow remote roles'}</span>
        </label>
        <label className="field field--full">
          <span>{sv ? 'Anställnings- och uppdragstyper' : 'Engagement types'}</span>
          <textarea name="engagement_types" rows={3} defaultValue={engagementTypes.join(', ')} placeholder={sv ? 'Tillsvidareanställning, konsultuppdrag' : 'Permanent employment, consulting assignment'} />
        </label>
        <label className="field field--full">
          <span>{sv ? 'Sparad sökpreferens' : 'Saved search preference'}</span>
          <input name="saved_need" defaultValue={savedNeed} placeholder={sv ? 'Valfritt – återkommande önskemål som endast ska påverka sökning' : 'Optional persistent search-only preference'} />
        </label>
      </div>
      <div className="inline-actions">
        <button className="button button--primary" disabled={busy} type="submit">
          {busy ? (sv ? 'Sparar…' : 'Saving…') : (sv ? 'Spara sökinställningar' : 'Save Search Profile defaults')}
        </button>
      </div>
      <p className="muted">
        {sv
          ? 'Dessa inställningar styr framtida sökningar. De är sökdata och får aldrig bli kandidatfakta eller ändra den verifierade karriärprofilen.'
          : 'These settings affect future searches only. They are search data and never become candidate evidence or alter the verified career profile.'}
      </p>
      {message ? <p className="wish-status" role="status">{message}</p> : null}
    </form>
  );
}
