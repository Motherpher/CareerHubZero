# HRDM-R v6.3 — CareerHub implementation

HRDM = **HR-Depth Module**.

CareerHub uses the canonical Reverse Mode to reconstruct what a job ad is actually asking for and then position the candidate against that reconstructed role.

## Canonical sequence

1. **Ad/Text Intake**
2. **Signal Extraction**
3. **Key Words & Concepts**
4. **Hidden Need Reconstruction**
5. **Field Logic Reconstruction**
6. **FunctionCore Estimation**
7. **DoD Diagnostic**
8. **Likely Assessment Zones**
9. **Candidate Positioning Map**
10. **HCC Reverse Commentary**

The sequence is mandatory. A standalone stage is not treated as a valid HRDM run.

Each run receives a Process-ID.

## 1 — Ad/Text Intake

Capture:
- title
- employer
- source
- location
- employment type
- work mode
- deadline
- salary if stated
- complete public job text available to the run
- provenance URL

Separate explicit facts from extracted/inferred interpretation.

## 2 — Signal Extraction

Extract observable signals:
- repeated requirements
- verbs and burden language
- seniority markers
- ownership/accountability markers
- stakeholder environment
- change/ambiguity signals
- technical/domain requirements
- cultural/identity signalling
- hidden working-condition indicators

No interpretation yet.

## 3 — Key Words & Concepts

Cluster the signals into:
- capabilities
- activities
- outputs
- environments
- relationships
- constraints
- identity/seniority signals
- assessment vocabulary

## 4 — Hidden Need Reconstruction

Answer:

**What problem is the employer actually trying to solve by hiring this person?**

Separate the explicit job description from the reconstructed underlying need.

Include confidence markers.

## 5 — Field Logic Reconstruction

Map the functional field:
- domain
- institutional/market environment
- interfaces
- authority structure
- dependencies
- likely friction zones
- pace/volatility
- success conditions

## 6 — FunctionCore Estimation

Express the role as a functional chain rather than a title.

Example form:

`input/problem → core function → outputs → organisational use → outcome`

## 7 — DoD Diagnostic

DoD compares:

- **Alpha** — stated/advertised role baseline
- **Zenith** — estimated functional reality

Assess four dimensions:
1. burden deviation
2. scope/environment deviation
3. function deviation
4. signal/identity deviation

Use an unweighted four-dimension average for the diagnostic and classify:
- Low
- Moderate
- High
- Critical

DoD is a role-coherence diagnostic, not a candidate score.

## 8 — Likely Assessment Zones

Reconstruct how the employer is likely to judge a candidate.

Examples:
- writing/editorial judgement
- research accuracy
- stakeholder communication
- programme/project coordination
- institutional navigation
- language
- domain knowledge
- pace and delivery
- digital/tool fluency

Assessment zones must be derived from the ad and FunctionCore.

## 9 — Candidate Positioning Map

Compare role-side demands only with evidence supplied to the run.

Allowed evidence:
- `CareerHub/profile/candidate.yaml`
- explicit WPB repository evidence referenced by that profile
- optional private evidence supplied for the run

Do not import unsupported candidate claims from model memory.

Output:
- strongest evidence matches
- transferable matches
- gaps / unknowns
- claims that must not be made
- likely interview proof points
- application positioning
- CV emphasis/de-emphasis

## 10 — HCC Reverse Commentary

HCC reviews structural honesty and candidate risk:

- hidden overload
- role inflation
- vague boundaries
- conflicting expectations
- exclusion/fairness concerns
- dignity
- structural inconsistency
- unreasonable burden
- misleading seniority/title signals

HCC does not block an application by itself; it makes the structural trade-offs visible.

## CareerHub operational ranking

Before HRDM, CareerHub uses a lightweight **triage score** to rank a large job pool.

That score is not HRDM and must never be labelled as such.

The triage score can consider:
- title/domain overlap
- evidence-keyword overlap
- work arrangement preference
- location/remote fit
- search lane
- job recency
- explicit language/certification uncertainty

The full HRDM sequence begins only after a job is selected for drill-down.

## Application writing

Application drafting occurs **after** the canonical HRDM-R sequence.

The writing layer may use a Skewer-Lite approach to sharpen:
- opening position
- evidence density
- relevance
- rhythm
- specificity

It may not alter functional truth or invent candidate evidence.
