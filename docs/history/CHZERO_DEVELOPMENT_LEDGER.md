# CareerHubZero Unified Development Ledger

**Ledger ID:** `CHZERO-DEV-LEDGER-001`  
**Canonical home:** `Motherpher/CareerHubZero`  
**Reconstruction cut-off:** 2026-10-07  
**Purpose:** one chronological and cross-referenced development history for CareerHub/CareerHubZero, with explicit work-package lineage, architectural reversals, failure/fix history and profile-fleet evidence.

> This ledger is a reconstruction layer over immutable Git history, GitHub issues/PRs, machine-readable release/audit state and historical ChatGPT design conversations. It does **not** replace those sources. It makes them searchable as one development history.

## 1. Source scope

The reconstruction covers the four repositories that materially form the CareerHub development line:

1. `Motherpher/CareerHubZero` — canonical Motor/software body, schemas, governance, audits, WPs and managed shell.
2. `Motherpher/wpb` — Weronika profile node and the original working CareerHub implementation from which reusable capability was extracted.
3. `Motherpher/Gracey` — Grace profile node; original local Motor, migration/cutover history, evidence recovery and fleet rollout.
4. `Motherpher/CareerHub-LinusF` — Linus reference thin-profile node and first personalised managed-site implementation.

Primary in-repository evidence includes:

- `CHANGELOG.md`
- `VERSION`
- `docs/EXTRACTION_INVENTORY.md`
- `docs/MIGRATION.md`
- `docs/SPRINT_1_0_SILICON_10WP.md`
- `docs/audit/*`
- `stack/releases/*`
- `stack/sprints/CH-1.0-SILICON.yaml`
- `stack/household/final-audit-status.json`
- GitHub issues/PRs #1–#41 and their implementation commits
- corresponding profile-repository commits and managed-site syncs.

Chat history is used for decisions and failure context that were not always preserved as formal repository artifacts. Where chat and repository state differ, the ledger records both as time-bound evidence and gives current machine state precedence for current-status claims.

---

# 2. Development chronology

## Phase A — WPB CareerHub genesis
### 2026-09-23

CareerHub first became a working system inside `wpb`. The initial commit stream built a complete profile-local prototype rather than a thin client. The sequence included:

- CareerHub overview/control room and privacy rules;
- job-source registry, search lanes and queries;
- Python package, job model, state, source adapters and triage matching;
- control-room renderer and CLI;
- scheduled/manual scans;
- HRDM application drill workflow;
- validation/provider integration documentation;
- issue-driven request parsing;
- job vault, application lifecycle, reminders and tracking;
- repeated UX contraction from technical control room toward a human `Find → Choose/Analyse → Apply` journey;
- shortlist-quality, provider-field and encoding fixes.

Representative WPB commits include `1db6126` (CareerHub overview), `c614bde` (Python package), `5023ecd` (source adapters), `40257ea` (HRDM application drill), `aa5296d` (persistent job vault/application state), and `0ece2f6` (Find/Choose/Apply UX).

### Architectural finding

The prototype proved the product, but it also exposed the structural problem that later created CareerHubZero: reusable software, personal profile evidence and live personal state were co-located in one person's repository.

`docs/EXTRACTION_INVENTORY.md` later formalised the split:

- **centralise:** models, state machinery, sourcing, matching, HRDM, application generation, canonical HRDM documents, reusable adapters/operations;
- **generalise first:** dashboard, CLI, workflows and search-profile logic;
- **remain profiled:** candidate evidence, private CV/LinkedIn reconciliation, job vault, applications, generated cases, personal preferences and notification destinations.

---

# Phase B — CareerHubZero established as central capability
## 2026-09-23

`Motherpher/CareerHubZero` was created as the central operations/software repository. The design boundary became:

```text
CareerHubZero = reusable capability / Motor / common contracts
profile repository = person identity + verified evidence + preferences + live state + generated artifacts
```

WPB remained live while extraction was performed.

### 0.1.0-alpha

Initial CHZero baseline:

- central operations vs profiled-instance boundary;
- architecture and migration documentation;
- HRDM-R v6.3 core/schema preservation;
- first validation workflow;
- roadmap/milestone structure.

### Early migration/M-series

