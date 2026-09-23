# Profiled Instance Blueprint

This document defines a private CareerHub profile node without changing the CareerHub base contract.

## Boundary

CareerHubZero owns reusable capability. A profiled instance owns candidate context, evidence and durable application state.

Personal identity, CV evidence, job history and application history must not be committed to CareerHubZero.

## Evidence classes

Every candidate assertion should remain source-bounded:

- `verified` — source-backed and permitted for external use.
- `project_claim` — present in project/application material but requiring stronger source binding before external use.
- `positioning_hypothesis` — usable for search or framing only; never a factual CV claim.

Unknown remains unknown. Stronger wording is not stronger evidence.

## Positioning views

A profiled instance may maintain several internal or market-facing views over the same evidence bank. They may alter ordering, headline and vocabulary, but may not alter the underlying facts.

These views are profile implementation detail. They do not extend the CareerHub user contract.

## Canonical state

The engine contract remains centered on:

```yaml
state:
  job_vault: data/job_vault.json
  applications: data/applications.json
```

Analysed jobs, generated artifacts, progression and outcomes remain part of the application workflow rather than a separate user-facing subsystem.

## HRDM binding

HRDM candidate positioning is bound to the profiled instance evidence snapshot used for that run. Model memory is not candidate evidence.

## Default user surface

The visible user journey remains:

**Find → Analyse? → Apply**

Everything else is supporting implementation.
