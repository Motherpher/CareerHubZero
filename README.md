# CareerHubZero

**Central operations for CareerHub.**

CareerHubZero is the reusable system layer behind profiled CareerHub instances. It contains the capability contract for sourcing jobs, analysing selected roles with HRDM-R, generating evidence-bounded application material, maintaining durable state, measuring market response and rendering the user-facing CareerHub journey.

It deliberately does **not** contain a person's private profile, CV, job history or application history.

## Two-part architecture

```text
                 CAREERHUB

        CENTRAL OPERATIONS
        Motherpher/CareerHubZero
        ├── sourcing / matching contracts
        ├── HRDM-R
        ├── employer/role research
        ├── application generation
        ├── instance + state contracts
        ├── market-response analytics
        ├── dashboard rendering
        ├── notifications / reusable workflows
        └── validation
                 │
                 │ runs against
                 ▼
        PROFILED INSTANCE
        e.g. a person's private repository
        ├── candidate profile
        ├── evidence index
        ├── positioning surfaces
        ├── search configuration
        ├── job vault
        ├── analysed jobs / HRDM runs
        ├── applications
        ├── response ledger / experiments
        └── outcomes
```

**Central CareerHub = capability.**  
**Profiled CareerHub = context + state.**

## User contract

The primary user journey remains:

**1. Find jobs → 2. Analyse? → 3. Apply**

Status and market-response views can be exposed as compact commands without surfacing implementation machinery.

## Current state

**CareerHubZero 0.2.0-alpha — profiled-instance contract and market-response layer.**

The first working CareerHub implementation was developed inside `Hybrismannen/wpb`. CareerHubZero is the canonical central-operations repository. Generic capability is being extracted without moving private candidate state into the engine.

The migration principle remains **copy → generalize → validate → cut over**.

## Repository map

```text
core/
  hrdm/                canonical HRDM specification and result schema

docs/
  ARCHITECTURE.md      system boundary and component model
  INSTANCE_CONTRACT.md contract between engine and profiled instance
  MARKET_RESPONSE.md   response-ledger and experiment rules
  MIGRATION.md         staged extraction from the WPB implementation
  PRINCIPLES.md        non-negotiable design rules

src/
  careerhub/
    instance.py        profiled-instance loader and path validation
    analytics.py       market-response aggregation
    dashboard.py       minimal instance dashboard renderer

scripts/
  validate_instance.py
  render_dashboard.py

schemas/
  instance.schema.json
  profile.schema.json
  search_profile.schema.json
  response_event.schema.json
  response_ledger.schema.json
  candidate_profile.schema.json   legacy/minimal compatibility contract
```

## Status labels

- **Central contracts:** active alpha
- **Profiled-instance loader:** active alpha
- **Market-response analytics:** active alpha
- **Dashboard renderer:** active alpha
- **WPB profiled instance:** remains live during migration
- **Full sourcing/application runtime cutover:** not yet complete
