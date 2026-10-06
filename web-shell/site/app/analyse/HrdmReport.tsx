type Hrdm = Record<string, any>;

function Value({ value }: { value: any }) {
  if (value === null || value === undefined || value === '') return <p className="muted">Not stated.</p>;
  if (Array.isArray(value)) {
    if (!value.length) return <p className="muted">No items recorded.</p>;
    return <ul>{value.map((item, index) => <li key={index}>{typeof item === 'object' ? <Value value={item} /> : String(item)}</li>)}</ul>;
  }
  if (typeof value === 'object') {
    return (
      <dl className="definition-list">
        {Object.entries(value).map(([key, item]) => (
          <div className="definition-pair" key={key}>
            <dt>{key.replaceAll('_', ' ')}</dt>
            <dd><Value value={item} /></dd>
          </div>
        ))}
      </dl>
    );
  }
  return <span>{String(value)}</span>;
}

function Section({ title, value }: { title: string; value: any }) {
  return (
    <section className="report-section">
      <h3>{title}</h3>
      <Value value={value} />
    </section>
  );
}

export default function HrdmReport({ report, actionId }: { report: Hrdm; actionId?: string }) {
  const job = report?.job ?? {};
  const hy = report?.hybridianesque ?? {};
  const active = hy.status === 'active' || hy.activated === true;
  return (
    <article className="hrdm-report">
      <header className="hrdm-report__header">
        <div>
          <p className="meta-label">HRDM-R result</p>
          <h2>{job.title || 'Role analysis'}</h2>
          <p className="muted">{job.company || 'Employer not stated'}{job.location ? ` · ${job.location}` : ''}</p>
        </div>
        <div className="trace-chip">{report.process_id || report.trace?.process_id || actionId || 'Process'}</div>
      </header>

      <Section title="1. Signals" value={report.signals} />
      <Section title="2. Key words & concepts" value={report.concept_clusters} />
      <Section title="3. Hidden need reconstruction" value={report.hidden_need} />
      <Section title="4. Field logic reconstruction" value={report.field_logic} />
      <Section title="5. FunctionCore estimation" value={report.function_core} />
      <Section title="6A. DoD diagnostic" value={report.dod} />
      <Section title="7. Likely assessment zones" value={report.assessment_zones} />
      <Section title="8. Candidate positioning map" value={report.candidate_positioning} />

      <section className={`report-section hybrid-statement ${active ? 'hybrid-statement--active' : ''}`}>
        <p className="meta-label">Hybridianesque relevance statement</p>
        <h3>{active ? 'Activated automatically' : 'Evaluated — not activated'}</h3>
        <p>{hy.activation_rationale || hy.why || (active
          ? 'The role met the evidence threshold for multi-logic structural interpretation.'
          : 'The role did not meet the evidence threshold for Hybridianesque activation.')}</p>
        <dl className="definition-list">
          <div className="definition-pair"><dt>Why relevant</dt><dd><Value value={hy.criteria} /></dd></div>
          <div className="definition-pair"><dt>What it does here</dt><dd>{active ? 'Separates the role’s participating logics, structural asymmetries, translation work and movement from process into usable output.' : 'No deep interpretation was applied because the threshold was not met.'}</dd></div>
          {active ? <>
            <div className="definition-pair"><dt>What it found</dt><dd><Value value={{ participating_logics: hy.participating_logics, asymmetries: hy.asymmetries, translation_relations: hy.translation_relations, process_to_output: hy.process_to_output }} /></dd></div>
            <div className="definition-pair"><dt>Result for interpretation</dt><dd>{hy.framing_if_active || 'See the structural findings above.'}</dd></div>
            <div className="definition-pair"><dt>Risk / safeguard scan</dt><dd><Value value={{ overload_or_misframing: hy.overload_or_misframing, failure_modes: hy.failure_modes, risk_remaining: hy.risk_remaining }} /></dd></div>
          </> : null}
          <div className="definition-pair"><dt>Confidence</dt><dd>{hy.confidence || 'Not stated'}</dd></div>
        </dl>
      </section>

      <Section title="9. HCC reverse commentary" value={report.hcc} />
      <Section title="Application strategy" value={report.application_strategy} />
      <details className="report-trace"><summary>Process trace</summary><Value value={report.trace} /></details>
    </article>
  );
}
