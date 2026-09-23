# Profiled Instance Contract

A profiled CareerHub instance supplies verified career context, search preferences and state. It does not duplicate the central engine.

## Required instance inputs

At minimum:

    careerhub:
      instance_id: example-person
      engine:
        repository: Motherpher/CareerHubZero
        version: "0.x"

    profile:
      path: profile/candidate.yaml

    search:
      path: config/search_profile.yaml

    state:
      job_vault: data/job_vault.json
      applications: data/applications.json

## Hard candidate-evidence rule

CareerHub may position or match a candidate only from evidence that is career-related, bound to an allowed career source, verified and present in the profiled instance.

Absent evidence remains **unknown**.

CareerHub must never generate a matchable profile fact from private-life information, family or relationship context, health information, religion, ethnicity or sexual orientation, political affiliation, personal financial context, model memory, conversational impressions or unverified biographical claims.

CareerHub must never invent dates, employers, qualifications, tools, language proficiency, results, achievements, current location or current employment status.

## Search-only user overlay

The user may enter **specific wishes or needs** to refine a search.

Canonical contract:

    user_search_overlay:
      source: user_input
      scope: search_only
      specific_wishes_or_needs: "..."

This overlay may influence sourcing queries, filtering, ranking and presentation order.

It may not influence candidate-evidence truth, CV claims, HRDM proof points or external factual claims about the candidate.

## Expected state outputs

A profiled instance may maintain normalized sourced jobs, historic job vault, analysed-job records, application cases, deadlines, next actions, reminder history, status progression, generated artifacts and outcomes.

## Status vocabulary

Canonical application progression:

    saved
    preparing
    ready
    applied
    contacted
    portfolio
    interview_1 ... interview_5
    meeting_1 ... meeting_5
    offer
    denied
    withdrawn
    archived

## User-facing rule

The implementation may use issues, workflows, JSON, APIs and structured state internally.

The profiled user should normally experience only:

**Find jobs → Analyse? → Apply**

No additional user-facing command or funnel is canonical unless explicitly added to the base contract.
