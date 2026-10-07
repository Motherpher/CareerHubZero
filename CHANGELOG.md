# CareerHubZero Changelog

The authoritative per-version content register is `stack/releases/<version>.yaml`.

## Changelog ID contract

Every release section and every individual change entry has a permanent identifier.

- Release ID: `CHZ-REL-<normalized-version>`
- Change ID: `CHZ-CHG-<normalized-version>-<ordinal>`
- `normalized-version` removes punctuation and represents `alpha` as `A`; for example `0.2.9-alpha` → `029A`.
- IDs are immutable once merged. If an entry is corrected or superseded, preserve its ID and add a new sourced change record rather than renumbering history.

## 0.2.9-alpha — 2026-09-25; repository recheck 2026-10-05
**Release ID:** `CHZ-REL-029A`  
**Household Silicon Sprint integration line + central profile cutover.**

- **`CHZ-CHG-029A-001`** Preserve the 2026-09-25 Household audit as the historical sprint snapshot.
- **`CHZ-CHG-029A-002`** Replace the blocked cross-repository composite-Action distribution path with checkout-based execution of CareerHubZero in profile repositories.
- **`CHZ-CHG-029A-003`** Clear WP02 after central-body compatibility passes for Weronika and Grace.
- **`CHZ-CHG-029A-004`** Rebind Weronika and Grace operational workflows to the central CareerHub motor.
- **`CHZ-CHG-029A-005`** Delete the duplicated local `src`, `scripts`, `hrdm` and requirements runtimes from both remaining profile nodes.
- **`CHZ-CHG-029A-006`** Clear WP03 after manifest-driven validation/rendering succeeds on both profile `main` branches.
- **`CHZ-CHG-029A-007`** Harden the action-complete managed web shell and artifact delivery path; scope artifact tracing to `.careerhub-artifacts`.
- **`CHZ-CHG-029A-008`** Canonicalise the user journey as Profile → Search → Analyse → Apply → Track, with Library and Improve my CareerHub as supporting workspaces.
- **`CHZ-CHG-029A-009`** Keep WP06, WP09 and WP10 blocked pending geography/routing and dependent end-gate proof.
- **`CHZ-CHG-029A-010`** Install WP40.0 sourced-development history enforcement: every substantive change set must carry a diff-bound provenance event before merge.
- **`CHZ-CHG-029A-011`** Establish WP40.1 server-resolved profile context with explicit repository binding and fail-closed deployment/profile mismatch handling.
- **`CHZ-CHG-029A-012`** Centralise profile-scoped Library namespace guards for list/open/upload/activate/deactivate/erase/reload operations.
- **`CHZ-CHG-029A-013`** Add the conservative WP40.1 reset classifier and dry-run/apply tooling with `PRESERVE`, `SYNTHETIC_DELETE`, `TRANSIENT_CLEAR`, `ORPHAN_REVIEW` and `UNKNOWN_BLOCK` classes.
- **`CHZ-CHG-029A-014`** Reconcile fleet binding metadata and legacy-Motor state, bind Linus/Weronika/Grace manifests to their repositories, and remove the known Weronika WP39 synthetic E2E ledger/report residue as a bounded reset unit.
- **`CHZ-CHG-029A-015`** Establish the WP40.2 governed Library lifecycle `UPLOADED → INGESTING → INDEXED → ACTIVE`, with explicit `INACTIVE`, `INGEST_FAILED` and `ERASED` exception states.
- **`CHZ-CHG-029A-016`** Add server-side document extraction/indexing and analysis evidence-use manifests so only successfully indexed ACTIVE profile-owned Library sources can enter a job analysis.
- **`CHZ-CHG-029A-017`** Make Job Analysis navigation/reload-safe through a durable action record, stable `/analyse/<action-id>` result address and global background-process tray while preserving repository read-back before `COMPLETED`.
- **`CHZ-CHG-029A-018`** Replace normal-user HRDM-R/Hybridianesque execution language with product language (`Analyse job opening` / `Job analysis`) and expose the normal 2–5 minute report window.
- **`CHZ-CHG-029A-019`** Establish WP40.3 profile-scoped persistent Search workspace filters for job type, work mode, published date and application deadline, including 1-week/1-month/2-month/3-month presets and a bounded default deadline horizon.
- **`CHZ-CHG-029A-020`** Add profile-scoped persistent vacancy dismiss/restore decisions so rejected search results stay hidden across reloads and repeated searches until explicitly restored.
- **`CHZ-CHG-029A-021`** Evolve Search run sessions to schema 1.1 with filter-sensitive comparison keys, preserved `NEW / SEEN / CHANGED` semantics, separate source-failure handling and checked/matched/new/changed/dismissed completion counts.
- **`CHZ-CHG-029A-022`** Rebuild the Search workspace around ordinary job-site controls while preserving the direct real-vacancy handoff into the existing durable Job Analysis pipeline.

