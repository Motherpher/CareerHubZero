# Profiled Instance Contract

A profiled CareerHub instance supplies context and receives state/artifacts. It does not duplicate the central engine.

## Required instance inputs

At minimum:

```yaml
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
```

## Candidate evidence rule

CareerHub may only position a candidate using evidence supplied by the profiled instance or explicitly verified external evidence allowed by that instance.

Absent evidence remains **unknown**.

CareerHub must never invent:

- dates
- employers
- qualifications
- software/tool proficiency
- language proficiency
- results or achievements
- current location
- current employment status

## Expected state outputs

A profiled instance may maintain:

- normalized sourced jobs
- historic job vault
- analysed-job records
- application cases
- deadlines
- next actions
- reminder history
- status progression
- generated artifacts

## Status vocabulary

Canonical application progression:

```text
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
```

## User-facing rule

The implementation may use issues, workflows, JSON, APIs and structured state internally.

The profiled user should not need to understand those mechanisms.
