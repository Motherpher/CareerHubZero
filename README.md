# CareerHubZero

**Canonical software body for CareerHub.**

CareerHubZero is the single reusable software body behind every CareerHub profile node. It owns sourcing, geography, matching, HRDM-R, application generation, state contracts, rendering, reusable workflows, schemas and release governance.

A profile node owns only verified career evidence, search settings, durable state and generated artifacts. It exposes a versionless `careerhub.yaml` manifest and does not fork or independently version CareerHub.

## User contract

**1. Find jobs → 2. Analyse? → 3. Apply**

Everything else is implementation behind that interface.

## Body contract

```text
Motherpher/CareerHubZero          ← one CareerHub body + one VERSION
        │
        ├── CareerHub-LinusF      ← thin profile; already under Motherpher
        ├── wpb    ← stable target; migration from Hybrismannen/wpb
        └── Gracey       ← stable target; migration from Hybrismannen/Gracey
```

A CareerHub release is valid only when the unified body and all active profile-node compatibility checks pass.

## Current version

**CareerHub 0.2.8-alpha — Household-governed Silicon Sprint execution baseline.**

Canonical version source: `VERSION`.

Per-version content register: `stack/releases/`.

Registered profile hubs: `stack/registry.yaml`.

Versioning and release rules: `docs/VERSIONING.md`.

1.0 Full Audit Lock: `docs/AUDIT_1.0.md`.

Executable capability audit: `docs/CAPABILITY_AUDIT_0.2.7.md`.

Active 1.0 contraction sprint: `docs/SPRINT_1_0_SILICON_10WP.md`.

Repository ownership plan: `docs/REPOSITORY_OWNERSHIP.md`.

## Repository map

```text
core/
  hrdm/                 canonical HRDM specification and schema

docs/
  ARCHITECTURE.md
  AUDIT_1.0.md
  INSTANCE_CONTRACT.md
  MIGRATION.md
  PRINCIPLES.md
  REPOSITORY_OWNERSHIP.md
  VERSIONING.md

src/careerhub/           reusable central runtime
scripts/                 central validation/version tooling
schemas/                 canonical contracts
stack/
  registry.yaml          all active profile hubs
  releases/              full content register per version
```

## Non-negotiable separation

**Central CareerHub = motor/capability.**  
**Profiled CareerHub = context/state.**

Software changes are made only in the CareerHub body. The matchable profile is hard-bound to verified career sources; private-life data has no profile path. Every runtime/schema/workflow change requires a single CareerHub version bump and release-ledger entry. Profile nodes are compatibility-tested against the body; versions are not propagated into them.

## Migration status

- `Motherpher/CareerHub-LinusF` is a thin Motherpher profile using the current verified-career schema.
- `Motherpher/wpb/CareerHub` has the unified manifest but still executes its legacy local motor until private central-action access and parity pass.
- `Motherpher/Gracey/CareerHub` has the unified manifest but still executes its temporary local motor until private central-action access and parity pass.
- Grace's pre-firewall Region Stockholm application artifact is quarantined until verified career sources are added and the case is rerun.

## Stable release rule

`1.0.0` is created only after the full audit checklist passes for CareerHubZero, Linus, Weronika and Grace. A partially migrated hub blocks 1.0.
