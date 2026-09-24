# CareerHubZero

**Canonical central motor for CareerHub.**

CareerHubZero is the single reusable motor behind every profiled CareerHub instance. It owns sourcing/matching capability, HRDM-R, application generation, state contracts, rendering, reusable workflows, schemas and stack version governance.

A profiled hub owns only verified career evidence, search settings, durable job/application state and generated artifacts. User-entered wishes or needs are a search-only raster and never candidate evidence. It must not fork or redefine the motor.

## User contract

**1. Find jobs → 2. Analyse? → 3. Apply**

Everything else is implementation behind that interface.

## Stack contract

```text
Motherpher/CareerHubZero          ← one canonical motor + VERSION
        │
        ├── CareerHub-LinusF      ← thin profile; already under Motherpher
        ├── CareerHub-Weronika    ← stable target; migration from Hybrismannen/wpb
        └── CareerHub-Grace       ← stable target; migration from Hybrismannen/Gracey
```

A CareerHub version is stack-current only when every active registered profile hub consumes the same central engine version, contains no local motor copy and satisfies the stable Motherpher ownership boundary.

## Current version

**CareerHubZero 0.2.4-alpha — Grace stack recovery + Motherpher ownership and 1.0 audit-lock governance.**

Canonical version source: `VERSION`.

Per-version content register: `stack/releases/`.

Registered profile hubs: `stack/registry.yaml`.

Versioning and release rules: `docs/VERSIONING.md`.

1.0 Full Audit Lock: `docs/AUDIT_1.0.md`.

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

Motor changes are made only in CareerHubZero. The matchable profile is hard-bound to verified career sources; private-life data has no profile path. Every motor/schema/workflow change requires a version bump and release-ledger entry. The release workflow propagates that version to registered profile hubs and fails rather than silently leaving a hub behind.

## Migration status

- `Motherpher/CareerHub-LinusF` is already a thin Motherpher profile repository but its candidate profile still requires migration to the current verified-career schema.
- `Hybrismannen/wpb/CareerHub` remains the Weronika legacy implementation and contains local motor code. Stable target: `Motherpher/CareerHub-Weronika`.
- `Hybrismannen/Gracey/CareerHub` is now registered, policy-normalised and bound to CareerHubZero 0.2.4-alpha, but still contains a temporary local motor. Stable target: `Motherpher/CareerHub-Grace`.
- Grace's pre-firewall Region Stockholm application artifact is quarantined until verified career sources are added and the case is rerun.

## Stable release rule

`1.0.0` is created only after the full audit checklist passes for CareerHubZero, Linus, Weronika and Grace. A partially migrated hub blocks 1.0.
