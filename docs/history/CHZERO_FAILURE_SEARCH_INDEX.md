# CareerHubZero Failure Search Index

**Index ID:** `CHZERO-FAIL-INDEX-001`  
**Cut-off:** 2026-10-07

## 1. Purpose

This file is designed for reverse lookup from a failure symptom.

Do not search only by WP number. Search by the words a user/developer is likely to observe, for example:

- `analysis completed no report`
- `repository not found action`
- `search no new jobs`
- `Turbopack output reports`
- `Grace upload not evidence`
- `profile sees other profile library`
- `Maps key`
- `429 credit_balance_exhausted`

Each record links symptom → subsystem → historical cause → resolution → WP/PR/commit → regression guard/current state.

## 2. Failure classes

- `ARCH_DRIFT` — architecture deviates from the canonical one-body/thin-profile contract.
- `EXEC_PATH` — dispatch/execution path does not run or cannot be resolved.
- `PERSISTENCE` — generated state/result does not durably materialise.
- `SURFACE` — user-facing control/result/state is absent or misleading.
- `INTEGRATION` — external/provider/repository/deployment integration failure.
- `DATA_BOUNDARY` — profile/evidence/privacy/isolation boundary failure or risk.
- `BUILD` — build/runtime packaging failure.
- `SEARCH` — sourcing/query/delta/filter/result-quality failure.
- `AUDIT_STATE` — stale or conflicting state records.
- `MIGRATION` — legacy Motor/metadata/cutover failure.

---

## FAIL-001 — Organisation OpenAI secret unavailable to private CHZero

- **Search terms:** `org secret`, `OPENAI_API_KEY`, `selected repository`, `private repo`, `GitHub Free`
- **Class:** INTEGRATION
- **Date:** 2026-09-23
- **Symptom:** organisation secret could not be made available to private CareerHubZero through the selected-repository configuration.
- **Root cause:** available GitHub organisation/plan secret configuration did not expose the desired org secret to the private repo.
- **Resolution:** use repository-level `OPENAI_API_KEY` for CHZero rather than blocking on org-secret distribution.
- **Affected:** CareerHubZero live AI path.
- **Status:** resolved/superseded architecture.

## FAIL-002 — Base-product drift via Napp / market-response extension

- **Search terms:** `Napp`, `market-response`, `architecture drift`, `base contract`, `Find Analyse Apply`
- **Class:** ARCH_DRIFT
- **Date:** 2026-09-23
- **Symptom:** experimental positioning/market-response functionality began to behave like a base CareerHub subsystem.
- **Root cause:** profile/research extension was promoted too far into the common architecture.
- **Resolution:** PR #8 restored canonical base flow and removed the noncanonical extension from base CareerHub.
- **Guard:** one central Motor; profiles may vary, base architecture may not fork.
- **Status:** resolved.

## FAIL-003 — CAREERHUB_STACK_TOKEN dependency became architectural liability

- **Search terms:** `CAREERHUB_STACK_TOKEN`, `stack token`, `cross repo token`, `profile sync`, `push distribution`
- **Class:** ARCH_DRIFT / INTEGRATION
- **Date:** 2026-09-23 to 2026-09-24
- **Symptom:** stack harmonisation depended on a credential with write/read scope across private profile repos.
- **Root cause:** distribution model assumed central push/synchronisation.
- **Historical issue:** #10.
- **Resolution:** unified-body architecture removed the token from stable design; Silicon WP02 later adopted checkout-based central execution in profile repos.
- **Status:** superseded/resolved.

## FAIL-004 — E01 central reusable Action could not resolve private CHZero

- **Search terms:** `E01`, `repository not found`, `Unable to resolve action`, `private action`, `CareerHubZero action`
- **Class:** EXEC_PATH / INTEGRATION
- **Date:** 2026-09-25
- **Symptom:** profile workflow could not resolve the central private Action (`repository not found` class).
- **Impact:** WP02, WP03 and downstream 1.0 proof blocked.
- **Root cause:** cross-repository private reusable-Action accessibility/distribution path.
- **Resolution:** replace blocked reusable-Action distribution with checkout-based execution of CareerHubZero inside each profile repository.
- **Evidence:** PR #33; final audit E01 PASS with checkout-based mechanism.
- **Regression guard:** profile nodes run central body without requiring cross-profile write credentials.
- **Status:** PASS/resolved.

