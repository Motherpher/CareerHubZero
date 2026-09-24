# CareerHubZero Changelog

The authoritative per-version content register is `stack/releases/<version>.yaml`.

## 0.2.6-alpha — 2026-09-24
**Unified CareerHub body architecture.**

- Replace the permanent engine + stack-lock model with one CareerHub software body and one VERSION.
- Add versionless `careerhub.yaml` manifests to Linus, Weronika and Grace.
- Make `instance.yaml` and `stack.lock.yaml` migration-only artifacts.
- Remove cross-repository version propagation from the stable release path.
- Remove `CAREERHUB_STACK_TOKEN` as a stable architecture requirement.
- Add unified-body validation and a 1.0 Full Audit Lock guard.
- Begin centralising reusable Grace/Weronika runtime modules into CareerHubZero.

## 0.2.5-alpha — 2026-09-24
**Precision-aware vacancy geotagging + zoom-aware map aggregation.**

- Add Google Places API (New) geotagging adapter for sourced vacancies.
- Prefer source coordinates and explicit vacancy addresses before broader locality geocoding.
- Preserve geographic precision instead of inventing street-level locations.
- Add zoom-aware country/region/locality clusters and high-zoom point expansion.
- Track both total jobs and newly sourced jobs in cluster payloads.
- Add canonical job-geo schema, CLI and unit tests.
- Reserve country-matrix enrichment as a separate, provider-independent layer.

## 0.2.4-alpha — 2026-09-24
**Grace stack recovery + Motherpher ownership and 1.0 audit-lock governance.**

- Register Grace as the third active CareerHub profile instance.
- Correct stale central engine metadata from 0.2.2-alpha to the current line.
- Require Grace pre-firewall application artifacts to be revalidated before external use.
- Expand 0.3.0-alpha cutover scope to both WPB and Grace legacy motors.
- Set Motherpher ownership as the repository boundary for all CareerHub repositories; ownership migration completed for Linus, Weronika and Grace.
- Define CareerHubZero 1.0.0 as the Full Audit Lock release, not a feature-count milestone.
- Correct the example candidate profile to use the canonical `verification_queue` field.

## 0.2.3-alpha — 2026-09-24
**Verified-career evidence firewall + search-only user raster.**

- Hard-block private-life fields from the matchable candidate profile.
- Require every matchable claim to bind to a verified, permitted career source.
- Separate user-entered "specific wishes or needs" into a search-only overlay.
- Forbid the search overlay from becoming CV evidence, HRDM proof points or application claims.
- Add runtime policy validation and regression tests.
- Tighten candidate/search schemas and profiled-instance documentation.

## 0.2.2-alpha — 2026-09-24
**Harmonised stack version governance.**

- Establish `VERSION` as the single motor-version source.
- Add full stack registry.
- Add per-version machine-readable release ledger/backlog.
- Add generated profile `stack.lock.yaml`.
- Add central remote sync and compatibility checks.
- Block stack release if an active profile is behind or contains its own motor.
- Remove independent package-version drift.

## 0.2.1-alpha — 2026-09-24
**Base-contract drift correction.**

- Restore canonical user flow: Find → Analyse? → Apply.
- Remove Napp/market-response as a base CareerHub command/subsystem.
- Restore job vault + applications as canonical state core.
- Preserve evidence-bounded profile support.

## 0.2.0-alpha — 2026-09-24
**Profiled-instance expansion.**

- Add profile/search/evidence contracts and instance loader.
- Add dashboard renderer.
- Added experimental market-response layer later identified as base-contract drift.

## 0.1.0-alpha — 2026-09
**Centralisation baseline.**

- Establish CareerHubZero.
- Define central operations vs profiled instance boundary.
- Preserve HRDM core and migration plan from WPB.
