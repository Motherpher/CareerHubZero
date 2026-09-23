# CareerHubZero

**Central operations for CareerHub.**

CareerHubZero is the reusable system layer behind profiled CareerHub instances. It contains the capability to source jobs, analyse a selected role with HRDM-R, generate an evidence-bounded application pack, track deadlines and application state, and render the user-facing CareerHub journey.

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

**CareerHubZero 0.1.0-alpha — extraction and separation phase.**

The first working CareerHub implementation was developed inside `Hybrismannen/wpb`. CareerHubZero now becomes the canonical central-operations repository. WPB remains operational while generic capability is extracted and made instance-independent.

The migration principle is **copy → generalize → validate → cut over**. We do not break the live profiled instance while building the central engine.

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
  careerhub/           reusable runtime package

examples/
  instance.example.yaml
  profile.example.yaml

schemas/
  instance.schema.json
```

## Status labels

- **Central core:** being established
- **WPB profiled instance:** live
- **Runtime cutover:** not started
- **Canonical source after cutover:** Motherpher/CareerHubZero