## FAIL-005 — E02 Google Maps API key unavailable / paid provider unwanted

- **Search terms:** `E02`, `Google Maps`, `Maps key`, `GOOGLE_MAPS_API_KEY`, `paid maps`
- **Class:** INTEGRATION
- **Date:** 2026-09-25 to 2026-10-06
- **Symptom:** geography gate blocked on absent Google Maps key.
- **Root cause:** audit/design treated one provider as mandatory even though geography had other valid runtime paths.
- **Resolution:** PR #34 made Google Maps optional and disabled by explicit user choice; local/admin/labour-market geography remains active.
- **Current audit state:** `SKIPPED_USER_DISABLED`, authorised/nonblocking.
- **Status:** resolved by architecture/policy change.

## FAIL-006 — E03 OpenAI credit exhaustion

- **Search terms:** `E03`, `429`, `credit_balance_exhausted`, `OpenAI quota`, `Responses API`
- **Class:** INTEGRATION
- **Date:** 2026-09-25; cleared 2026-10-06
- **Symptom:** live OpenAI gate failed with HTTP 429 credit-balance exhaustion.
- **Impact:** live HRDM/application proof and WP10 blocked.
- **Resolution evidence:** run `37436076911` passed OpenAI Responses API using `gpt-5.6-sol` and `CAREERHUB_GATE_OK`.
- **Status:** PASS/resolved.

## FAIL-007 — Weronika and Grace retained duplicate local Motors

- **Search terms:** `legacy motor`, `local motor`, `src/careerhub`, `local HRDM`, `WP03`, `profile cutover`
- **Class:** MIGRATION / ARCH_DRIFT
- **Date:** 2026-09-24 to 2026-10-05
- **Symptom:** profile repositories still contained authoritative runtime/HRDM despite one-body target.
- **Root cause:** migration parity/cutover incomplete.
- **Resolution Weronika:** commits `842b31c` and `92f861d`.
- **Resolution Grace:** commits `1ff7dab` and `066be5b`.
- **Evidence:** PR #33; final audit WP03 PASS.
- **Status:** resolved.

## FAIL-008 — Grace pre-firewall application artifact unsafe under new evidence policy

- **Search terms:** `Grace`, `Region Stockholm`, `pre-firewall`, `application artifact`, `quarantine`
- **Class:** DATA_BOUNDARY / MIGRATION
- **Date:** 2026-09-24 to 2026-10-05
- **Symptom:** application artifact predated the verified-career evidence firewall and could not automatically be treated as valid.
- **Resolution:** quarantine/review requirement; Grace closure commit `066be5b` retired the pre-firewall Region Stockholm artifact.
- **Status:** resolved.

## FAIL-009 — Vercel project creation blocked by permission 403

- **Search terms:** `Vercel 403`, `project creation`, `permission`, `deployment blocked`
- **Class:** INTEGRATION
- **Date:** 2026-10-05
- **Symptom:** initial programmatic Vercel project creation for personalised CareerHub was blocked by permission/403.
- **Later state:** profile deployments subsequently existed and were synced; this is retained as historical deployment failure evidence.
- **Status:** historical blocker, later bypassed/resolved operationally.

## FAIL-010 — `/find` displayed search configuration but could not run a search

- **Search terms:** `find no search`, `Run Search missing`, `search settings only`, `Platsbanken`, `WP2`
- **Class:** SURFACE / SEARCH
- **Date:** 2026-10-05
- **Symptom:** deployed Search workspace displayed saved configuration but had no working activation path.
- **Resolution:** OCT-WP2 / PR #28 added Run Search, server-side Platsbanken execution, session overrides, dedupe/triage and provenance.
- **Guard:** Search surface must expose a complete user action, not configuration only.
- **Status:** resolved.