The early migration line used `M0–M6` terminology before the later Silicon WPs superseded it as the main execution map. The historical migration sequence was:

- M0 — Governance and evidence firewall
- M1 — Unified body contract
- M2 — Central runtime extraction
- M3 — Reusable distribution
- M4 — Profile cutover
- M5 — Geography completion
- M6 — Full Audit Lock

See `CHZERO_WP_REGISTRY.md` for temporal and reconciled status.

### First infrastructure failure: OpenAI secret placement

An organization-level secret could not be exposed to the private CHZero repository under the available GitHub organisation setup. The selected-repository route did not make the secret usable. The operational workaround was a repository-level `OPENAI_API_KEY` rather than continuing to depend on the unavailable organisation-secret path.

---

# Phase C — Profile contracts, drift correction and stack governance
## 2026-09-23 to 2026-09-24

### 0.2.0-alpha — profiled-instance expansion

Added:

- profile/search/evidence contracts and loader;
- dashboard renderer;
- experimental market-response/positioning structures.

### Drift event — Napp / market-response

The experimental market-response layer was judged to be architectural drift from the base CareerHub contract. The user explicitly required one central Motor and profile variation only; Napp was not to become part of the base hub structure.

PR #8 restored the canonical base contract:

```text
Find → Analyse? → Apply
```

and removed the non-canonical Napp/market-response extension from the base system.

### 0.2.2-alpha — harmonised stack governance

PR #9 introduced:

- `VERSION` as the version source;
- stack registry;
- per-version machine-readable release ledger/backlog;
- generated stack locks;
- cross-repository sync/compatibility checks;
- CI enforcement against Motor/schema/workflow drift.

At this stage a cross-profile stack token (`CAREERHUB_STACK_TOKEN`) was still part of the distribution approach. Issue #10 captured the missing-token blocker. This mechanism was later removed from the stable architecture rather than becoming permanent.

### Linus profile node

Issue #7 records the deployment of `Motherpher/CareerHub-LinusF` as the first private profile node, initially aligned to `CareerHubZero@0.2.0-alpha`. It became the first thin-profile reference and later the first managed personalised web-shell reference.

---

# Phase D — Evidence firewall, Grace recovery and unified body
## 2026-09-24

### 0.2.3-alpha — verified-career evidence firewall

CareerHub established a strict evidence boundary:

- private-life fields cannot become matchable candidate evidence;
- matchable claims require verified permitted career sources;
- user wishes/specific needs belong to Search Profile/search overlay;
- search intent may not silently become CV, HRDM or application evidence.

This rule persists as a core integrity invariant.

### Grace registration and recovery

Grace became the third active profile line. Historical issue #12 and migration records show the required preservation/recovery work:

- preserve the existing 159-job history;
- introduce verified career sources;
- quarantine/revalidate or retire pre-firewall application material;
- verify central parity before deleting the local runtime.

### 0.2.4-alpha / 0.2.5-alpha

The line added:

- Grace stack recovery and Motherpher ownership governance;
- formal 1.0 Full Audit Lock concept;
- precision-aware vacancy geotagging;
- Google Places adapter and canonical job-geography schema;
- zoom-aware aggregation and precision preservation.

### 0.2.6-alpha — one CareerHub body

The architecture changed from a permanent `engine + stack-lock` model to:

```text
one CareerHub software body + one VERSION
```

with versionless `careerhub.yaml` manifests in each profile node.

Stable architecture explicitly removed:

- profile-local independent versions;
- stable `instance.yaml` / `stack.lock.yaml` requirements;
- central cross-repository version propagation;
- `CAREERHUB_STACK_TOKEN` as a stable dependency.

### 0.2.7-alpha — execution spine and HRDM lifecycle

Added:

- one manifest-driven central CLI;
- central reusable execution path;
- canonical HRDM Process-ID/run registry;
- active report shelf and immutable **HRDM report history**;
- report archive after vacancy deadline;
- Markdown/DOCX/PDF report artifacts;
- Hybridianesque Hy-Filter as the then-current optional explicit gate;
- search-profile normalisation;
- capability audit.

Important distinction: the “immutable historical ledger” introduced here was the HRDM run/report ledger, **not** a CHZero development-history ledger. This document set supplies the missing development ledger.

---

# Phase E — CareerHub 1.0 Silicon Sprint
## 2026-09-24 to 2026-09-25

