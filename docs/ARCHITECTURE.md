# Architecture

## 1. CareerHub is one software body

CareerHub is released as one product with one version.

**Canonical software body:** `Motherpher/CareerHubZero`

It contains all reusable capability:

- sourcing and source adapters,
- normalization and deduplication,
- geographical drill and vacancy geotagging,
- matching and triage,
- verified-career evidence policy enforcement,
- search-only user overlay handling,
- HRDM-R,
- employer/role context research,
- evidence-bounded candidate positioning,
- application and document generation,
- state lifecycle,
- dashboard/rendering,
- reminders/notifications,
- reusable actions/workflows,
- schemas, migrations, tests and audit governance.

There is no separately versioned profile engine in the stable architecture.

## 2. Profile nodes

A profile repository is a bounded data/context node for one person.

It may contain only:

- identity required to label the profile,
- verified career-source references,
- verified career evidence,
- search configuration,
- search-only wishes/needs,
- job/application state,
- generated artifacts,
- `careerhub.yaml`.

It does not own runtime code, HRDM logic, central schemas or a software version.

## 3. Stable topology

```text
Motherpher/CareerHubZero      ← one CareerHub body + one VERSION
        │
        ├── CareerHub-LinusF  ← profile/data node
        ├── wpb/CareerHub     ← profile/data node
        └── Gracey/CareerHub  ← profile/data node
```

## 4. Dependency direction

```text
profile/search/state
      ↓
CareerHub body
      ↓
analysis / artifacts / state updates
      ↓
same profile repository
```

Each profile repository writes its own state using its own repository-scoped credentials.

## 5. Stable manifest

Each profile exposes `careerhub.yaml` containing only paths and profile identity.

It contains no engine repository and no engine version.

## 6. Interface rule

**Find → Analyse? → Apply**

Everything else is implementation.

## 7. Hard separation invariant

**VERIFIED CAREER SOURCES → MATCHABLE PROFILE → HRDM / APPLICATION CLAIMS**

**USER WISHES / NEEDS → SEARCH RASTER → SOURCING / FILTERING / RANKING**

**PRIVATE-LIFE DATA → NO PROFILE PATH**

No path may cross these boundaries.

## 8. Geography

CareerHub geography uses a dual-layer model:

- Google Maps Platform for global place selection/geocoding/routing,
- authoritative country adapters for national administrative/statistical/functional geography.

Sweden is the first country adapter.

## 9. Versioning

`VERSION` in CareerHubZero is the only CareerHub software version.

Profile nodes are compatibility-tested, not independently versioned.

## 10. Migration

`instance.yaml`, `stack.lock.yaml`, profile-local motors and cross-repository version propagation are pre-1.0 migration mechanisms only.

They are removed from the stable architecture after Grace and Weronika complete central-body cutover.

See `docs/BODY_ARCHITECTURE.md`, `docs/VERSIONING.md` and `docs/MIGRATION.md`.
