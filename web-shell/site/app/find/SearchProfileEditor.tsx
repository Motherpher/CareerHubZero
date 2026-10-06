'use client';

import { FormEvent, useState } from 'react';
import ProcessIndicator from '@/app/_components/ProcessIndicator';
import MotorRunIndicator from '@/app/_components/MotorRunIndicator';

type Lane = {
  lane_id: string;
  name: string;
  bucket: string;
  priority: number;
  queries?: string[];
};

type ActionFeedback = {
  message?: string;
  next_step?: string;
  action_id?: string;
  user_state?: string;
  error?: string;
};

export default function SearchProfileEditor({
  anchors,
  remoteAllowed,
  engagementTypes,
  savedNeed,
  lanes,
}: {
  anchors: string[];
  remoteAllowed: boolean;
  engagementTypes: string[];
  savedNeed: string;
  lanes: Lane[];
}) {
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<ActionFeedback | null>(null);
  const [motorActionId, setMotorActionId] = useState('');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setFeedback(null);
    setMotorActionId('');
    const form = new FormData(event.currentTarget);
    const laneUpdates = lanes.map((lane) => ({
      lane_id: lane.lane_id,
      name: String(form.get(`lane_name_${lane.lane_id}`) ?? lane.name).trim(),
      queries: String(form.get(`lane_queries_${lane.lane_id}`) ?? '').split(/[,\n]/).map((item) => item.trim()).filter(Boolean),
    }));
    const payload = {
      anchors: String(form.get('anchors') ?? ''),
      remote_allowed: form.get('remote_allowed') === 'on' ? 'true' : 'false',
      engagement_types: String(form.get('engagement_types') ?? ''),
      saved_need: String(form.get('saved_need') ?? ''),
      lanes_json: JSON.stringify(laneUpdates),
    };
    try {
      const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ operation: 'search_profile_update', payload }),
      });
      const data = await response.json().catch(() => ({}));
      setFeedback(response.ok ? data : { ...data, message: data.error ?? data.message ?? 'Search Profile could not be updated.' });
      if (response.ok && data.user_state === 'running_in_background' && data.action_id) setMotorActionId(String(data.action_id));
    } catch {
      setFeedback({ message: 'CareerHub could not send the Search Profile update. Try again.' });
    } finally {
      setBusy(false);
    }
  }

  return <form className="action-form" onSubmit={submit}>
    <ProcessIndicator active={busy} label="Updating your Search Profile…" detail="CareerHub is sending the new defaults to the governed motor." />
    <MotorRunIndicator actionId={motorActionId} />
    <div className="explainer">
      <strong>Changes here become your future search defaults.</strong>
      <p>Use the search runner above when you only want to change one search. Use this editor when you want CareerHub to remember the change next time.</p>
    </div>
    <div className="action-form__grid">
      <label className="field"><span>Geographic anchors</span><input name="anchors" defaultValue={anchors.join(', ')} placeholder="Stockholm, Uppsala" /></label>
      <label className="field field--checkbox"><span>Remote work</span><span><input name="remote_allowed" type="checkbox" defaultChecked={remoteAllowed} /> Allow remote roles</span></label>
      <label className="field field--full"><span>Engagement types</span><textarea name="engagement_types" rows={3} defaultValue={engagementTypes.join(', ')} placeholder="Permanent employment, consulting assignment" /></label>
      <label className="field field--full"><span>Saved search need</span><input name="saved_need" defaultValue={savedNeed} placeholder="Optional persistent search-only preference" /></label>
    </div>

    <div className="lane-editor">
      <div className="explainer">
        <strong>Role lanes are search directions — not claims about you.</strong>
        <p>Rename a lane to make the direction clearer, and change its search terms to broaden or narrow what CareerHub looks for. Bucket and priority stay governed so the search architecture remains coherent.</p>
      </div>
      {lanes.map((lane) => <div className="lane-editor__item" key={lane.lane_id}>
        <div className="lane-editor__head">
          <strong>{lane.name}</strong>
          <span className="lane-editor__meta">{lane.bucket} · priority {lane.priority}</span>
        </div>
        <label className="field"><span>Lane name</span><input name={`lane_name_${lane.lane_id}`} defaultValue={lane.name} /></label>
        <label className="field"><span>Search terms</span><textarea name={`lane_queries_${lane.lane_id}`} rows={3} defaultValue={(lane.queries ?? []).join(', ')} placeholder="journalist, editor, communications coordinator…" /></label>
      </div>)}
    </div>

    <div className="inline-actions"><button className="button button--primary" disabled={busy} type="submit">{busy ? 'Saving…' : 'Save future search defaults'}</button><a className="button" href="/help">What do these settings mean?</a></div>
    <p className="muted">Search preferences change sourcing and ranking only. They do not become candidate evidence or rewrite your Career Profile.</p>
    {feedback ? <div className="action-state" role="status"><strong>{feedback.message ?? 'Search Profile request registered.'}</strong>{feedback.next_step ? <small>{feedback.next_step}</small> : null}{feedback.action_id ? <small>Reference for troubleshooting: {feedback.action_id}</small> : null}</div> : null}
  </form>;
}
