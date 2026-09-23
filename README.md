# CareerHubZero

**Canonical central motor for CareerHub.**

CareerHubZero is the single reusable motor behind every profiled CareerHub instance. It owns sourcing/matching capability, HRDM-R, application generation, state contracts, rendering, reusable workflows, schemas and stack version governance.

A profiled hub owns only verified career evidence, search settings, durable job/application state and generated artifacts. User-entered wishes or needs are a search-only raster and never candidate evidence. It must not fork or redefine the motor.

## User contract

**1. Find jobs → 2. Analyse? → 3. Apply**

Everything else is implementation behind that interface.

## Stack contract

```text
Motherpher/CareerHubZero       ← one canonical motor + VERSION
        │
        ├── CareerHub-LinusF   ← profile/config/state/artifacts
        └── WPB CareerHub      ← profile/config/state/artifacts
```

A CareerHub version is stack-current only when every active registered profile hub consumes the same central engine version and contains no local motor copy.

## Current version

**CareerHubZero 0.2.3-alpha — verified-career evidence firewall + search-only user raster.**

Canonical version source: `VERSION`.

Per-version content register: `stack/releases/`.

Registered profile hubs: `stack/registry.yaml`.

Versioning and release rules: `docs/VERSIONING.md`.

## Repository map

```text
core/
  hrdm/                 canonical HRDM specification and schema

docs/
  ARCHITECTURE.md
  INSTANCE_CONTRACT.md
  MIGRATION.md
  PRINCIPLES.md
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

`Motherpher/CareerHub-LinusF` is structured as a profile node. `Hybrismannen/wpb/CareerHub` still contains the original legacy local motor; the stack registry deliberately treats that as a release blocker until the WPB cutover removes the duplicate motor.