## FAIL-011 — OCT-WP3 first PR carried pre-squash history conflict

- **Search terms:** `PR29`, `WP3 conflict`, `pre-squash`, `superseded branch`
- **Class:** BUILD / DEVELOPMENT_PROCESS
- **Date:** 2026-10-05
- **Symptom:** first WP3 PR could not cleanly represent implementation history after WP2 squash merge.
- **Resolution:** close PR #29 without dropping product work; rebuild cleanly on merged main as PR #30.
- **Status:** resolved.

## FAIL-012 — Turbopack could not trace `../output` / `../reports`

- **Search terms:** `Turbopack`, `../output`, `../reports`, `artifact tracing`, `.careerhub-artifacts`, `build failure`
- **Class:** BUILD
- **Date:** 2026-10-05
- **Symptom:** fixture production build failed/warned because Next.js tracing crossed outside site root.
- **Root cause:** artifact delivery attempted to make external repository paths part of site bundle tracing.
- **Resolution:** PR #31 introduced `site/.careerhub-artifacts` mirror; PR #32 restricted tracing to that managed mirror.
- **Guard:** no broad whole-project artifact tracing; keep API path contract while deployment reads site-local mirror.
- **Status:** resolved.

## FAIL-013 — Final audit snapshot stale after external gates cleared

- **Search terms:** `WP10 blocked stale snapshot`, `final-audit-status`, `37436795188`, `WP01 WP09 PASS`
- **Class:** AUDIT_STATE
- **Date:** 2026-10-06
- **Symptom:** Household run showed WP01–WP09 PASS while WP10 remained blocked because final-audit snapshot still contained September blocker state.
- **Resolution:** PR #36 updated only the final-audit snapshot, followed by the required final-audit/regression path.
- **Current machine state:** all WP01–WP10 PASS; release 1.0 allowed.
- **Status:** resolved.

## FAIL-014 — HRDM action queued but browser had no completed-report return channel

- **Search terms:** `analysis queued no report`, `HRDM-R result missing`, `ACT reference only`, `202 QUEUED`, `WP39`
- **Class:** SURFACE / EXEC_PATH
- **Date:** 2026-10-06
- **Symptom:** Analyse could submit `analyse_role` and display an action reference, but user could not retrieve/render the completed report.
- **Root cause:** action dispatch existed without browser status/result retrieval closure.
- **WP:** WP39 / issue #39.
- **Resolution:** PR #40 added preflight, lifecycle, action-to-result binding and stable result retrieval.
- **Later hardening:** FAIL-018.
- **Status:** resolved at central/fleet level; WP40 still extends background process behaviour.

## FAIL-015 — Hybridianesque exposed as a normal-user expert switch

- **Search terms:** `Hybridianesque Yes No`, `Hy-Filter`, `user gate`, `auto relevance`
- **Class:** SURFACE / ARCH_DRIFT
- **Date:** 2026-10-06
- **Symptom:** normal user was expected to know whether an expert analytical filter should run.
- **Root cause:** HRDM codex gate was surfaced directly as product UX.
- **Resolution:** WP39/PR #40 moved relevance evaluation into Motor using the four validity criteria and evidence/confidence trace.
- **Later UX policy:** WP40 removes `Hybridianesque` terminology from normal interface entirely while keeping it internal.
- **Status:** central logic resolved; user-language cleanup remains WP40 acceptance.

## FAIL-016 — Repeated search could not distinguish “no new jobs” from stale/failed search

- **Search terms:** `no new jobs`, `search delta`, `NEW SEEN CHANGED`, `source health`, `same results`
- **Class:** SEARCH / SURFACE
- **Date:** 2026-10-06
- **Symptom:** repeated successful search and failed/stale search could look equivalent.
- **Root cause:** no persistent comparable search-session history/fingerprints.
- **Resolution:** WP39/PR #40 adds search-session persistence and delta classification (`NEW`, `SEEN`, `CHANGED`; source failure separated).
- **Later extension:** WP40 adds user-facing date/type/mode filters and persistent dismissals.
- **Status:** delta logic resolved; UX expansion open.

