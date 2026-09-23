# Profiled Instance Blueprint

This document defines the reusable contract for a private CareerHub profile node. It extends the minimum instance contract without moving personal data into CareerHubZero.

## Boundary

CareerHubZero owns capability. A profiled instance owns candidate context and durable state.

A profiled instance may be a private GitHub repository or another private state store that implements the same paths/contracts. Personal identity, CV evidence, job history, application history and response events must not be committed to CareerHubZero.

## Evidence classes

Every candidate assertion must have one of three states:

- `verified` — source-backed and permitted for external use.
- `project_claim` — present in prior project/application material but requires source binding before external use.
- `positioning_hypothesis` — usable for search, segmentation or A/B framing only; never a factual CV claim.

Unknown remains unknown. A stronger sentence is not a substitute for stronger evidence.

## Positioning surfaces

A profile may maintain several market-facing surfaces. Surfaces may alter ordering, headline, vocabulary and search lanes, but they must not alter the underlying evidence ledger.

This permits controlled market testing without creating contradictory candidate identities.

## Market-response funnel

Canonical response stages:

`exposed → viewed → saved/shortlisted → recruiter_contact → qualified_contact → application → interview_1 → interview_2_plus → case_test → reference_check → offer → assignment`

Terminal/diagnostic states include `denied`, `withdrawn`, and `no_response`.

No-response is retained as evidence. It must not be silently discarded from conversion analysis.

## Optional state paths

A profiled instance may declare:

```yaml
state:
  job_vault: data/job_vault.json
  applications: data/applications.json
  response_events: data/response_events.json
  verification_queue: data/verification_queue.json
  analysed_jobs: data/analysed_jobs/
```

## HRDM binding

HRDM candidate positioning is bound to the profiled instance evidence snapshot used for that run. The run must record provenance or a profile snapshot/version identifier. Model memory is not candidate evidence.

## Default user surface

The visible user journey remains:

**Find → Analyse? → Apply → Track response**

The deeper evidence ledger, verification queue, HRDM trace and engine status are administrative/supporting views.