The user accepted a ten-WP contraction sprint with the rule:

> **Invert before adding. Unify before optimizing. Replace, delete, then prove.**

The authoritative dependency map is stored in `stack/sprints/CH-1.0-SILICON.yaml` and fully described in `docs/SPRINT_1_0_SILICON_10WP.md`.

### WP01–WP10

| WP | Issue | Purpose |
|---|---:|---|
| WP01 | #1 | Collapse Runtime to One CareerHub Body |
| WP02 | #3 | Invert Distribution |
| WP03 | #4 | Cut Over Profiles and Delete Legacy Motors |
| WP04 | #16 | Unify the Search Kernel |
| WP05 | #17 | Career Learning Loop |
| WP06 | #15 | Unified Geography |
| WP07 | #18 | Canonical HRDM |
| WP08 | #19 | One Application and Outcome State Machine |
| WP09 | #20 | One Hub Surface |
| WP10 | #14 | Contract, Audit and Lock CareerHub 1.0 |

### 2026-09-25 audit snapshot

The Household audit was intentionally preserved as a historical snapshot. At that time three external gates blocked parts of the dependency chain:

- **E01** — private central Action/distribution path unresolved (`repository not found` class of failure);
- **E02** — Google Maps API key unavailable;
- **E03** — OpenAI API returned `429 credit_balance_exhausted`.

The dependency logic was:

- E01 → WP02 → WP03;
- E02 → WP06 → WP09;
- E03 → live HRDM/application proof → WP10.

This status is historical, not current.

---

# Phase F — Distribution/cutover recovery and profile thin-node closure
## 2026-10-05

Repository recheck and implementation replaced the blocked private reusable-Action model with **checkout-based central execution** in each profile repository.

PR #33 records the formal recheck:

- WP02 PASS after checkout-based distribution worked for Weronika and Grace;
- WP03 PASS after duplicated local Motors were removed and validation/rendering succeeded;
- the 2026-09-25 audit remained preserved rather than rewritten.

### Weronika cutover

Key commits:

- `842b31c` — WP03 central-Motor cutover, operations bridge, workflow rebinding, duplicate runtime removal;
- `92f861d` — migration metadata retirement.

### Grace cutover

Key commits:

- `1ff7dab` — WP03 central-Motor cutover and duplicate runtime removal;
- `066be5b` — migration metadata retirement and pre-firewall Region Stockholm artifact retirement.

This is the point at which Linus, Weronika and Grace become materially consistent with the thin-profile architecture.

---

# Phase G — Personalised web architecture and managed workspace
## 2026-10-05

The product then shifted from repository/control-room operation to dedicated personalised CareerHub web workspaces.

### PR #21 — dual personalised hub architecture

Established:

- CareerHubZero remains sole Motor/software body;
- each profile repository owns verified person context, runtime state and protected presentation/UX configuration;
- managed central shell can be synchronised without overwriting protected personalisation.

### PR #22 — documentation reconciliation

Removed remaining documentation contradiction around profile presentation ownership vs central Motor ownership.

### PR #23 — personal workspace / Library / Search-session architecture

Established the user-facing workspace sequence:

```text
Profile → Search → Analyse → Apply → Track
```

with Library and improvement functions as supporting workspaces. It also separated persistent Search Profile from one-search overrides and added source-library/search-session contracts.

### PR #24 — non-generic personalised derivation

Added the central derivation formula and anti-generic guardrails for person-specific CareerHub presentation.

### PR #25–26 — Wish Bank

Created the `I wish… / Jag önskar…` feedback loop, then segmented wishes into MOTOR / PROFILE / BOTH / UNTRIAGED and functional domains. Vercel private Blob became the operational store; GitHub issue projection remained optional.

### PR #27 — workspace capability promotion

Promoted the reusable Profile/Search/Analyse/Apply/Track/Library surfaces into the central managed shell.

---

# Phase H — October execution packages: web activation and action completeness
## 2026-10-05

These packages used short `WP2`/`WP3` names in PR titles. They are **not** the same as Silicon WP02/WP03. This ledger namespaces them as `OCT-WP2` and `OCT-WP3`.

### OCT-WP2 — PR #28

Failure found: the personalised `/find` page could show search settings but could not actually launch a search.

