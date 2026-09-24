# Migration: Profile-Local CareerHubs → Unified CareerHub Body

## Objective

Move all reusable capability into one CareerHub software body while preserving person-specific evidence, search settings, state and provenance.

## Stable target

```text
Motherpher/CareerHubZero      one software body + one VERSION
Motherpher/CareerHub-LinusF   profile node + careerhub.yaml
Motherpher/wpb/CareerHub      profile node + careerhub.yaml
Motherpher/Gracey/CareerHub   profile node + careerhub.yaml
```

Profile nodes are not independently versioned.

## Current migration state

### Linus
- versionless `careerhub.yaml` installed,
- no profile-local CareerHub motor,
- canonical verified-evidence profile,
- suitable as the first stable thin-profile reference.

### Weronika
- versionless `CareerHub/careerhub.yaml` installed,
- canonical verified-evidence profile,
- local runtime/HRDM still present as migration code,
- cutover to central reusable body still required.

### Grace
- versionless `CareerHub/careerhub.yaml` installed,
- canonical evidence/search contract,
- 159-job history preserved,
- pre-firewall application quarantined,
- local runtime/HRDM still present as migration code,
- cutover to central reusable body still required.

## Migration sequence

### M0 — Governance and evidence firewall
Status: **COMPLETE**

### M1 — Unified body contract
Status: **COMPLETE**

- one VERSION,
- versionless profile manifests,
- no stable stack-lock requirement,
- no central cross-repository version propagation,
- `CAREERHUB_STACK_TOKEN` removed from stable architecture.

### M2 — Central runtime extraction
Status: **ACTIVE**

Reusable modules from Grace/Weronika are being moved into CareerHubZero:

- sourcing,
- matching,
- HRDM,
- application generation,
- state lifecycle,
- rendering,
- notifications,
- issue/update parsing.

### M3 — Reusable distribution
Status: **OPEN**

Create the central reusable action/workflow interface used by all profile repositories.

The caller profile repository writes its own state with its own `GITHUB_TOKEN`.

### M4 — Profile cutover
Status: **OPEN**

For Weronika and Grace:

1. run central body against existing state,
2. compare outputs/state transitions,
3. repair any parity differences,
4. switch workflows to central reusable execution,
5. remove profile-local Python/HRDM runtime,
6. archive/remove `instance.yaml` and `stack.lock.yaml`.

### M5 — Geography completion
Status: **ACTIVE**

Complete global map selection, geotagging, country-adapter registry, Sweden/SCB adapter, radius/travel-time and progressive widening.

### M6 — Full Audit Lock
Status: **NOT STARTED**

Run `docs/AUDIT_1.0.md` against the entire CareerHub body and Linus/Weronika/Grace compatibility suite.

Only a complete PASS permits `VERSION = 1.0.0`.

## Non-goals

- No private-life data enters candidate evidence.
- No search wish becomes candidate evidence.
- No profile repository carries an independent CareerHub software version.
- No cross-profile write token is required for normal CareerHub operation.