## 0.2.7-alpha — 2026-09-24
**Release ID:** `CHZ-REL-027A`  
**Integrated execution spine + HRDM report/ledger lifecycle.**

- **`CHZ-CHG-027A-001`** Add one manifest-driven central CLI spanning sourcing through rendering.
- **`CHZ-CHG-027A-002`** Add central composite GitHub Action for profile-side execution.
- **`CHZ-CHG-027A-003`** Add canonical HRDM Process-ID/run-registry support.
- **`CHZ-CHG-027A-004`** Add HRDM active report shelf and immutable historical ledger.
- **`CHZ-CHG-027A-005`** Archive reports from the active shelf after vacancy deadline while retaining history.
- **`CHZ-CHG-027A-006`** Add HRDM Markdown, DOCX and PDF artifacts.
- **`CHZ-CHG-027A-007`** Install Hybridianesque Hy-Filter as an optional, explicitly gated HRDM depth filter.
- **`CHZ-CHG-027A-008`** Preserve precise vacancy address/coordinates for geotagging.
- **`CHZ-CHG-027A-009`** Add search-profile normalization across all active profile-node shapes.
- **`CHZ-CHG-027A-010`** Add executable capability audit and explicit remaining 1.0 blockers.

## 0.2.6-alpha — 2026-09-24
**Release ID:** `CHZ-REL-026A`  
**Unified CareerHub body architecture.**

- **`CHZ-CHG-026A-001`** Replace the permanent engine + stack-lock model with one CareerHub software body and one VERSION.
- **`CHZ-CHG-026A-002`** Add versionless `careerhub.yaml` manifests to Linus, Weronika and Grace.
- **`CHZ-CHG-026A-003`** Make `instance.yaml` and `stack.lock.yaml` migration-only artifacts.
- **`CHZ-CHG-026A-004`** Remove cross-repository version propagation from the stable release path.
- **`CHZ-CHG-026A-005`** Remove `CAREERHUB_STACK_TOKEN` as a stable architecture requirement.
- **`CHZ-CHG-026A-006`** Add unified-body validation and a 1.0 Full Audit Lock guard.
- **`CHZ-CHG-026A-007`** Begin centralising reusable Grace/Weronika runtime modules into CareerHubZero.

## 0.2.5-alpha — 2026-09-24
**Release ID:** `CHZ-REL-025A`  
**Precision-aware vacancy geotagging + zoom-aware map aggregation.**

- **`CHZ-CHG-025A-001`** Add Google Places API (New) geotagging adapter for sourced vacancies.
- **`CHZ-CHG-025A-002`** Prefer source coordinates and explicit vacancy addresses before broader locality geocoding.
- **`CHZ-CHG-025A-003`** Preserve geographic precision instead of inventing street-level locations.
- **`CHZ-CHG-025A-004`** Add zoom-aware country/region/locality clusters and high-zoom point expansion.
- **`CHZ-CHG-025A-005`** Track both total jobs and newly sourced jobs in cluster payloads.
- **`CHZ-CHG-025A-006`** Add canonical job-geo schema, CLI and unit tests.
- **`CHZ-CHG-025A-007`** Reserve country-matrix enrichment as a separate, provider-independent layer.

