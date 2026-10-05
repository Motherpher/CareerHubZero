# CareerHub Repository Gate Recheck — 2026-10-05

## Purpose

This document is a dated supplement to `CAREERHUB_HOUSEHOLD_SPRINT_AUDIT_2026-09-25.md`. It does **not** rewrite the September audit. It records repository-side evidence that changed the status of WP02 and WP03 after that audit.

The recheck is deliberately bounded to work that can be proven from GitHub repositories and GitHub Actions. Vercel deployment state, live production aliases and Vercel environment configuration are outside this recheck.

## Executive verdict

**Repository gate verdict: BLOCKED, with WP02 and WP03 cleared and formally closed.**

The historical distribution and profile-cutover blockers are resolved. CareerHub now has one authoritative central runtime in `Motherpher/CareerHubZero`; active profile nodes consume that runtime through checkout-based execution against their own manifest and no longer require authoritative local runtime copies.

The remaining Silicon Sprint blockers are not WP02/WP03. WP06 still requires live geography/routing proof; WP09 remains dependent on WP06; WP10 remains dependent on the incomplete downstream gate set.

Fresh Household Director run `37347655415` independently produced:

```text
WP01 PASS
WP02 PASS
WP03 PASS
WP04 PASS
WP05 PASS
WP06 BLOCKED
WP07 PASS
WP08 PASS
WP09 BLOCKED
WP10 BLOCKED
```

The Household workflow therefore remains red by design while WP06/WP09/WP10 are unresolved; that red overall result does not reopen WP02 or WP03.

## Re-evaluated work packages

| WP | 2026-09-25 | 2026-10-05 repository recheck | Basis |
|---|---|---|---|
| WP01 — Collapse Runtime to One CareerHub Body | PASS | PASS (carried forward) | Not reopened by this recheck. Central runtime remains canonical. |
| WP02 — Invert Distribution | BLOCKED | **PASS / CLOSED** | Private composite-Action sharing was replaced by checkout-based central-body execution in both remaining profile repos. Silicon issue #3 is closed as completed. |
| WP03 — Cut Over Profiles and Delete Legacy Motors | BLOCKED | **PASS / CLOSED** | Weronika and Grace workflows execute CHZero; duplicate runtimes and migration-only locks are removed; profile-owned state validates/renders successfully on `main`. Silicon issue #4 is closed as completed. |
| WP04 — Unify Search Kernel | PASS | PASS (carried forward) | Not reopened by this recheck. |
| WP05 — Career Learning Loop | PASS | PASS (carried forward) | Not reopened by this recheck. |
| WP06 — Unified Geography | BLOCKED | **BLOCKED** | Live Maps/routing and full geography end-to-end proof remain outstanding. |
| WP07 — Canonical HRDM | PASS | PASS (carried forward) | Not reopened by this recheck. |
| WP08 — One Application and Outcome State Machine | PASS | PASS (carried forward) | Not reopened by this recheck. |
| WP09 — One Hub Surface | BLOCKED | **BLOCKED** | Dependency on WP06 is still unmet. |
| WP10 — Contract Audit and Lock CareerHub 1.0 | BLOCKED | **BLOCKED** | Full downstream/end-audit gate cannot close while WP06/WP09 remain blocked. |

## WP02 evidence — distribution inversion

### Weronika Pérez Borjas

- Repository: `Motherpher/wpb`
- WP02 merge commit: `d03a96e8bc0917164659809cf8c67607793ee371`
- Compatibility run: `37343374586` — success
- Native profile validation run: `37343374408` — success

The profile no longer depends on `uses: Motherpher/CareerHubZero@main` as a cross-repository composite Action. The compatibility workflow checks out `Motherpher/CareerHubZero`, installs the canonical requirements and executes the central CLI against `CareerHub/careerhub.yaml`.

### Grace

- Repository: `Motherpher/Gracey`
- WP02 merge commit: `413adadf4e8906d193e028e0ab1c1a4b6d3ba2e0`
- Compatibility run: `37343394541` — success
- Native profile validation run: `37343394582` — success

The same checkout-based distribution path succeeds for Grace.

### WP02 conclusion

The September blocker — private CareerHubZero Action access to profile repositories — is no longer part of the current architecture. Distribution is inverted without requiring central write-back tokens or cross-repository composite-Action access.

Silicon issue `#3` was closed as **completed** on 2026-10-05 after the fresh Household Director run also returned WP02 PASS.

**WP02: PASS / CLOSED.**

## WP03 evidence — profile cutover and legacy motor deletion

### Weronika Pérez Borjas

Initial central-motor cutover:
- merge commit: `842b31c477fdd083b109d4e43bc80bd3d448f421`
- post-cutover validation: `37345897861` — success
- post-cutover compatibility: `37345897747` — success

Final WP03 closure cleanup:
- merge commit: `92f861dc4a29b1f52e92914297bb1b9135faf7fe`
- `Validate CareerHub`: `37348625867` — success
- unified-body compatibility: `37348625998` — success
- WPB archive validation: `37348626242` — success

Removed from active CareerHub paths:
- `CareerHub/src`
- `CareerHub/scripts`
- `CareerHub/hrdm`
- `CareerHub/requirements.txt`
- `CareerHub/instance.yaml`
- `CareerHub/stack.lock.yaml`

