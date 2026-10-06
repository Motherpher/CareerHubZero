'use client';

import { useMemo, useState } from 'react';

type Lane = { lane_id?: string; name?: string; bucket?: string; priority?: number; queries?: string[] };

const help = [
  ['What is the CareerHub Motor?', 'The Motor is the governed runtime behind Search, Analyse, Apply and Track. It uses the active verified profile as evidence and keeps search-only wishes separate from candidate facts.'],
  ['What is HRDM-R?', 'HRDM-R is the reverse role-analysis sequence. It reconstructs signals, hidden need, field logic, FunctionCore, DoD, assessment zones, candidate positioning and HCC commentary before application positioning.'],
  ['What is Hybridianesque?', 'Hybridianesque is an enclosed structural depth filter inside HRDM-R. CareerHub evaluates it automatically and activates it only when the role shows evidenced plural logics, structural asymmetry, constitutive translation and process-to-output movement.'],
  ['Why did my search show no new roles?', 'A successful repeated search is compared with the previous comparable run. If nothing unseen or changed appears, CareerHub says that explicitly. Source failures are shown separately and are never reported as zero new roles.'],
  ['What is a Search Lane?', 'A Search Lane is one part of the active search strategy, such as a core, adjacent or bridge direction. Lanes govern query families; they do not become candidate evidence.'],
  ['What does the red status dot mean?', 'The blinking red dot appears only while an active Motor process is preparing, waiting for execution or running. When the process finishes or fails, the dot stops.'],
  ['What is an ACT reference?', 'ACT-* is the technical identity of one Motor action. It is secondary audit information and gives a stable reference for execution and report retrieval.'],
];

export default function MotorGuide({ profileName, lanes }: { profileName: string; lanes: Lane[] }) {
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return help;
    return help.filter(([question, answer]) => `${question} ${answer}`.toLowerCase().includes(q));
  }, [query]);

  return (
    <section className="motor-guide" aria-labelledby="motor-heading">
      <div className="motor-guide__head">
        <div>
          <p className="eyebrow">CareerHub Motor</p>
          <h2 id="motor-heading">One governed workflow, visible from search to outcome</h2>
        </div>
        <div className="motor-current">
          <span className="meta-label">Current profile</span>
          <strong>{profileName}</strong>
          <a className="text-link" href="/profile">Review / change profile</a>
        </div>
      </div>

      <ol className="motor-flow">
        <li><span>1</span><strong>Profile</strong><small>Verified career evidence defines what CareerHub may claim.</small></li>
        <li><span>2</span><strong>Search</strong><small>Lanes and optional wishes create the active query plan.</small></li>
        <li><span>3</span><strong>Analyse</strong><small>HRDM-R interprets the role before positioning decisions.</small></li>
        <li><span>4</span><strong>Apply</strong><small>Application material is bounded by verified evidence.</small></li>
        <li><span>5</span><strong>Track</strong><small>Application state and outcomes are recorded.</small></li>
        <li><span>6</span><strong>Learn</strong><small>Outcomes can change search hypotheses, never rewrite candidate facts.</small></li>
      </ol>

      <div className="motor-guide__lanes">
        <div>
          <p className="meta-label">Active search lanes</p>
          <div className="tag-row">{lanes.length ? lanes.map((lane, index) => <span className="tag" key={lane.lane_id ?? index}>{lane.name || lane.bucket || `Lane ${index + 1}`}</span>) : <span className="muted">No lanes configured.</span>}</div>
        </div>
        <a className="button" href="/find">Open / change search settings</a>
      </div>

      <div className="motor-help">
        <label className="field field--full"><span>Search CareerHub help</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="HRDM-R, Hybridianesque, search lanes, status…" /></label>
        <div className="help-results">{filtered.map(([question, answer]) => <details key={question}><summary>{question}</summary><p>{answer}</p></details>)}</div>
      </div>
    </section>
  );
}
