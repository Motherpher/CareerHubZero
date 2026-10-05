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
- dashboard/rendering contracts,
- the reusable Vercel/Next.js interaction shell,
- reminders/notifications,
- reusable actions/workflows,
- schemas, migrations, tests and audit governance.

There is no separately versioned profile engine in the stable architecture.

## 2. Profile nodes

A profile repository is a bounded personal CareerHub node for one person.

It may contain:

- identity required to label the profile,
- verified career-source references,
- verified career evidence,
- search configuration,
- search-only wishes/needs,
- job/application state,
- generated artifacts,
- protected presentation configuration and optional person-owned presentation components,
- `careerhub.yaml`.

It does not own runtime logic, HRDM logic, canonical schemas or a software version.

The profile repository therefore owns **who the hub is for and how the hub presents itself**, but not the CareerHub motor.

## 3. Stable topology

```text
Motherpher/CareerHubZero      ← one CareerHub motor + one VERSION
        │
        ├── CareerHub-LinusF  ← profile/context/state + presentation
        ├── wpb               ← profile/context/state + presentation
        └── Gracey            ← profile/context/state + presentation
```

## 4. Dependency direction

```text
profile/search/state + presentation
              ↓
        CareerHub body
              ↓
analysis / artifacts / state updates / rendered interface
              ↓
      same profile repository
```

Each profile repository writes its own state using its own repository-scoped credentials.

## 5. Stable manifest

Each profile exposes `careerhub.yaml` containing paths and profile identity.

It contains no engine repository and no engine version. It may optionally point to protected presentation files such as `personalisation/hub.profile.yaml`, `personalisation/theme.tokens.json`, `personalisation/voice.yaml` and `site/`.

## 6. Interface rule

**Find → Analyse? → Apply**

Everything else is implementation.

## 7. Hard separation invariant

**VERIFIED CAREER SOURCES → MATCHABLE PROFILE → HRDM / APPLICATION CLAIMS**

**USER WISHES / NEEDS → SEARCH RASTER → SOURCING / FILTERING / RANKING**

**PRIVATE-LIFE DATA → NO PROFILE PATH**

**PERSONALISATION → PRESENTATION / UX ONLY; IT MAY NOT CREATE CAREER EVIDENCE**

No path may cross these boundaries.

## 8. Geography

CareerHub geography uses a dual-layer model:

- Google Maps Platform for global place selection/geocoding/routing,
- authoritative country adapters for national administrative/statistical/functional geography.

Sweden is the first country adapter.

## 9. Vercel and web presentation

The canonical web architecture is defined in `docs/DUAL_HUB_WEB_ARCHITECTURE.md`.

Stable deployment logic:

- CareerHubZero develops the managed shell.
- Each profile repository receives managed shell updates into its `site/` application.
- `personalisation/**` and `site/personal/**` remain owned by that profile and may not be silently overwritten centrally.
- Each profile repository maps to its own Vercel project, with `site/` as the project root.

This permits person-specific visual and tonal design without creating person-specific CareerHub engines.

## 10. Versioning

`VERSION` in CareerHubZero is the only CareerHub software version.

Profile nodes are compatibility-tested, not independently versioned.

## 11. Migration

`instance.yaml`, `stack.lock.yaml`, profile-local motors and cross-repository version propagation are pre-1.0 migration mechanisms only.

They are removed from the stable architecture after Grace and Weronika complete central-body cutover.

See `docs/BODY_ARCHITECTURE.md`, `docs/DUAL_HUB_WEB_ARCHITECTURE.md`, `docs/VERSIONING.md` and `docs/MIGRATION.md`.