Rebound to central execution:
- manual drill/application pack
- scheduled job scan
- issue-driven HRDM/application flow
- application status updates
- deadline reminders
- OpenAI diagnostic
- profile validation/rendering

Preserved as profile-owned state/context:
- manifest
- verified profile/evidence
- search configuration
- job and application state
- HRDM ledger
- reports/output/history
- repository-specific research/archive material

### Grace

Initial central-motor cutover:
- merge commit: `1ff7dabb7aa004fd7c325026ffc33607468bb107`
- post-cutover compatibility: `37345918372` — success
- post-cutover profile validation/rendering: `37345918421` — success

Final WP03 closure cleanup:
- merge commit: `066be5b3e4da5697c745ccfb487318ed17352bd0`
- post-cleanup validation/rendering: `37348650361` — success
- post-cleanup unified-body compatibility: `37348650378` — success

Removed from active CareerHub paths:
- `CareerHub/src`
- `CareerHub/scripts`
- `CareerHub/hrdm`
- `CareerHub/requirements.txt`
- `CareerHub/instance.yaml`
- `CareerHub/stack.lock.yaml`

The validation gate is manifest-driven: it checks the profile/search/state paths declared by `CareerHub/careerhub.yaml` rather than assuming another profile's filenames. Grace-specific Swedish interaction copy remains profile-side.

The historical Region Stockholm pre-firewall application pack is now formally retired rather than merely quarantined. Repository state records `pre_firewall_artifact_retired` and `external_use_allowed: false`. The job/case remains saved for history and can only produce a future application through a completely fresh current-policy central CareerHub run.

### Linus

Linus was already a thin central-body profile node. The final steady-state shell/CI hardening was merged as:
- commit `cd7d0933ca848274321f01f3f236309319fa941d`
- post-merge managed-shell parity + protected-personalisation + production build run `37348676752` — success

The site-build workflow is now read-only: it syncs CHZero into the CI workspace to detect drift, verifies `personalisation/**` and `site/personal/**` are untouched, and builds the committed shell. It no longer commits or pushes managed-shell changes from CI.

### WP03 conclusion

All three active profiles are thin nodes executing the same central CareerHub body. The two duplicated local motors are gone, obsolete migration locks are gone, active operations are rebound centrally, and profile-owned evidence/search/state/history remain intact.

Silicon issue `#4` was closed as **completed** on 2026-10-05. Fresh Household Director run `37347655415` returned WP03 PASS.

**WP03: PASS / CLOSED.**

## Central runtime hardening evidence

The central WP3 action-completeness line was also revalidated before this recheck:

- artifact-delivery hotfix merge: `6644e067839e88313400b4a26b49a5d3ff54e52c`
- central validation run `37340409335` — success, including production Next.js build
- artifact-tracing hardening merge: `ad348d46753c58f2eebc85e0eff500609a118979`
- central validation run `37343706733` — success
- audit/control recheck merge: `b4b87cfc7a07ebddd3eeee0af8ab3242e241a5de`
- central validation run `37347655464` — success

The artifact API scopes output tracing to the managed `.careerhub-artifacts` mirror rather than tracing parent directories or the whole project.

## Current blocker set after recheck

### Still blocking

1. **WP06 — Unified Geography**
   - live Google Maps/routing proof
   - full geography end-to-end execution evidence

2. **WP09 — One Hub Surface**
   - remains downstream of WP06
   - repository architecture can continue to harden, but WP09 cannot receive final PASS while the geography dependency is open

3. **WP10 — Contract Audit and Lock CareerHub 1.0**
   - requires the full dependency chain to pass
   - stable `1.0.0` remains prohibited

### External proof still outstanding

- live OpenAI HRDM/application execution after the previous API-credit exhaustion remains an external proof item

### No longer current blockers

- private CareerHubZero composite-Action access
- Weronika local-motor cutover
- Grace local-motor cutover
- duplicate authoritative runtime under either remaining profile node
- obsolete `instance.yaml` / `stack.lock.yaml` profile migration locks
- Grace's old pre-firewall application artifact as an active reusable asset

## Repository architecture after cutover

```text
Motherpher/CareerHubZero
  └── canonical runtime + contracts + managed shell

Motherpher/CareerHub-LinusF
  └── profile/search/state/personalisation + managed shell

Motherpher/wpb
  └── CareerHub profile/search/state/history + repository research archive
      runtime: checked out from CareerHubZero when workflows execute

Motherpher/Gracey
  └── CareerHub profile/search/state/history + profile-specific Swedish interaction layer
      runtime: checked out from CareerHubZero when workflows execute
```

## Status rule

This recheck supersedes the **current-state interpretation** of WP02/WP03 in the 2026-09-25 audit, but it does not alter the historical audit record. Any later release ledger or audit should cite both documents when explaining the transition from BLOCKED to PASS.

## Recheck result

```text
WP01 PASS
WP02 PASS / CLOSED   ← changed from historical BLOCKED
WP03 PASS / CLOSED   ← changed from historical BLOCKED
WP04 PASS
WP05 PASS
WP06 BLOCKED
WP07 PASS
WP08 PASS
WP09 BLOCKED
WP10 BLOCKED

1.0.0 release allowed: NO
```
