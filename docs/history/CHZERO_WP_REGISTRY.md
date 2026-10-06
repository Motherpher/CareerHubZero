# CareerHubZero Canonical Work-Package Registry

**Registry ID:** `CHZERO-WP-REGISTRY-001`  
**Cut-off:** 2026-10-07

## 1. Why this registry exists

CareerHub development has used several work-package namespaces at different times. GitHub issue numbers are not WP numbers, and later October PR titles reused short names such as `WP2` and `WP3` that collide with the earlier Silicon `WP02` and `WP03`.

This registry therefore treats **WP identity as its own field** and stores issue/PR numbers as evidence links.

### Namespace rule

- `M0–M6` = pre-Silicon migration milestones.
- `SIL-WP01–SIL-WP10` = CareerHub 1.0 Silicon Sprint. Display aliases remain `WP01–WP10`.
- `OCT-WP2`, `OCT-WP3` = October web/action execution packages whose PR titles used `WP2`/`WP3`; these are **not** Silicon WP02/WP03.
- `WP38`, `WP39` = chat/project aliases for GitHub issues #38/#39, whose formal titles are `WP-CHM-UX-01` and `WP-CHM-OPS-02`.
- `WP40` = GitHub issue #41.

---

# 2. Pre-Silicon migration milestones

These milestones are preserved because they explain the transition from WPB/Grace local Motors into the unified architecture. They were later absorbed/superseded by the Silicon sprint rather than deleted from history.

| ID | Historical name | Historical state in `docs/MIGRATION.md` | Reconciled outcome | Primary successor |
|---|---|---|---|---|
| M0 | Governance and evidence firewall | COMPLETE | Completed; evidence firewall remains canonical | SIL-WP01 / core governance |
| M1 | Unified body contract | COMPLETE | Completed; one VERSION/versionless manifests established | SIL-WP01 |
| M2 | Central runtime extraction | ACTIVE | Completed through central body + profile cutovers | SIL-WP01 / SIL-WP03 |
| M3 | Reusable distribution | OPEN | Original reusable-private-Action model replaced by checkout-based central execution | SIL-WP02 |
| M4 | Profile cutover | OPEN | Completed for Weronika/Grace on 2026-10-05 | SIL-WP03 |
| M5 | Geography completion | ACTIVE | Functionally cleared; Google Maps later made optional/user-disabled | SIL-WP06 |
| M6 | Full Audit Lock | NOT STARTED | Final audit state later PASS / release allowed | SIL-WP10 |

### Migration-specific companion issues

- Issue #2 — `M2 — Remove repository and instance hard-coding` — closed `not_planned`; requirement absorbed into central body work.
- Issue #12 — `M5 — Grace central-motor cutover and pre-firewall revalidation` — closed `not_planned`; work later completed under SIL-WP03/cutover commits.
- Issue #11 — `0.3.0-alpha: complete WPB central-motor cutover` — closed `not_planned`; superseded by Silicon WP structure.
- Issue #10 — `STACK BLOCKER: configure CAREERHUB_STACK_TOKEN` — closed `not_planned`; token architecture later removed/replaced.
- Issue #13 — `STACK OWNERSHIP — relocate all CareerHub profile repositories to Motherpher` — completed.

---

# 3. CareerHub 1.0 Silicon Sprint — canonical WP01–WP10

Authoritative sprint rule:

> **Invert before adding. Unify before optimizing. Replace, delete, then prove.**

Machine dependency source: `stack/sprints/CH-1.0-SILICON.yaml`.

## SIL-WP01 / WP01 — Collapse Runtime to One CareerHub Body

- **GitHub issue:** #1
- **Depends on:** none
- **Purpose:** move from central + Grace + Weronika runtime duplication to one CareerHub runtime and thin profile nodes.
- **Key deliverables:** runtime inventory, canonical module map, one CLI/action spine, generic sourcing/matching/HRDM/application/state/rendering code, repository-independence.
- **Deletion target:** authoritative Grace/Weronika local runtimes and duplicate runtime/render/document code after parity.
- **Historical risk:** centralisation by copying rather than contraction.
- **Final audit:** PASS (`C01`).
- **GitHub issue state at cut-off:** open; this does not override final-audit PASS.
- **Failure-search tags:** `duplicate-motor`, `runtime-authority`, `profile-local-code`, `centralisation`, `one-body`.

## SIL-WP02 / WP02 — Invert Distribution

