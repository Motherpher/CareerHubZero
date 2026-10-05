# CareerHub Profile Manifest Contract

A CareerHub profile node supplies verified career context, search settings and state. It does not duplicate or version the CareerHub body.

A profile repository may contain **other independent workrooms** in addition to CareerHub. CareerHub is not assumed to own the entire profile container.

## Stable manifest

Each CareerHub profile node exposes `careerhub.yaml`.

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

## Multi-room profile-container rule

CareerHub may be one bounded room inside a larger person/profile repository.

Examples of sibling rooms may include:

- writer/journalism workrooms;
- research rooms;
- portfolio/creative-production rooms;
- professional-practice rooms;
- other domain-specific workspaces.

These sibling rooms remain outside CareerHub authority unless a specific bridge contract exposes selected evidence to CareerHub.

CareerHub must not treat sibling-room state as its own storage and must not automatically crawl or ingest an entire profile repository merely because the files are technically accessible.

## Candidate-evidence rule

CareerHub may position or match a candidate only from verified career-related evidence bound to permitted source IDs.

Absent evidence remains unknown.

Private-life data, model memory, conversational impressions and search-only wishes/needs cannot become candidate evidence.

Evidence from another profile workroom may enter CareerHub only through an **explicit, provenance-preserving export/bridge**. The source room retains authority over the underlying fact; CareerHub receives a career-use representation, not ownership of the source material.

Unpublished drafts, confidential sources, private research notes and unresolved evidence must not cross into CareerHub automatically.

## Search-only overlay

```yaml
user_search_overlay:
  source: user_input
  scope: search_only
  specific_wishes_or_needs: "..."
```

This may affect sourcing, filtering, ranking and presentation but not candidate truth, HRDM proof points or application claims.

## State outputs

A CareerHub profile node may maintain:

- normalized sourced jobs,
- historical job vault,
- analyzed-job records,
- application cases,
- deadlines and next actions,
- reminder history,
- status progression,
- generated artifacts and outcomes.

These are CareerHub state. They do not become the canonical state of sibling workrooms in the same profile container.

## User-facing rule

The user should normally experience only:

**Find jobs → Analyse? → Apply**

A higher-level profile interface may expose CareerHub alongside other independent rooms without changing this CareerHub journey.

`instance.yaml` is deprecated migration metadata and is not part of the stable 1.0 contract.
