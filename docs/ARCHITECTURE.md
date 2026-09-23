# Architecture

## 1. System boundary

CareerHub is split into one canonical motor and multiple profiled instances.

### A. Central motor — CareerHubZero

Owned by **Motherpher/CareerHubZero**.

This layer contains all reusable capability:

- job-source adapters
- normalization and deduplication
- deterministic matching and triage
- HRDM-R
- employer and role context research
- evidence-bounded candidate positioning
- application drafting and document generation
- deadline logic
- application-state contracts
- dashboard/rendering logic
- notifications
- reusable automation/workflow definitions
- schemas, validation and regression tests
- stack version governance

No profiled hub may maintain an authoritative fork of these capabilities.

### B. Profiled instance

A separate private repository or bounded folder for one person.

It may contain only instance-specific material:

- candidate identity/profile and evidence
- career/search preferences
- target geographies/languages/availability
- search configuration values
- job vault and analysed-job records
- application history and progression
- outcomes
- generated views/artifacts
- private notes/documents
- generated stack lock

## 2. Dependency direction

```text
Profiled instance
      │ context/state
      ▼
CareerHubZero @ canonical VERSION
      │ analysis/artifacts/state updates
      ▼
Profiled instance
```

CareerHubZero must not depend on a specific person. Profile hubs must not redefine CareerHubZero motor logic.

## 3. Interface rule

**Find → Analyse? → Apply**

Everything else is implementation.

## 4. Data classes

### Capability data — CareerHubZero only
- source definitions
- schemas
- canonical prompts/contracts
- matching/scoring logic
- HRDM implementation
- application/rendering logic
- workflow templates
- version/release machinery

### Profile data — profiled hub only
- candidate profile/evidence
- personal preferences
- private source references

### State data — profiled hub only
- saved jobs
- deadlines
- application status
- interview/meeting history
- reminders already sent
- outcomes

## 5. Versioning

`VERSION` in CareerHubZero is the single motor-version source.

Every central motor/schema/workflow change requires:
1. a new `VERSION`,
2. `stack/releases/<version>.yaml`,
3. successful central CI,
4. propagation to every active hub in `stack/registry.yaml`,
5. remote compatibility verification.

Only after those checks may the release be tagged as stack-current. See `docs/VERSIONING.md`.
