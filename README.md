# CareerHubZero

**Central operations for CareerHub.**

CareerHubZero is the reusable system layer behind profiled CareerHub instances. It contains the capability to source jobs, analyse selected roles with HRDM-R, generate evidence-bounded application material, track application state and outcomes, and render the user-facing CareerHub journey.

It deliberately does **not** contain a person's private profile, CV, job history or application history.

## Two-part architecture

```text
                 CAREERHUB

        CENTRAL OPERATIONS
        Motherpher/CareerHubZero
        ├── sourcing
        ├── matching
        ├── HRDM-R
        ├── employer/role research
        ├── application generation
        ├── state contracts
        ├── notifications
        ├── rendering
        └── reusable workflows
                 │
                 │ runs against
                 ▼
        PROFILED INSTANCE
        e.g. a person's private repository
        ├── candidate profile
        ├── preferences
        ├── evidence/CV
        ├── job vault
        ├── analysed jobs
        ├── applications
        └── outcomes
```

**Central CareerHub = capability.**  
**Profiled CareerHub = context + state.**

## User contract

The profiled user should normally experience only:

**1. Find jobs → 2. Do you want to analyse this job? → YES → 3. Apply**

Sourcing internals, HRDM, ranking, case creation, document generation and workflow machinery remain behind that interface.

## Current state

**CareerHubZero 0.2.1-alpha — base-contract drift correction.**

The first working CareerHub implementation was developed inside `Hybrismannen/wpb`. CareerHubZero is the canonical central-operations repository. Generic capability is extracted without moving private candidate state into the engine.

The migration principle remains **copy → generalize → validate → cut over**.

## Repository map

```text
core/
  hrdm/                canonical HRDM specification and result schema

docs/
  ARCHITECTURE.md      system boundary and component model
  INSTANCE_CONTRACT.md contract between central operations and a profiled instance
  MIGRATION.md         staged extraction from the WPB implementation
  PRINCIPLES.md        non-negotiable design rules

src/
  careerhub/
    instance.py        profiled-instance loader and path validation
    dashboard.py       application-state dashboard renderer

scripts/
  validate_instance.py
  render_dashboard.py

schemas/
  instance.schema.json
  profile.schema.json
  search_profile.schema.json
  candidate_profile.schema.json
```

## Status labels

- **Central contracts:** active alpha
- **Profiled-instance loader:** active alpha
- **Dashboard renderer:** active alpha
- **WPB profiled instance:** remains live during migration
- **Full sourcing/application runtime cutover:** not yet complete
