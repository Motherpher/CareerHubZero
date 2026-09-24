# Architecture

## 1. System boundary

CareerHub is split into one canonical motor and multiple profiled instances.

### A. Central motor — CareerHubZero

Owned by **Motherpher/CareerHubZero**.

This layer contains all reusable capability:

- job-source adapters,
- normalization and deduplication,
- deterministic matching and triage,
- verified-career-evidence policy enforcement,
- search-only user overlay handling,
- HRDM-R,
- employer and role context research,
- evidence-bounded candidate positioning,
- application drafting and document generation,
- deadline logic,
- application-state contracts,
- dashboard/rendering logic,
- notifications,
- reusable automation/workflow definitions,
- schemas, validation and regression tests,
- stack version governance.

No profiled hub may maintain an authoritative fork of these capabilities.

### B. Profiled instance

A separate bounded repository for one person.

It may contain only instance-specific material needed for the CareerHub service:

- identity needed to label the instance,
- verified career-source references,
- verified career evidence,
- search configuration,
- optional search-only wishes/needs,
- target geographies/languages/availability as search configuration,
- job vault and analysed-job records,
- application history and progression,
- outcomes,
- generated views/artifacts,
- generated stack lock.

Private-life material is outside the candidate-evidence model.

## 2. Repository placement

Stable CareerHub repositories live under **Motherpher**.

Target layout:

```text
Motherpher/CareerHubZero
Motherpher/CareerHub-LinusF
Motherpher/wpb            # CareerHub/ bounded instance
Motherpher/Gracey         # CareerHub/ bounded instance
```

A legacy repository outside Motherpher may be used during migration, but it is a source/transition state and cannot satisfy the 1.0 stable stack boundary.

## 3. Dependency direction

Profiled instance → verified career evidence + search raster + state → CareerHubZero → analysis/artifacts/state updates → profiled instance.

CareerHubZero must not depend on a specific person. Profile hubs must not redefine CareerHubZero motor logic.

## 4. Interface rule

**Find → Analyse? → Apply**

Everything else is implementation.

## 5. Data classes

### Capability data — CareerHubZero only
Source definitions, schemas, canonical prompts/contracts, matching/scoring logic, HRDM implementation, application/rendering logic, workflow templates and version/release machinery.

### Verified career profile data — profiled hub only
Allowed career-source references, source-bound verified career claims and derived positioning tied back to verified evidence IDs.

### Search-raster data — profiled hub only
Geographies, engagement types, search lanes and specific wishes or needs supplied by the user.

Search-raster data does not become candidate evidence.

### State data — profiled hub only
Saved jobs, deadlines, application status, interview/meeting history, reminders already sent and outcomes.

## 6. Hard separation invariant

**VERIFIED CAREER SOURCES → MATCHABLE PROFILE → HRDM / APPLICATION CLAIMS**

**USER WISHES / NEEDS → SEARCH RASTER → SOURCING / FILTERING / RANKING**

**PRIVATE-LIFE DATA → NO PROFILE PATH**

No path may cross these boundaries.

## 7. Legacy artifact rule

Artifacts produced before the verified-career firewall may be preserved for provenance, but they are not automatically valid for external use.

They must be:
- revalidated against verified career evidence, or
- explicitly retired/archived as pre-firewall artifacts.

Grace's Region Stockholm application case is the first registered example of this rule.

## 8. Versioning

VERSION in CareerHubZero is the single motor-version source.

Every central motor/schema/workflow change requires:
1. a new VERSION,
2. a `stack/releases` version ledger,
3. successful central CI,
4. propagation to every active hub in `stack/registry.yaml`,
5. remote compatibility verification.

Only after those checks may the release be tagged as stack-current. See `docs/VERSIONING.md`.
