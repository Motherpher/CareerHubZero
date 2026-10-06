# CareerHubZero Development Provenance Map

**Provenance ID:** `CHZERO-PROVENANCE-001`  
**Cut-off:** 2026-10-07

## 1. Purpose

The development ledger combines evidence created for different purposes and at different times. This file defines how those sources are interpreted so historical snapshots are preserved without being mistaken for current state.

## 2. Evidence precedence

### Tier A — Current machine/runtime state

Use first for a claim about **what is current now**:

- `VERSION`
- `stack/household/final-audit-status.json`
- current `careerhub.yaml`/schemas/contracts
- current default-branch code and tests
- current profile-node files where profile state is relevant.

Tier A does not erase history. It only wins current-state reconciliation.

### Tier B — GitHub execution evidence

Use for what was **implemented, merged, failed or tested at a point in time**:

- GitHub issues
- PR titles/bodies/diffs
- merge state
- commits
- workflow-run IDs
- profile-repository cutover/sync commits.

### Tier C — Historical repository documents

Use as timestamped development snapshots:

- `CHANGELOG.md`
- `docs/MIGRATION.md`
- `docs/EXTRACTION_INVENTORY.md`
- `docs/SPRINT_1_0_SILICON_10WP.md`
- `docs/audit/*`
- `stack/releases/*`
- `stack/sprints/*`
- archived migration/readme/status files in profile repositories.

These files are allowed to contain old status such as `BLOCKED`, `ACTIVE` or `OPEN`. The ledger must mark the date rather than silently rewriting them.

### Tier D — Chat/design history

Use for:

- Director/user architectural decisions;
- decisions not fully represented in GitHub text;
- naming/alias history;
- live-testing observations that triggered a later issue;
- rationale for superseding an approach;
- WP designs written in chat before/after formal issue creation.

A chat-derived design must be labelled as such when it was not committed into the repository at that time.

## 3. Conflict rule

When two sources disagree:

1. ask whether they refer to the same date/state;
2. preserve both if one is a historical snapshot;
3. use current Tier A evidence for `current_reconciled_status`;
4. never modify an old audit merely to make it appear current;
5. record the superseding event.

Example:

```text
docs/MIGRATION.md: M4 Profile cutover = OPEN
          ↓ later implementation
Weronika/Grace cutover commits + PR #33
          ↓ current audit
final-audit-status.json: WP03 = PASS
```

The first statement is historically valid and the last statement is current.

## 4. Repository catalogue

### `Motherpher/CareerHubZero`

Role: canonical Motor/software body and history home.

High-value historical paths:

- `/CHANGELOG.md`
- `/VERSION`
- `/docs/ARCHITECTURE.md`
- `/docs/EXTRACTION_INVENTORY.md`
- `/docs/MIGRATION.md`
- `/docs/SPRINT_1_0_SILICON_10WP.md`
- `/docs/ACTION_COMPLETENESS_CONTRACT.md`
- `/docs/PERSONAL_WORKSPACE_PROFILE_LIBRARY_SEARCH.md`
- `/docs/DUAL_HUB_WEB_ARCHITECTURE.md`
- `/docs/audit/`
- `/stack/BACKLOG.yaml`
- `/stack/releases/`
- `/stack/sprints/CH-1.0-SILICON.yaml`
- `/stack/household/final-audit-status.json`
- GitHub issues/PRs #1–#41.

### `Motherpher/wpb`

Role: original working CareerHub and Weronika profile node.

Historical significance:

- origin of the first local CareerHub runtime;
- source of extraction inventory;
- early UX/search/job-vault/application lifecycle work;
- local Motor later removed under WP03;
- production E2E evidence for WP38–39;
- current thin-profile/fleet-sync evidence.

Key commits recorded in ledger include:

- `1db6126` — CareerHub overview;
- `c614bde` — Python package;
- `40257ea` — HRDM application drill;
- `aa5296d` — job vault/application state;
- `842b31c` — central Motor cutover;
- `92f861d` — migration metadata retirement;
- `74d6a60` — Motor close-loop fleet sync.

### `Motherpher/Gracey`

Role: Grace profile node and second legacy local-Motor migration case.

Historical significance:

- local CareerHub Motor introduced at `a0ebf75`;
- Grace-specific evidence/search/history preservation requirements;
- canonical search/profile/HRDM-manifest alignment;
- central cutover `1ff7dab`;
- migration/pre-firewall closure `066be5b`;
- personalisation/managed-site rollout;
- close-loop fleet sync `7bb9106`.

### `Motherpher/CareerHub-LinusF`

Role: Profile Node 001/reference thin profile and first personalised managed-site reference.

Historical significance:

- initial private profile deployment from issue #7;
- reference implementation of non-generic personalisation;
- managed-shell syncs;
- durable persistence/fleet rollout evidence;
- close-loop fleet sync `40e38ea`.

## 5. Work-package source map

### Silicon WP01–WP10

Primary sources:

1. `docs/SPRINT_1_0_SILICON_10WP.md` — detailed intended scope/deletion/exit gates.
2. `stack/sprints/CH-1.0-SILICON.yaml` — machine dependencies and issue mapping.
3. GitHub issues #1, #3, #4, #16, #17, #15, #18, #19, #20, #14.
4. `docs/audit/*` and `stack/household/final-audit-status.json` — temporal/final clearance.
5. profile repo commits — cutover/runtime proof.

### October execution packages

Primary sources:

- PR #27 — central managed workspace promotion;
- PR #28 — `WP2` interactive search activation;
- PR #29/#30 — `WP3` action surfaces/handoffs;
- PR #31/#32 — artifact/Turbopack hardening.

Ledger aliases `OCT-WP2` and `OCT-WP3` exist solely to prevent collision with Silicon WP02/WP03.

### WP38–WP40

Primary sources:

- issue #38 — formal `WP-CHM-UX-01`;
- issue #39 — formal `WP-CHM-OPS-02`;
- PR #40 — implementation unit explicitly titled `WP38–39`;
- subsequent durable persistence/search regression commits;
- fleet-sync profile commits;
- issue #41 — WP40 original scope;
- chat record — later four-sprint WP40 decomposition.

## 6. Commit inclusion policy

Git history remains the exhaustive commit source. The unified ledger indexes **development-significant commits**, meaning commits that change:

- architecture;
- contracts/schemas;
- WP state;
- runtime/deployment behaviour;
- failure state or remediation;
- evidence/privacy boundaries;
- profile cutover;
- build/regression integrity;
- user workflow.

Pure generated-data refreshes are not repeated in the narrative ledger unless they prove a failure or gate. They remain searchable in Git.

## 7. Required provenance fields for future entries

Every machine-readable event should, where available, carry:

```yaml
source_class: repo | issue | pr | commit | workflow | audit | chat
source_repository:
source_path:
source_number:
source_sha:
source_run_id:
source_date:
confidence: direct | reconciled | chat_only
historical_snapshot: true|false
```

This allows future tools to determine whether a statement is direct implementation evidence, a historical snapshot, or a later reconstruction.
