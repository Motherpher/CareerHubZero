# CareerHub Unified Body Architecture

## 1. Core rule

CareerHub is **one software body with one release version**.

There are not separate profile engines.

`Motherpher/CareerHubZero/VERSION` is the only CareerHub software version.

Profile repositories are data/context surfaces. They do not pin, fork or independently version the CareerHub runtime.

## 2. Body

The CareerHub body contains all reusable capability:

- sourcing and source adapters,
- normalization and deduplication,
- geographical drill and job geotagging,
- matching and triage,
- verified-career evidence firewall,
- HRDM-R,
- application generation,
- document generation,
- application/state lifecycle,
- dashboards/rendering,
- notifications,
- reusable GitHub Actions/workflows,
- schemas,
- migrations,
- regression tests,
- release/audit governance.

All of those capabilities are released together as **CareerHub X.Y.Z**.

## 3. Profile nodes

A profile repository contains only person-specific material:

- verified career evidence,
- search raster,
- job/application state,
- generated artifacts,
- a `careerhub.yaml` profile manifest.

The profile manifest contains paths only. It has no engine repository and no engine version.

Example:

```yaml
schema_version: "1.0"
profile_id: grace

profile:
  path: profile/candidate.yaml

search:
  path: config/search_profile.yaml

state:
  job_vault: data/job_vault.json
  applications: data/applications.json
```

## 4. Version semantics

CareerHub 1.0.0 means the **entire body** has passed the Full Audit Lock:

- runtime,
- evidence model,
- geography,
- HRDM,
- application generation,
- state model,
- workflows,
- profile manifest contract,
- all active profile-node compatibility tests.

There is no separate "engine 1.0" and "profile 1.0".

A profile either satisfies the current CareerHub manifest/schema contract or it does not.

## 5. Distribution

The preferred 1.0 distribution model is **pull execution**:

```text
Profile repository
     |
     | invokes
     v
CareerHub central reusable action/workflow @ v1
     |
     | reads local careerhub.yaml
     v
profile/search/state
```

This eliminates central cross-repository write propagation as a normal operating requirement.

Profile repositories use their own repository-scoped `GITHUB_TOKEN` to write their own state.

The central body is shared through GitHub's private-action/reusable-workflow sharing within the Motherpher organization.

## 6. Migration artifacts

The following files are migration scaffolding and are **not part of the stable 1.0 architecture**:

- `instance.yaml`
- `stack.lock.yaml`
- per-profile engine version fields
- `CAREERHUB_STACK_TOKEN` central push propagation

They remain only until Grace and Weronika have cut over from their local motors.

## 7. 1.0 release principle

The release sequence becomes:

```text
develop one CareerHub body
        ↓
complete all modules
        ↓
run central regression suite
        ↓
run profile compatibility suite
  Linus + Weronika + Grace
        ↓
Full Audit Lock
        ↓
VERSION = 1.0.0
        ↓
tag CareerHub v1.0.0
        ↓
all profile nodes execute CareerHub v1
```

No profile repository is independently "released".