- **GitHub issue:** #3
- **Depends on:** WP01
- **Purpose:** profile nodes invoke the central body and write only to themselves.
- **Original delivery assumption:** private reusable action/release pinning.
- **Historical blocker:** E01 private central Action resolution failed (`repository not found` class).
- **Resolution:** checkout-based central execution in each profile repository.
- **Architecture removed:** `CAREERHUB_STACK_TOKEN`/cross-profile write credential as stable dependency.
- **Formal recheck:** PR #33.
- **Final audit:** PASS (`C02`).
- **GitHub issue state:** closed/completed 2026-10-05.
- **Failure-search tags:** `E01`, `private-action`, `repository-not-found`, `distribution`, `checkout-central`, `stack-token`.

## SIL-WP03 / WP03 — Cut Over Profiles and Delete Legacy Motors

- **GitHub issue:** #4
- **Depends on:** WP01, WP02, WP07, WP08
- **Purpose:** one parity → cutover → delete pattern for Weronika and Grace.
- **Preservation requirements:** Grace 159-job history; verified profile evidence/state; pre-firewall artifact review.
- **Weronika evidence:** commit `842b31c` central cutover; `92f861d` migration-metadata retirement.
- **Grace evidence:** `1ff7dab` central cutover; `066be5b` migration metadata + pre-firewall artifact retirement.
- **Deletion target:** local Motors, local HRDM copies/runners, active migration-only metadata.
- **Formal recheck:** PR #33.
- **Final audit:** PASS (`C03`).
- **GitHub issue state:** closed/completed 2026-10-05.
- **Failure-search tags:** `cutover`, `legacy-motor`, `migration-metadata`, `parity`, `Weronika`, `Grace`, `159-job-history`.

## SIL-WP04 / WP04 — Unify the Search Kernel

- **GitHub issue:** #16
- **Depends on:** WP01
- **Purpose:** one search schema/normalisation/query contract over verified evidence + search overlay + hypotheses.
- **Deletion target:** legacy search-profile dialects, profile-side source-query transforms, duplicate lane normalisation.
- **Final audit:** PASS (`C04`).
- **GitHub issue state:** open.
- **Later related work:** OCT-WP2 search activation; WP39 search delta; WP40 Search UX.
- **Failure-search tags:** `search-kernel`, `lane-dialect`, `query-plan`, `dedupe`, `provenance`, `search-profile`.

## SIL-WP05 / WP05 — Career Learning Loop

- **GitHub issue:** #17
- **Depends on:** WP04
- **Purpose:** outcomes become bounded inputs to future search/ranking decisions without mutating candidate truth.
- **Canonical events:** surfaced, viewed/ignored, HRDM-selected, user rejected, applied, employer response, test/interview, offer, denied/withdrawn, elapsed time, geography.
- **Guardrail:** learning may tune hypotheses/ranking but may not create unsupported candidate evidence.
- **Deletion target:** separate analytics truth and second recommendation score.
- **Final audit:** PASS (`C05`).
- **GitHub issue state:** open.
- **Failure-search tags:** `learning-loop`, `candidate-truth`, `ranking`, `outcome-event`, `evidence-drift`.

## SIL-WP06 / WP06 — Unified Geography

- **GitHub issue:** #15
- **Depends on:** WP01, WP04
- **Purpose:** one normalized job-geo object with provider/country enrichment and map/drill projections.
- **Historical blocker:** E02 absent Google Maps API key.
- **Architecture correction:** PR #34 made Google Maps optional and user-disabled; geography remained supported without the paid provider.
- **Final audit:** PASS (`C06`).
- **GitHub issue state:** open.
- **Current external gate:** `E02 = SKIPPED_USER_DISABLED`.
- **Failure-search tags:** `E02`, `google-maps`, `geography`, `geo-object`, `provider-optional`, `precision`.

## SIL-WP07 / WP07 — Canonical HRDM

- **GitHub issue:** #18
- **Depends on:** WP01
- **Purpose:** one HRDM v6.3 execution path, one Process-ID/run ledger, active/history projections.
- **Original Hy-Filter rule:** Hybridianesque recommendation + explicit Yes/No user gate.
- **Artifacts:** Markdown/DOCX/PDF, active shelf, history/archive lifecycle.
- **Deletion target:** local HRDM copies, duplicate report/docx logic, shortened/noncanonical PIDs.
- **Final audit:** PASS (`C07`).
- **GitHub issue state:** open.
- **Later policy change:** WP39 moved normal-user Hybridianesque activation decision into the Motor.
- **Failure-search tags:** `HRDM`, `Process-ID`, `report-ledger`, `Hybridianesque`, `HCC`, `analysis`.

