# CareerHub Profile Manifest Contract

A CareerHub profile node supplies verified career context, search settings and state. It does not duplicate or version the CareerHub body.

## Stable manifest

Each profile node exposes `careerhub.yaml`.

Example:

```yaml
schema_version: "1.0"
profile_id: example-person

profile:
  path: profile/candidate.yaml

search:
  path: config/search_profile.yaml

state:
  job_vault: data/job_vault.json
  applications: data/applications.json
```

The manifest deliberately contains **no engine repository and no engine version**.

## Candidate-evidence rule

CareerHub may position or match a candidate only from verified career-related evidence bound to permitted source IDs.

Absent evidence remains unknown.

Private-life data, model memory, conversational impressions and search-only wishes/needs cannot become candidate evidence.

## Search-only overlay

```yaml
user_search_overlay:
  source: user_input
  scope: search_only
  specific_wishes_or_needs: "..."
```

This may affect sourcing, filtering, ranking and presentation but not candidate truth, HRDM proof points or application claims.

## State outputs

A profile node may maintain:

- normalized sourced jobs,
- historical job vault,
- analyzed-job records,
- application cases,
- deadlines and next actions,
- reminder history,
- status progression,
- generated artifacts and outcomes.

## User-facing rule

The user should normally experience only:

**Find jobs → Analyse? → Apply**

`instance.yaml` is deprecated migration metadata and is not part of the stable 1.0 contract.