## FAIL-017 — Wish routing fragmented across profile sites/deployments

- **Search terms:** `Wish Bank`, `wish routing`, `CAREERHUB_WISH_ENDPOINT`, `WISH-ID`, `site project`
- **Class:** INTEGRATION / SURFACE
- **Date:** 2026-10-06
- **Symptom:** wish submission/deployment topology was fragmented and acceptance verification depended on infrastructure configuration.
- **Resolution path:** WP39/PR #40 added protected Wish Bank ledger/health readiness; one authoritative endpoint/topology required.
- **Status:** central close-loop implementation landed; deployment-specific verification remains relevant to operations.

## FAIL-018 — Analysis could be marked complete before result was durably stored/read back

- **Search terms:** `false completed`, `persistence before completion`, `GitHub read-back`, `HRDM materialization`, `b55547e`, `c08e639`
- **Class:** PERSISTENCE
- **Date:** 2026-10-06
- **Symptom:** generation success was not sufficient proof that a profile-owned result had been durably materialised and could be reopened.
- **Root cause:** completion semantics were tied too closely to generation/execution rather than durable repository state.
- **Resolution:** commits `b55547e` and `c08e639` require repository persistence/read-back before `COMPLETED`.
- **Production proof:** `ACT-20261006155733-2c2a00a7`, PID `HRDM-R-20261006-0001-S09-A-R01-FINAL`.
- **Canonical invariant:** `generation success != COMPLETED`.
- **Status:** resolved; must remain a regression invariant in WP40.

## FAIL-019 — Search Profile script/package import shadowing

- **Search terms:** `script import shadowing`, `Search Profile package resolution`, `direct script`, `import error`
- **Class:** BUILD / EXEC_PATH
- **Date:** 2026-10-06
- **Symptom:** direct script execution resolved package/module imports incorrectly in Search Profile tooling.
- **Resolution:** central fixes/regressions around script package resolution/import shadowing, including commits `7d6a36a`, `2476ce6`, `515335e`, `d9be7c4`.
- **Status:** resolved/regression protected.

## FAIL-020 — Synthetic WP39 E2E role remains visible in Weronika UI

- **Search terms:** `WP39 End-to-End Test Role`, `test residue`, `Weronika recent analyses`, `synthetic`
- **Class:** DATA_BOUNDARY / SURFACE
- **Date:** identified 2026-10-06
- **WP:** WP40
- **Symptom:** synthetic test role/result remains in user-facing Recent analyses.
- **Required fix:** bounded reset removes synthetic/test/transient residue while preserving genuine career/evidence data.
- **Status:** OPEN WP40 acceptance target.

## FAIL-021 — Grace Library upload/storage does not prove ACTIVE evidence use

- **Search terms:** `Grace upload`, `Library`, `ACTIVE source`, `indexed`, `storage-only`, `analysis evidence`
- **Class:** DATA_BOUNDARY / PERSISTENCE
- **Date:** identified 2026-10-06
- **WP:** WP40
- **Symptom:** upload/storage visibility is insufficient; source needs immediate indexing/status and proof that ACTIVE evidence enters analysis context.
- **Risk:** stored document falsely represented as evidence used.
- **Required invariant:** only profile-owned, successfully ingested, ACTIVE sources included in analysis evidence manifest.
- **Status:** OPEN WP40 acceptance target.

## FAIL-022 — Cross-profile Library access risk

- **Search terms:** `cross-profile`, `Library isolation`, `other profile source`, `Blob namespace`, `list open delete`
- **Class:** DATA_BOUNDARY
- **Date:** WP40
- **Symptom/risk:** Library namespace/API must prove one profile cannot list/open/delete another profile's source.
- **Required fix:** profile-scoped Blob namespace + fail-closed API regression tests.
- **Status:** OPEN WP40 acceptance target.

## FAIL-023 — Analysis execution still needs page/navigation independence

