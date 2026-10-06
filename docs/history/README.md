# CareerHubZero History & Failure Search

This directory is the canonical human-readable entry point for CareerHub/CareerHubZero development history.

## Start here

### I know roughly **when** something happened

Open [`CHZERO_DEVELOPMENT_LEDGER.md`](./CHZERO_DEVELOPMENT_LEDGER.md).

It reconstructs the full development line from the original WPB CareerHub on 2026-09-23 through CareerHubZero centralisation, the Silicon sprint, profile cutovers, personalised web rollout, WP38–39 and the open WP40 line.

### I know the **WP**

Open [`CHZERO_WP_REGISTRY.md`](./CHZERO_WP_REGISTRY.md).

Important: WP naming has multiple generations. The registry resolves collisions such as:

- Silicon `WP02` vs October PR-title `WP2`;
- Silicon `WP03` vs October PR-title `WP3`;
- chat/project aliases `WP38`/`WP39` vs formal GitHub titles `WP-CHM-UX-01` / `WP-CHM-OPS-02`.

### Something has **failed** and I only know the symptom

Open [`CHZERO_FAILURE_SEARCH_INDEX.md`](./CHZERO_FAILURE_SEARCH_INDEX.md).

Search using observed words, not assumed architecture. Examples:

```text
analysis completed no report
repository not found
429 credit_balance_exhausted
Turbopack output reports
no new jobs
Grace upload active evidence
cross profile library
WP39 End-to-End Test Role
VERSION 0.2.9 1.0
```

Each failure record resolves symptom → class → root cause → fix → WP/PR/commit → regression/current state.

### I need to know **which source is authoritative**

Open [`CHZERO_PROVENANCE_MAP.md`](./CHZERO_PROVENANCE_MAP.md).

It defines the evidence hierarchy and the rule for historical documents whose old status is still correct for its date but no longer current.

## Machine-readable indexes

For scripts/agents/grep/search tooling:

- [`../../stack/history/development-ledger.yaml`](../../stack/history/development-ledger.yaml)
- [`../../stack/history/wp-registry.yaml`](../../stack/history/wp-registry.yaml)
- [`../../stack/history/failure-index.yaml`](../../stack/history/failure-index.yaml)

## Status rule

Never collapse these into one field:

```text
status_at_event
current_reconciled_status
github_state
audit_status
release_state
```

Examples:

- a historical migration file can correctly say `OPEN` while later audit evidence says `PASS`;
- a GitHub issue may remain open despite implementation being merged;
- `release_1_0_allowed: true` does not prove `1.0.0` was actually released while `VERSION` remains `0.2.9-alpha`.

## Future maintenance rule

A development-significant WP/failure is not considered historically closed until its ledger entry contains:

1. trigger/problem;
2. affected subsystem/profile;
3. intended WP scope;
4. implementation evidence;
5. failure/root cause where applicable;
6. fix/supersession;
7. regression guard;
8. temporal and current status;
9. provenance links.

Do not delete old failures because they are fixed. Mark them resolved and preserve the search trail.