Fix:

- `Run Search` control;
- saved Search Profile remains baseline;
- session-only lane/need override;
- server-side Platsbanken execution;
- dedupe/ranking/provenance;
- no mutation of saved Search Profile.

### OCT-WP3 — PR #29 → PR #30

PR #29 was closed because of pre-squash history conflict, then rebuilt cleanly as PR #30.

PR #30 established the Action Completeness Contract:

- every user capability must expose control, choices, execution path and result state;
- `/api/action` Motor gateway;
- managed profile operations workflow;
- root/nested profile layout support;
- shell + operations bridge sync;
- fixture-site production build gate.

### Turbopack artifact failure — PR #31 and PR #32

The new production build gate caught invalid tracing outside the Next.js site root (`../output` and `../reports`).

Resolution:

- generated artifacts mirrored under `site/.careerhub-artifacts`;
- operations workflow refreshes/commits the mirror;
- tracing narrowed to managed mirror only;
- external artifact path contract preserved.

This is an important example of why failures are first-class ledger records rather than buried in commits.

---

# Phase I — External-gate and Full Audit reconciliation
## 2026-10-06

### E02 — Google Maps path changed by user decision

PR #34 made paid Google Maps optional and disabled by user choice. CareerHub geography remained supported through local/admin/labour-market geography. E02 became `SKIPPED_USER_DISABLED`, not a system failure.

### E03 — OpenAI live gate

PR #35 records live OpenAI Responses API PASS in run `37436076911` using `gpt-5.6-sol` and reconciles the audit against the current managed Next.js surface.

### WP01–WP10 final audit state

PR #36 updated the final audit snapshot after Household run `37436795188` and validation run `37436795258`.

`stack/household/final-audit-status.json` currently records:

- overall `PASS`;
- WP01–WP10 all `PASS`;
- Janitor `PASS_WITH_NONBLOCKING_FINDINGS`;
- Director reconciliation `PASS`;
- E01 PASS through checkout-based central execution;
- E02 optional/user-disabled;
- E03 PASS;
- `release_1_0_allowed: true`.

### Current release-state caveat

Despite audit permission for 1.0, the current repository `VERSION` remains `0.2.9-alpha`, and several historical GitHub WP issues remain open. Therefore this ledger distinguishes:

- **audit/functional status** — current machine evidence;
- **GitHub issue state** — workflow metadata;
- **released version** — actual `VERSION`/tag state.

The ledger must not infer that `1.0.0` was released merely because release was allowed.

---

# Phase J — Motor usability WPs 38–39
## 2026-10-06

Live personalised-site testing exposed a new class of closed-loop usability/operations failures.

### WP38 alias / Issue #38

GitHub title: `WP-CHM-UX-01 — Motor Interaction Clarity & Guidance`.

Trigger included opaque queued-action messaging and poor visibility of profile/search-lane/state controls.

Required:

- visible active-process indicator;
- plain-language state vocabulary;
- profile/search-lane discoverability;
- workflow explanation;
- searchable help/Q&A.

### WP39 alias / Issue #39

GitHub title: `WP-CHM-OPS-02 — Restore HRDM-R Results, Auto-Hybridianesque, Search Delta & Wish Routing`.

Four failure families:

1. HRDM could be queued but the report did not return to the browser.
2. Hybridianesque relevance was wrongly pushed onto the normal user as a Yes/No expert choice.
3. repeated search could not distinguish no-new-results from stale/failed execution;
4. Wish routing was fragmented across deployments.

### PR #40 — WP38–39 integration

Merged both WPs as one unit:

- action preflight and explicit lifecycle;
- stable HRDM result retrieval;
- automatic evidence-gated Hybridianesque relevance;
- search-session persistence/delta (`NEW` / `SEEN` / `CHANGED` plus source-health separation);
- protected Wish Bank ledger/health;
- Motor workflow/help/profile/lane/active-state UI.

### E2E production proof and persistence hardening

Subsequent live work proved the full chain with action `ACT-20261006155733-2c2a00a7` and Process-ID `HRDM-R-20261006-0001-S09-A-R01-FINAL` in the Weronika profile line.

A critical completion invariant was then hardened in CHZero commits:

- `b55547e` — repository persistence required before completion;
- `c08e639` — durable HRDM persistence invariants locked.

