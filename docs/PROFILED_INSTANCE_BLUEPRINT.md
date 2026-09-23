# Profiled Instance Blueprint

This document defines a CareerHub profile node without changing the CareerHub base contract.

## Boundary

CareerHubZero owns reusable capability. A profiled instance owns verified career-source references, verified career evidence, search configuration, an optional user search overlay, durable application state and generated artifacts.

Private-life material is not candidate evidence and must not be carried into the matchable profile.

## Matchable evidence rule

A candidate assertion is matchable only when:

1. it is a career claim,
2. it is bound to at least one permitted career source,
3. that source is marked verified,
4. the evidence item itself is marked verified.

No interview impression, model memory, general personal context or unrelated private information may be promoted into candidate evidence.

Unknown remains unknown.

## Verified career sources

Allowed source classes:

- cv
- professional_profile
- employment_record
- qualification
- certification
- portfolio_work_sample
- employer_reference
- verified_project_record

Other material may identify what needs verification, but it cannot generate the matchable profile.

## Search-only wishes and needs

A profiled instance may expose one free-text field: **Specific wishes or needs**.

Its canonical contract is:

    user_search_overlay:
      source: user_input
      scope: search_only
      specific_wishes_or_needs: ""

This field may affect job sourcing, filtering and ranking. It must never be copied into candidate evidence, positioning facts, CV content, HRDM proof points or application claims.

## Positioning views

Positioning may reorder or summarise verified evidence. It may not add facts.

Every positioning surface that affects matching should retain references to the verified evidence IDs from which it was derived.

## Canonical state

The engine contract remains centered on:

    state:
      job_vault: data/job_vault.json
      applications: data/applications.json

Analysed jobs, generated artifacts, progression and outcomes remain part of the application workflow rather than a separate user-facing subsystem.

## HRDM binding

HRDM candidate positioning is bound to the verified career-evidence snapshot used for that run.

Model memory is not candidate evidence. Search-only wishes and needs are not candidate evidence.

## Default user surface

The visible user journey remains:

**Find → Analyse? → Apply**

Everything else is supporting implementation.
