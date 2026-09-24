# Migration: Profile-Local CareerHubs → CareerHubZero

## Objective

Move all reusable CareerHub capability into `Motherpher/CareerHubZero` while preserving each person's verified career evidence, search configuration, job/application state, historical provenance and user-facing surfaces.

## Current Motherpher topology

```text
Motherpher/CareerHubZero
Motherpher/CareerHub-LinusF
Motherpher/wpb
  └── CareerHub/          Weronika bounded instance
Motherpher/Gracey
  └── CareerHub/          Grace bounded instance
```

Repository ownership migration is complete.

## Current profile-contract state

### Linus
- canonical `0.2.4-alpha` engine binding,
- canonical verified-evidence profile,
- canonical search-only overlay,
- no profile-local CareerHub motor,
- stack lock: aligned.

### Weronika
- canonical `0.2.4-alpha` engine binding,
- parallel verified-evidence profile at `CareerHub/profile/candidate_verified.yaml`,
- canonical search profile at `CareerHub/config/search_profile.yaml`,
- legacy candidate/profile files retained only for the temporary local runtime,
- profile-local motor still present,
- stack lock: blocked pending central-motor cutover.

### Grace
- canonical `0.2.4-alpha` engine binding,
- canonical verified-evidence profile,
- canonical search profile,
- 159-job historical vault preserved,
- Region Stockholm pre-firewall application artifact quarantined,
- profile-local motor still present,
- stack lock: blocked pending central-motor cutover.

## Migration sequence

### M0 — Central governance
Status: **COMPLETE**

- central architecture and instance boundary,
- verified-career evidence firewall,
- search-only raster,
- stack registry and locks,
- release/version governance,
- Motherpher ownership boundary,
- 1.0 Full Audit Lock.

### M1 — Extract pure reusable core
Status: **OPEN**

Move/generalise from legacy profile motors into CareerHubZero:

- source adapters,
- normalisation/deduplication,
- matching/triage,
- HRDM execution,
- application generation,
- document generation,
- state transitions,
- dashboard/rendering,
- workflow/bootstrap logic.

No person-specific assumptions may enter central core.

### M2 — Remove repository/person hard-coding
Status: **OPEN**

The same CareerHubZero runtime must operate against Linus, Weronika and Grace by instance configuration only.

### M3 — Reusable workflow layer
Status: **OPEN**

Profile repositories should call centrally governed reusable workflows rather than maintain independent workflow logic.

### M4 — Canonical profile contracts
Status: **COMPLETE for 0.2.4**

All three active instances now have a CareerHubZero-compatible engine binding and verified-evidence candidate path.

Legacy runtime profile files may temporarily coexist only where required for dual-run migration.

### M5 — Historical/state preservation
Status: **COMPLETE for migration baseline**

Grace:
- 159-job history preserved,
- issue #2 preserved after transfer,
- pre-firewall application state marked `external_use_allowed=false`.

Weronika:
- corpus, credits, job/application state and broader WPB provenance remain preserved in `Motherpher/wpb`.

### M6 — Dual-run parity
Status: **OPEN**

For controlled jobs, compare legacy runtime and CareerHubZero on:

1. source normalisation,
2. triage,
3. HRDM structure,
4. candidate-evidence use,
5. application artifact generation,
6. state transitions,
7. rendered user surfaces.

Run separately for Weronika and Grace.

### M7 — Repository relocation to Motherpher
Status: **COMPLETE**

- `Hybrismannen/Gracey` → `Motherpher/Gracey`
- `Hybrismannen/wpb` → `Motherpher/wpb`
- central registry repointed,
- connector access verified,
- Grace transferred issue links repaired.

Repository renaming is cosmetic and non-blocking.

### M8 — Central-motor cutover
Status: **BLOCKED by M1–M3 and M6**

After parity:
- remove `CareerHub/src/careerhub` from Grace and Weronika,
- remove profile-local runners and HRDM copies,
- retire legacy runtime-only profile/config copies,
- regenerate aligned stack locks,
- make CareerHubZero the only authoritative runtime.

### M9 — Full audit and 1.0 lock
Status: **NOT STARTED**

Run `docs/AUDIT_1.0.md` against CareerHubZero + Linus + Weronika + Grace.

Only a full PASS permits `VERSION = 1.0.0`.

## Non-goals

Migration does not move private-life data into CareerHub, does not convert search wishes into evidence, and does not delete historical state merely because it predates the current runtime.
