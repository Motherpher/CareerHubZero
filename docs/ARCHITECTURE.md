# Architecture

## 1. System boundary

CareerHub is split into two deliberately different layers.

### A. Central Operations

Owned by **Motherpher/CareerHubZero**.

This layer contains reusable capability:

- job-source adapters
- normalization and deduplication
- deterministic matching and triage
- HRDM-R
- employer and role context research
- evidence-bounded candidate positioning
- application drafting
- DOCX generation
- deadline logic
- application-state contracts
- dashboard rendering
- notifications
- reusable automation/workflow definitions
- validation and regression tests

It must be able to operate without knowing the identity of any particular candidate.

### B. Profiled Instance

A separate private repository or other state store for one person.

It contains:

- candidate identity and profile
- verified evidence and CV material
- career preferences
- target geographies
- languages
- availability
- search configuration overrides
- job vault
- analysed jobs
- application history
- interview/meeting progression
- outcomes
- private notes and documents

## 2. Dependency direction

The profiled instance depends on CareerHubZero.

CareerHubZero must **not** depend on a specific profiled repository.

```text
Profiled instance
      │
      │ supplies context/state
      ▼
CareerHubZero
      │
      │ returns analysis/artifacts/state updates
      ▼
Profiled instance
```

## 3. Interface rule

The user-facing contract remains intentionally simple:

**Find → Analyse? → Apply**

Everything else is implementation.

## 4. Data classes

### Capability data
May live in CareerHubZero:
- source definitions
- schemas
- canonical prompts/contracts
- scoring logic
- rendering logic
- workflow templates

### Profile data
Must live outside CareerHubZero:
- name
- CV
- employment history
- contact details
- personal preferences
- private evidence

### State data
Must live outside CareerHubZero:
- saved jobs
- deadlines
- application status
- interview history
- reminders already sent

## 5. Versioning

CareerHubZero will use explicit versions.

Profiled instances should eventually pin a compatible CareerHubZero release rather than track unreviewed development automatically.

Initial line:

```text
0.x  extraction / contract stabilization
1.0  first stable reusable central operations release
```
