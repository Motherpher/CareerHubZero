# CareerHubZero Changelog

The authoritative per-version content register is `stack/releases/<version>.yaml`.

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