## 0.2.4-alpha — 2026-09-24
**Release ID:** `CHZ-REL-024A`  
**Grace stack recovery + Motherpher ownership and 1.0 audit-lock governance.**

- **`CHZ-CHG-024A-001`** Register Grace as the third active CareerHub profile instance.
- **`CHZ-CHG-024A-002`** Correct stale central engine metadata from 0.2.2-alpha to the current line.
- **`CHZ-CHG-024A-003`** Require Grace pre-firewall application artifacts to be revalidated before external use.
- **`CHZ-CHG-024A-004`** Expand 0.3.0-alpha cutover scope to both WPB and Grace legacy motors.
- **`CHZ-CHG-024A-005`** Set Motherpher ownership as the repository boundary for all CareerHub repositories; ownership migration completed for Linus, Weronika and Grace.
- **`CHZ-CHG-024A-006`** Define CareerHubZero 1.0.0 as the Full Audit Lock release, not a feature-count milestone.
- **`CHZ-CHG-024A-007`** Correct the example candidate profile to use the canonical `verification_queue` field.

## 0.2.3-alpha — 2026-09-24
**Release ID:** `CHZ-REL-023A`  
**Verified-career evidence firewall + search-only user raster.**

- **`CHZ-CHG-023A-001`** Hard-block private-life fields from the matchable candidate profile.
- **`CHZ-CHG-023A-002`** Require every matchable claim to bind to a verified, permitted career source.
- **`CHZ-CHG-023A-003`** Separate user-entered "specific wishes or needs" into a search-only overlay.
- **`CHZ-CHG-023A-004`** Forbid the search overlay from becoming CV evidence, HRDM proof points or application claims.
- **`CHZ-CHG-023A-005`** Add runtime policy validation and regression tests.
- **`CHZ-CHG-023A-006`** Tighten candidate/search schemas and profiled-instance documentation.

## 0.2.2-alpha — 2026-09-24
**Release ID:** `CHZ-REL-022A`  
**Harmonised stack version governance.**

- **`CHZ-CHG-022A-001`** Establish `VERSION` as the single motor-version source.
- **`CHZ-CHG-022A-002`** Add full stack registry.
- **`CHZ-CHG-022A-003`** Add per-version machine-readable release ledger/backlog.
- **`CHZ-CHG-022A-004`** Add generated profile `stack.lock.yaml`.
- **`CHZ-CHG-022A-005`** Add central remote sync and compatibility checks.
- **`CHZ-CHG-022A-006`** Block stack release if an active profile is behind or contains its own motor.
- **`CHZ-CHG-022A-007`** Remove independent package-version drift.

## 0.2.1-alpha — 2026-09-24
**Release ID:** `CHZ-REL-021A`  
**Base-contract drift correction.**

- **`CHZ-CHG-021A-001`** Restore canonical user flow: Find → Analyse? → Apply.
- **`CHZ-CHG-021A-002`** Remove Napp/market-response as a base CareerHub command/subsystem.
- **`CHZ-CHG-021A-003`** Restore job vault + applications as canonical state core.
- **`CHZ-CHG-021A-004`** Preserve evidence-bounded profile support.

## 0.2.0-alpha — 2026-09-24
**Release ID:** `CHZ-REL-020A`  
**Profiled-instance expansion.**

- **`CHZ-CHG-020A-001`** Add profile/search/evidence contracts and instance loader.
- **`CHZ-CHG-020A-002`** Add dashboard renderer.
- **`CHZ-CHG-020A-003`** Add experimental market-response layer later identified as base-contract drift.

## 0.1.0-alpha — 2026-09
**Release ID:** `CHZ-REL-010A`  
**Centralisation baseline.**

- **`CHZ-CHG-010A-001`** Establish CareerHubZero.
- **`CHZ-CHG-010A-002`** Define central operations vs profiled instance boundary.
- **`CHZ-CHG-010A-003`** Preserve HRDM core and migration plan from WPB.