- **Search terms:** `analysis stops navigation`, `reload`, `background execution`, `active process`, `global process`
- **Class:** PERSISTENCE / SURFACE
- **Date:** WP40
- **Symptom/risk:** long-running analysis must not depend on the initiating page lifecycle.
- **Required fix:** durable ActiveProcess state immediately at launch; central/GitHub execution continues to terminal state; reload/navigation restores state; global process indicator links to result.
- **Status:** OPEN WP40 acceptance target.

## FAIL-024 — Search lacks ordinary job-site filtering/dismissal controls

- **Search terms:** `job type`, `remote hybrid onsite`, `published date`, `deadline`, `last month`, `dismiss`, `[×]`
- **Class:** SEARCH / SURFACE
- **Date:** WP40
- **Symptom:** search execution exists but controls remain less usable than a normal job-search site.
- **Required fix:** multi-select types, supported work modes, published/deadline windows, presets/custom dates, persistent dismissed job IDs, clear checked/new summary.
- **Status:** OPEN WP40 acceptance target.

## FAIL-025 — Internal Motor/HRDM terminology leaks into normal user experience

- **Search terms:** `HRDM-R UI`, `Hybridianesque UI`, `Motor terminology`, `implementation language`, `Job analysis`
- **Class:** SURFACE
- **Date:** WP40
- **Symptom:** product exposes internal implementation concepts normal users should not need to know.
- **Required fix:** user language `Analyse job opening` / `Job analysis`; internal HRDM/Hy logic retained only in technical/trace layers; Help written in product language.
- **Status:** OPEN WP40 acceptance target.

## FAIL-026 — GitHub issue state and functional/audit state diverge

- **Search terms:** `issue open but pass`, `WP01 open`, `WP10 open`, `audit PASS`, `status conflict`
- **Class:** AUDIT_STATE / DEVELOPMENT_PROCESS
- **Date:** current ledger reconstruction
- **Symptom:** several Silicon issues remain open even though `final-audit-status.json` records WP01–WP10 PASS.
- **Root cause:** issue workflow metadata was not reconciled when later machine/audit gates cleared.
- **Resolution in this history system:** never use issue `open/closed` as sole current-status truth; store `github_state` separately from `audit_status` and `release_state`.
- **Status:** documented; issue-hygiene cleanup remains optional governance work.

## FAIL-027 — 1.0 release permission differs from actual VERSION

- **Search terms:** `release_1_0_allowed`, `VERSION 0.2.9-alpha`, `1.0 released`, `WP10`
- **Class:** AUDIT_STATE / RELEASE_STATE
- **Date:** 2026-10-07 cut-off
- **Symptom:** final audit says `release_1_0_allowed: true`, but repository `VERSION` still reads `0.2.9-alpha` and WP10 issue is open.
- **Interpretation:** permission to release is not proof that the version/tag was actually released.
- **Ledger rule:** current release state comes from actual VERSION/tag/release evidence, not audit permission alone.
- **Status:** OPEN reconciliation point; do not falsely label 1.0 released.

---

# 3. Fast lookup by subsystem

| Subsystem | Failure IDs |
|---|---|
| Architecture / central Motor | 002, 003, 007, 015 |
| Distribution / GitHub | 003, 004, 018, 019 |
| OpenAI / HRDM | 001, 006, 014, 015, 018, 025 |
| Search | 010, 016, 019, 024 |
| Geography | 005 |
| Build / Next.js | 011, 012, 019 |
| Profile / evidence / Library | 007, 008, 020, 021, 022 |
| Audit / release | 013, 026, 027 |
| Vercel / deployment | 009, 017 |
| UI / usability | 010, 014, 015, 016, 020, 023, 024, 025 |

# 4. Required format for future failure entries

Every future failure should include:

```yaml
failure_id:
date_detected:
status:
class:
symptoms: []
search_terms: []
subsystems: []
affected_profiles: []
trigger:
root_cause:
resolution:
work_packages: []
issues: []
prs: []
commits: []
workflow_runs: []
regression_guard:
superseded_by:
notes:
```

This format is mirrored in the machine-readable development ledger.