## SIL-WP08 / WP08 — One Application and Outcome State Machine

- **GitHub issue:** #19
- **Depends on:** WP01, WP07
- **Purpose:** one case + one event history for analysis/application/reminder/outcome state.
- **Deletion target:** duplicate status representations, separate reminder truth, profile-local case logic.
- **Final audit:** PASS (`C08`).
- **GitHub issue state:** open.
- **Failure-search tags:** `application-state`, `case-event`, `reminder`, `outcome`, `single-history`.

## SIL-WP09 / WP09 — One Hub Surface

- **GitHub issue:** #20
- **Depends on:** WP04, WP05, WP06, WP07, WP08
- **Original user contract:** `Find → Analyse? → Apply`.
- **Later managed-workspace surface:** `Profile → Search → Analyse → Apply → Track`, with Library/supporting areas.
- **Historical blocker:** upstream geography/E02 plus stale expectation of Python dashboard path.
- **Reconciliation:** PR #35 replaced obsolete dashboard-path gate with canonical managed Next.js workspace.
- **Final audit:** PASS (`C09`).
- **GitHub issue state:** open.
- **Failure-search tags:** `hub-surface`, `Next.js`, `user-flow`, `dashboard`, `navigation`, `internal-terminology`.

## SIL-WP10 / WP10 — Contract, Audit and Lock CareerHub 1.0

- **GitHub issue:** #14
- **Depends on:** WP01–WP09
- **Purpose:** deletion + proof + Full Audit Lock, not feature accumulation.
- **Required proof:** central regressions, Linus/Weronika/Grace runs, live AI, geography, learning, HRDM report/archive, one-source-of-truth audit.
- **Historical blockers:** E01/E02/E03 and stale final-audit snapshot.
- **Final audit:** PASS (`C10`), Director PASS, release 1.0 allowed.
- **GitHub issue state:** open.
- **Important release distinction:** current `VERSION` is still `0.2.9-alpha`; audit permission is not evidence that 1.0.0 was actually tagged/released.
- **Failure-search tags:** `full-audit`, `1.0`, `release-lock`, `stale-snapshot`, `Janitor`, `Director`.

---

# 4. October web/action execution packages

## OCT-WP1 — managed workspace promotion/sync

- **Nature:** chat/execution-package alias; not a formal GitHub WP title.
- **Primary evidence:** PR #27 and profile-site syncs.
- **Purpose:** promote Profile/Search/Analyse/Apply/Track/Library into central shell, then sync to profile sites.
- **Status:** implemented/merged.
- **Failure-search tags:** `managed-shell`, `workspace`, `sync`, `profile-site`.

## OCT-WP2 — Add interactive web search activation

- **GitHub PR:** #28 (`WP2 — Add interactive web search activation`)
- **Collision warning:** not Silicon WP02.
- **Trigger:** `/find` could display Search Profile but had no execution action.
- **Fix:** Run Search, session overrides, server-side Platsbanken execution, dedupe/triage/provenance.
- **Status:** merged 2026-10-05.
- **Failure-search tags:** `no-search-button`, `find`, `Platsbanken`, `search-activation`, `session-override`.

## OCT-WP3 — Complete CareerHub action surfaces and Motor handoffs

- **GitHub PRs:** #29 (superseded/closed), #30 (clean merged implementation), #31/#32 hardening.
- **Collision warning:** not Silicon WP03.
- **Trigger:** visible product surfaces lacked complete execution/result handoff contracts.
- **Fix:** Action Completeness Contract, `/api/action`, profile operations workflow, fixture build gate.
- **Secondary failure:** Turbopack illegal outside-site tracing.
- **Secondary fix:** `.careerhub-artifacts` mirror + narrow tracing.
- **Status:** merged and hardened.
- **Failure-search tags:** `action-completeness`, `api-action`, `Turbopack`, `artifact`, `handoff`, `build-failure`.

---

# 5. WP38–WP40 operational/product-integrity line

## WP38 — Motor Interaction Clarity & Guidance

- **Formal GitHub title:** `WP-CHM-UX-01 — Motor Interaction Clarity & Guidance`
- **GitHub issue:** #38
- **Alias source:** later project/chat and PR #40 call the pair “WP38–39”.
- **Trigger:** opaque action state; user could not easily tell where they were, what the Motor was doing, or what to do next.
- **Required:** active indicator, plain-language state, current profile/lane visibility/editing, workflow orientation, searchable help.
- **Implementation:** PR #40.
- **Issue state:** open at cut-off, despite merged implementation PR.
- **Reconciled implementation status:** implemented in central Motor; fleet sync later completed.
- **Failure-search tags:** `queued-message`, `ACT-reference`, `active-process`, `workflow-help`, `profile-lanes`.

