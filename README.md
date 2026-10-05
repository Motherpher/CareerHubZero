# CareerHubZero

**Canonical software body for CareerHub.**

CareerHubZero is the single reusable software body behind every CareerHub profile node. It owns sourcing, geography, matching, HRDM-R, application generation, state contracts, reusable workflows, schemas, release governance and the centrally managed Vercel web shell.

A personalised profile node owns verified career evidence, search settings, durable state, generated artifacts **and its protected presentation layer**: tone, visual identity, information emphasis, optional personal components and hub composition. It exposes a versionless `careerhub.yaml` manifest and does not fork or independently version CareerHub.

## User contract

**1. Find jobs → 2. Analyse? → 3. Apply**

Everything else is implementation behind that interface.

## Body contract

```text
Motherpher/CareerHubZero          ← one CareerHub motor + one VERSION
        │
        ├── CareerHub-LinusF      ← thin profile + personalised hub
        ├── wpb                   ← thin profile + personalised hub
        └── Gracey                ← thin profile + personalised hub
```

A CareerHub release is valid only when the unified body, managed web shell and all active profile-node compatibility checks pass.

## Current version

**CareerHub 0.2.9-alpha — open Household-governed Silicon Sprint integration line.**

Canonical version source: `VERSION`.

Per-version content register: `stack/releases/`.

Registered profile hubs: `stack/registry.yaml`.

Versioning and release rules: `docs/VERSIONING.md`.

1.0 Full Audit Lock: `docs/AUDIT_1.0.md`.

Executable capability audit: `docs/CAPABILITY_AUDIT_0.2.7.md`.

Active 1.0 contraction sprint: `docs/SPRINT_1_0_SILICON_10WP.md`.

Household execution audit: `docs/audit/CAREERHUB_HOUSEHOLD_SPRINT_AUDIT_2026-09-25.md`.

Repository ownership plan: `docs/REPOSITORY_OWNERSHIP.md`.

Dual Vercel/web architecture: `docs/DUAL_HUB_WEB_ARCHITECTURE.md`.

## Repository map

```text
core/
  hrdm/                 canonical HRDM specification and schema

docs/
  ARCHITECTURE.md
  DUAL_HUB_WEB_ARCHITECTURE.md
  AUDIT_1.0.md
  INSTANCE_CONTRACT.md
  MIGRATION.md
  PRINCIPLES.md
  REPOSITORY_OWNERSHIP.md
  VERSIONING.md

src/careerhub/           reusable central runtime
web-shell/               centrally managed Vercel/Next.js shell + personalisation templates
scripts/                 central validation/version/sync tooling
schemas/                 canonical contracts, including presentation schemas
stack/
  registry.yaml          all active profile hubs
  releases/              full content register per version
```

## Non-negotiable separation

**Central CareerHub = motor/capability + reusable interaction shell.**  
**Personalised CareerHub = verified context/state + protected person-specific presentation.**

Software changes are made only in the CareerHub body. Person-owned presentation files are not central software and must never be silently overwritten by a motor release. The matchable profile remains hard-bound to verified career sources; private-life data has no profile path. Every runtime/schema/workflow change requires a single CareerHub version bump and release-ledger entry. Profile nodes are compatibility-tested against the body; versions are not propagated into them.

## Vercel deployment rule

Each personalised CareerHub repository is intended to have its own Vercel project with `site/` as project root.

CareerHubZero distributes the managed shell into centrally owned site paths. The profile repository retains ownership of `personalisation/**` and `site/personal/**`, allowing each hub to differ in tone, visual language, density, navigation emphasis and optional presentation components while executing the same CareerHub motor.

## Migration status

- `Motherpher/CareerHub-LinusF` is a thin Motherpher profile using the current verified-career schema.
- `Motherpher/wpb/CareerHub` has the unified manifest but still executes its legacy local motor until private central-action access and parity pass.
- `Motherpher/Gracey/CareerHub` has the unified manifest but still executes its temporary local motor until private central-action access and parity pass.
- Grace's pre-firewall Region Stockholm application artifact is quarantined until verified career sources are added and the case is rerun.

## Stable release rule

`1.0.0` is created only after the full audit checklist passes for CareerHubZero, Linus, Weronika and Grace. A partially migrated hub blocks 1.0.