The resulting rule is:

```text
generation success != COMPLETED
COMPLETED requires durable profile-repository materialisation + read-back
```

A direct Search Profile script-import/shadowing defect was also corrected and regression-protected during this production closure.

### Fleet rollout

The Motor close-loop update was subsequently synced across all three active profiles. Fleet-sync commits include:

- Linus `40e38ea`;
- Weronika `74d6a60`;
- Grace `7bb9106`.

---

# Phase K — WP40 product-integrity work
## Opened 2026-10-06; current at reconstruction cut-off

Issue #41: `WP40 — CareerHub Reset, Background Execution & Search/Library Usability`.

WP40 exists because a technically operational Motor still exposed product-integrity and usability faults across the three live profile instances.

Original issue workstreams:

A. Safe CH reset / synthetic residue cleanup.  
B. Library profile isolation + actual ACTIVE evidence use.  
C. Durable background analysis execution and stable results.  
D. Search UX comparable to ordinary job sites.  
E. Centrally managed searchable Help/Q&A.  
F. Deployment bindings / production access.

A later chat design decomposed WP40 into four dependency-ordered sprints. That decomposition is retained as **design evidence**, not retroactively presented as part of the original GitHub issue:

1. `WP40.1 — State Integrity, Reset & Profile Isolation`
2. `WP40.2 — Durable Library, Evidence Pipeline & Background Analysis`
3. `WP40.3 — Search Workspace & Job Decision Flow`
4. `WP40.4 — Help, Fleet Hardening, Release Audit & WP40 Lock`

The WP remains open at this reconstruction cut-off.

Known unresolved/acceptance targets include:

- remove `WP39 End-to-End Test Role` residue from Weronika-facing UI;
- Grace Library upload/open/activate/deactivate/erase and evidence-context proof;
- cross-profile Library isolation;
- navigation/reload-safe Job Analysis;
- global process visibility;
- remove user-facing `HRDM-R` / `Hybridianesque` terminology;
- date/type/mode search filters and persistent result dismissal;
- central `/help` surface;
- fleet preflight for Linus/Weronika/Grace.

---

# 3. Current reconciled architecture

At the cut-off, the intended architecture is:

```text
Motherpher/CareerHubZero
  = canonical Motor
  = common product body
  = managed web shell
  = common workflows/contracts/schemas
  = central Help/Wish infrastructure where applicable

Motherpher/CareerHub-LinusF
Motherpher/wpb/CareerHub
Motherpher/Gracey/CareerHub
  = thin profile nodes
  = verified evidence
  = personal search configuration
  = personal state
  = generated artifacts
  = protected presentation/personalisation
```

Profile-specific presentation may vary; Motor logic may not silently fork.

---

# 4. Status model used by this ledger

Every future ledger entry should separate:

- `status_at_event` — what was true then;
- `current_reconciled_status` — what later evidence establishes;
- `github_state` — issue/PR open/closed/merged state;
- `release_state` — actual released/tagged/version state;
- `superseded_by` — later architecture or fix when relevant.

This prevents historically correct documents from being mistaken for current truth.

---

# 5. Inclusion / exclusion rule

The ledger includes all development-significant WPs, architecture changes, failures, corrections, deployment gates and profile cutovers found in the source set.

Raw Git history remains the exhaustive commit ledger. Repetitive generated-data refresh commits (for example repeated job-list refreshes) are not duplicated line-by-line here unless they changed architecture, behaviour, failure state or validation. They remain discoverable through repository Git history and can be connected to a ledger event through the machine-readable index.

---

# 6. Companion records

- [`CHZERO_WP_REGISTRY.md`](./CHZERO_WP_REGISTRY.md) — canonical WP/M-series registry, aliases, dependencies and temporal/current status.
- [`CHZERO_FAILURE_SEARCH_INDEX.md`](./CHZERO_FAILURE_SEARCH_INDEX.md) — symptom/root-cause/fix/regression search index.
- [`CHZERO_PROVENANCE_MAP.md`](./CHZERO_PROVENANCE_MAP.md) — evidence hierarchy and source catalogue.
- [`../../stack/history/development-ledger.yaml`](../../stack/history/development-ledger.yaml) — machine-readable history/search spine.
