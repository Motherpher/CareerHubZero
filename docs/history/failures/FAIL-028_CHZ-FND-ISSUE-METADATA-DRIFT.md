# FAIL-028 — CHZ-FND-ISSUE-METADATA-DRIFT

**Date detected:** 2026-09-24  
**Class:** `AUDIT_STATE` / development governance  
**Status:** `HISTORICAL_GOVERNANCE_FINDING`

## Symptom

GitHub issue metadata/state did not reliably represent the actual development state of CareerHubZero as architecture, audit clearance and implementation progressed.

Search terms:

- `CHZ-FND-ISSUE-METADATA-DRIFT`
- `issue metadata drift`
- `stale issue state`
- `governance drift`
- `issue open but implementation complete`

## Root cause

Issue workflow metadata, historical documents, implementation status, audit status and release status were evolving independently without one canonical reconciliation model.

This later became visible at larger scale when several Silicon WP issues remained open while `stack/household/final-audit-status.json` recorded WP01–WP10 as PASS.

## Resolution in the unified history system

The development ledger does not use a single generic `status` field. It separates:

- `status_at_event`
- `current_reconciled_status`
- `github_state`
- `audit_status`
- `release_state`

The WP registry also separates canonical WP identity from GitHub issue numbering, preventing issue metadata from becoming the sole historical authority.

## Regression guard

Future WPs/failures must enter the canonical WP/development ledger with provenance and temporal/current status explicitly separated.

## Superseded by

`CHZERO-DEV-LEDGER-001` and `CHZERO-WP-REGISTRY-001`.