## WP39 — Restore results, automatic Hy-Filter, Search delta and Wish routing

- **Formal GitHub title:** `WP-CHM-OPS-02 — Restore HRDM-R Results, Auto-Hybridianesque, Search Delta & Wish Routing`
- **GitHub issue:** #39
- **Trigger families:**
  1. queued analysis without visible returned report;
  2. normal user forced to decide expert Hybridianesque activation;
  3. repeated search unable to distinguish no-new from failed/stale run;
  4. Wish routing fragmented.
- **Required lifecycle:** PREPARING / WAITING_FOR_EXECUTION / RUNNING / COMPLETED / FAILED.
- **Implementation:** PR #40.
- **Post-merge hardening:** repository read-back required before `COMPLETED`; commits `b55547e`, `c08e639`.
- **E2E evidence:** action `ACT-20261006155733-2c2a00a7`; PID `HRDM-R-20261006-0001-S09-A-R01-FINAL`.
- **Issue state:** open at cut-off; implementation/fleet evidence exists.
- **Failure-search tags:** `report-not-returned`, `false-complete`, `Hybridianesque-gate`, `search-delta`, `Wish-routing`, `durable-persistence`.

## WP40 — CareerHub Reset, Background Execution & Search/Library Usability

- **GitHub issue:** #41
- **Opened:** 2026-10-06
- **State:** open / not completed at reconstruction cut-off.
- **Trigger:** live usability failures after WP38–39 fleet rollout.
- **Original workstreams:**
  - A — safe reset/test-residue cleanup;
  - B — Library profile isolation + actual ACTIVE evidence use;
  - C — durable background Job Analysis;
  - D — ordinary-job-site Search UX;
  - E — central searchable Help/Q&A;
  - F — deployment repository bindings/normal production access.

### Chat-derived four-sprint decomposition

This decomposition was created after the issue and is recorded separately from the original issue text:

#### WP40.1 — State Integrity, Reset & Profile Isolation

- safe residue classification/reset;
- explicit runtime profile context;
- profile-scoped Library namespace;
- cross-profile fail-closed tests;
- deployment binding preflight.

**Gate:** `STATE BASELINE LOCK`.

#### WP40.2 — Durable Library, Evidence Pipeline & Background Analysis

- upload → ingest → index → ACTIVE lifecycle;
- evidence-use manifest;
- ACTIVE-only analysis context;
- durable ActiveProcess record;
- navigation/reload-safe analysis;
- global process indicator;
- stable `/analyse/<action-id>` result.

**Gate:** `DURABLE PROCESS LOCK`.

#### WP40.3 — Search Workspace & Job Decision Flow

- click-based job type controls;
- remote/hybrid/on-site where supported;
- published/deadline date windows;
- last week/month/2 months/3 months + custom range;
- persistent `[×]` dismissal;
- checked/new completion summary;
- direct Search → Analyse handoff.

**Gate:** `SEARCH WORKFLOW LOCK`.

#### WP40.4 — Help, Fleet Hardening, Release Audit & WP40 Lock

- central `/help` and contextual anchors;
- three-profile parity matrix;
- implementation-language audit;
- test-residue audit;
- production-access audit;
- final fleet scenarios.

**Gate:** `FLEET ACCEPTANCE LOCK`.

### WP40 known acceptance targets

- Grace upload lifecycle and evidence use proven;
- no cross-profile Library list/open/delete;
- analysis survives navigation/reload;
- global active-process surface;
- real Search job can complete end-to-end analysis;
- no normal UI `HRDM-R` or `Hybridianesque` language;
- Search type/date/dismiss controls;
- central searchable `/help`;
- remove `WP39 End-to-End Test Role` residue;
- Linus/Weronika/Grace fleet rollout/preflight.

---

# 6. Status-precedence rule

For every WP, the registry preserves multiple status channels rather than collapsing them:

1. **Historical document state** — valid only at its timestamp.
2. **GitHub issue/PR state** — workflow metadata, not necessarily functional truth.
3. **Audit state** — current machine/audit evidence where available.
4. **Deployment/fleet state** — whether profile nodes actually received the change.
5. **Release state** — whether the corresponding version/tag was actually released.

A GitHub issue can therefore remain open while its final-audit status is PASS, and a release can be *allowed* without `VERSION` having been bumped.
