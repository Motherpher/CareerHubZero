# CareerHubZero

**Canonical software body for CareerHub.**

CareerHubZero is the single reusable software body behind every CareerHub profile node. It owns sourcing, geography, matching, HRDM-R, application generation, state contracts, reusable workflows, schemas, release governance and the centrally managed web shell.

A personalised profile node owns verified career evidence, search settings, durable state, generated artifacts **and its protected presentation layer**: tone, visual identity, information emphasis, optional personal components and hub composition. It exposes a versionless `careerhub.yaml` manifest and does not fork or independently version CareerHub.

## User contract

**Profile → Search → Analyse → Apply → Track**

Supporting workspaces: **Library** and **Improve my CareerHub**.

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

Historical Household execution audit: `docs/audit/CAREERHUB_HOUSEHOLD_SPRINT_AUDIT_2026-09-25.md`.

Current repository gate recheck: `docs/audit/CAREERHUB_REPOSITORY_GATE_RECHECK_2026-10-05.md`.

Repository ownership plan: `docs/REPOSITORY_OWNERSHIP.md`.

Dual web architecture: `docs/DUAL_HUB_WEB_ARCHITECTURE.md`.

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
web-shell/               centrally managed Next.js shell + personalisation templates
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

## Distribution rule

Profile repositories consume the central CareerHub motor by checking out `Motherpher/CareerHubZero` at runtime and executing the canonical CLI against their own `careerhub.yaml` manifest. They do not require a cross-repository composite Action and they do not carry an authoritative local runtime.

The managed web shell is distributed only into central-owned site paths. Each profile repository retains ownership of `personalisation/**` and `site/personal/**`, allowing each hub to differ in tone, visual language, density, navigation emphasis and optional presentation components while executing the same CareerHub motor.

## Migration status

- `Motherpher/CareerHub-LinusF` uses the central action-complete CareerHub motor and the current personalised managed shell.
- `Motherpher/wpb/CareerHub` is cut over to the central motor. Its former local `src`, `scripts`, `hrdm` and requirements runtime have been removed; profile/search/state/history remain profile-owned.
- `Motherpher/Gracey/CareerHub` is cut over to the central motor. Its former local `src`, `scripts`, `hrdm` and requirements runtime have been removed; profile/search/state/history remain profile-owned.
- Grace's pre-firewall Region Stockholm application artifact remains quarantined until verified career sources are added and the case is rerun.

The 2026-09-25 Household audit remains a historical snapshot. WP02 and WP03 were re-evaluated as PASS on 2026-10-05 after checkout-based distribution and successful profile cutover; see the dated repository-gate recheck for evidence.

## Stable release rule

`1.0.0` is created only after the full audit checklist passes for CareerHubZero, Linus, Weronika and Grace. Current remaining blockers include live geography/routing proof and the dependent full-surface/end-audit gates; repository-side motor distribution and profile cutover are no longer blockers.
