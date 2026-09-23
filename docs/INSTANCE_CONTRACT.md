# Profiled Instance Contract

A profiled CareerHub instance supplies candidate context and durable market state to the reusable engine. It does **not** duplicate the central engine and personal data must not be committed to CareerHubZero.

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

Extended profiled instances may add:

```yaml
profile:
  path: profile/candidate.yaml
  evidence_index: profile/evidence_index.yaml
  surfaces_dir: profile/surfaces

search:
  path: config/search_profile.yaml
  experiments: config/market_experiments.yaml

state:
  job_vault: data/job_vault.json
  applications: data/applications.json
  response_ledger: data/response_ledger.json
  experiments: data/experiments.json

dashboard:
  path: dashboard/index.html
  data: dashboard/dashboard.json
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

Candidate profile claims should carry provenance or evidence identifiers. A positioning surface may change emphasis or signal order; it may not create a new biographical fact.

## Evidence index and positioning surfaces

An instance may maintain an evidence index separately from its readable candidate profile. This supports provenance, verification state and frozen HRDM snapshots without forcing raw private source material into the repository.

Multiple positioning surfaces are allowed. They are market hypotheses over the **same evidence bank**, not separate identities.

## Expected state outputs

A profiled instance may maintain:

- normalized sourced jobs
- historic job vault
- analysed-job records
- application cases
- deadlines and next actions
- reminder history
- status progression
- generated artifacts
- market-response events
- experiment state

## Application status vocabulary

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

## Market-response layer

Market response is a different object from HRDM analysis. It records what happened after exposure, outreach or application.

Typical response stages include:

```text
exposed
interested
contacted
qualified_contact
interview_1
interview_deep
case_or_test
references
offer
assignment
denied
withdrawn
no_response
```

Response data may guide future search and positioning experiments. It must not rewrite the evidence bank, and small samples must not be treated as a deterministic judgement about the candidate.

## Privacy and separation

A profiled instance should normally be private. Direct contact details, national identifiers and unrelated personal data are not required for the CareerHub operating model and should remain outside source control unless a deliberate secure design requires otherwise.

CareerHubZero contains reusable schemas and runtime only. Its validation workflow guards against committing profiled state into the central repository.

## User-facing rule

The implementation may use issues, workflows, JSON, APIs and structured state internally.

The profiled user should normally experience:

**Find → Analyse? → Apply**

Additional compact commands such as **Status** and **Napp** may expose durable state and market-response analytics without requiring the user to understand the underlying files.
