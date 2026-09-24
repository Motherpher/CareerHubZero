# CareerHub 1.0 Silicon Sprint — 10 Work Packages

## Sprint purpose

Move CareerHub from an increasingly capable alpha into **one compact, executable, learning software body**.

This sprint is deliberately not an expansion sprint.

Its design rule is:

> **Invert before adding. Unify before optimizing. Replace, delete, then prove.**

The target is not “more modules”. The target is fewer authorities, fewer runtime paths and fewer user surfaces while CareerHub becomes materially more capable.

---

## The Silicon Rule

Every WP must follow these constraints.

### S1 — One authority per concept
There may be one authoritative:
- software body,
- version,
- profile manifest,
- search contract,
- job geo object,
- HRDM path,
- case state model,
- learning-event model,
- user control surface.

Adapters may vary. Core truth may not.

### S2 — New code must collapse old code
A new module is justified only if it:
1. becomes the canonical path, and
2. permits an existing path to be deleted, absorbed or demoted to a thin adapter.

### S3 — Prefer inversion over orchestration
Examples:
- profile pulls central body instead of central body pushing versions,
- outcomes flow back into search hypotheses instead of creating a separate analytics product,
- map is a projection of canonical job geography instead of a separate location database,
- HRDM history is the same ledger viewed through active/history filters instead of two truths.

### S4 — Derived surfaces, stored truth
Dashboards, maps, counts, recommendations and reports should be derived from canonical state wherever practical.

Do not persist a second truth because it is convenient for display.

### S5 — Profiles contain context, not software
Profile nodes contain:
- verified evidence,
- search settings,
- state,
- generated artifacts,
- `careerhub.yaml`.

No profile-local authoritative runtime survives 1.0.

### S6 — Intelligence may learn; candidate truth may not drift
CareerHub may learn:
- which roles respond,
- which searches work,
- which geographies produce opportunities,
- which employers progress applications,
- which application strategies perform better.

It may not turn those observations into unsupported claims about the person.

### S7 — User complexity must decrease
The backend may become more capable while the user-facing contract remains:

```text
Find jobs → Analyse? → Apply
```

### S8 — Every WP ends with deletion
Each WP must list and execute a contraction target.

A WP is not DONE merely because the new path works.

### S9 — No hidden migration residue in 1.0
Migration scaffolding must be removed from active architecture before 1.0.

### S10 — Proof precedes release
A feature is “installed” only when:
- its central code path exists,
- regression tests pass,
- profile compatibility passes where applicable,
- the old path has been retired.

---

# Sprint topology

```text
WP01  ONE BODY
  │
  ├──── WP02  DISTRIBUTION INVERSION
  │        │
  │        └──── WP03  PROFILE CUTOVER / DELETE LEGACY
  │
  ├──── WP04  SEARCH KERNEL
  │        │
  │        └──── WP05  CAREER LEARNING LOOP
  │
  ├──── WP06  UNIFIED GEOGRAPHY
  │
  ├──── WP07  CANONICAL HRDM
  │        │
  │        └──── WP08  APPLICATION / OUTCOME STATE
  │                         │
  └─────────────────────────┼──── WP09  ONE HUB SURFACE
                            │
                            └──── WP10  CONTRACT / AUDIT / 1.0
```

The WPs can overlap in implementation, but their exit gates are dependency-ordered.

---

# WP01 — Collapse Runtime to One CareerHub Body
**Issue:** #1

### Inversion
From:
```text
central runtime + Grace runtime + Weronika runtime
```

To:
```text
one CareerHub runtime + thin profile nodes
```

### Deliverables
- runtime inventory,
- canonical module map,
- one CLI/action execution spine,
- generic sourcing/matching/HRDM/application/state/rendering code,
- removal of profile/repository hard-coding.

### Must delete
- authoritative Grace local runtime,
- authoritative Weronika local runtime,
- duplicate runtime/render/document code once parity is proven.

### Exit
Repository search shows one authoritative implementation per runtime capability.

---

# WP02 — Invert Distribution
**Issue:** #3

### Inversion
From:
```text
central body pushes version/state expectations outward
```

To:
```text
profile node invokes centrally released CareerHub body
and writes only to itself
```

### Deliverables
- Motherpher private-action access enabled,
- all three profiles invoke the same central action,
- repository-local writes use repository-scoped `GITHUB_TOKEN`,
- stable action/release pinning design.

### Must delete
- cross-repository version propagation,
- `CAREERHUB_STACK_TOKEN`,
- per-profile engine/version pinning.

### Exit
Linus, Weronika and Grace execute the same central body with no cross-profile write credential.

---

# WP03 — Cut Over Profiles and Delete Legacy Motors
**Issue:** #4

### Inversion
From:
```text
two bespoke migrations
```

To:
```text
one parity → cutover → delete pattern
```

### Deliverables
- Weronika parity run,
- Grace parity run,
- HRDM/application/state/render parity checks,
- Grace 159-job history preservation,
- Grace pre-firewall artifact revalidation or retirement,
- profile workflows switched to central action.

### Must delete
- Grace local motor,
- Weronika local motor,
- local HRDM copies,
- local runners,
- active `instance.yaml` / `stack.lock.yaml`.

### Exit
All three profiles are thin nodes.

---

# WP04 — Unify the Search Kernel
**Issue:** #16

### Inversion
From:
```text
profile-specific lane dialects + source-specific query logic
```

To:
```text
verified evidence + search overlay + hypotheses
            ↓
       one query contract
            ↓
        source adapters
```

### Deliverables
- one stable search schema,
- one lane/query normalization path,
- occupational/function hypothesis generation,
- source query provenance,
- centralized dedupe before ranking,
- employer/role-family targeting as hypotheses.

### Must delete
- legacy search-profile dialect,
- source-specific query transformation from profiles,
- duplicate lane normalization.

### Exit
Same search kernel works unchanged for all profiles.

---

# WP05 — Career Learning Loop
**Issue:** #17

### Inversion
From:
```text
analytics as a report about the past
```

To:
```text
outcomes become bounded inputs to the next search decision
```

### Deliverables
One canonical outcome-event stream covering:
- surfaced,
- viewed / ignored,
- selected for HRDM,
- user rejected,
- applied,
- employer response,
- test/interview,
- offer,
- denied/withdrawn,
- elapsed time,
- geography.

Derived learning:
- role-family response,
- function response,
- employer-type response,
- arrangement response,
- geography response,
- application-strategy response.

Every learned weight carries:
- evidence count,
- recency,
- uncertainty,
- provenance.

### Must delete
- separate analytics truth,
- second recommendation score,
- any mechanism that mutates verified candidate evidence.

### Exit
Historical replay changes search hypotheses reproducibly without changing candidate truth.

---

# WP06 — Unified Geography
**Issue:** #15

### Inversion
From:
```text
Google geography + Sweden geography + map data
```

To:
```text
one canonical job geo object
  ├─ global provider enrichment
  ├─ country adapter enrichment
  └─ map/drill projections
```

### Deliverables
- global Google Maps/Places anchor,
- one normalized geo object,
- country-adapter registry,
- Sweden/SCB adapter,
- län/kommun/RegSO/DeSO,
- local labour market / functional-region enrichment,
- radius and travel-time drill,
- progressive widening,
- precision-aware clustering,
- total/new job counts,
- map payload for world → country → city → workplace.

### Must delete
- parallel geo representations,
- fake map precision,
- geography scoring outside the central ranking/learning model.

### Exit
One global drill works everywhere; Sweden gains deeper official matrix intelligence without changing the core.

---

# WP07 — Canonical HRDM
**Issue:** #18

### Inversion
From:
```text
HRDM code + local HRDM copies + report utilities
```

To:
```text
one HRDM v6.3 execution path
        ↓
one Process-ID / run ledger
        ↓
active/history report projections
```

### Deliverables
- full canonical HRDM-R,
- canonical Process-ID states,
- atomic RUNSEQ,
- run registry,
- HCC-Lite,
- Hybridianesque recommendation + explicit Yes/No gate,
- active HRDM report shelf,
- historical ledger,
- deadline archive lifecycle,
- Markdown, DOCX, PDF,
- banking validation.

### Must delete
- local HRDM copies,
- duplicate HRDM report/docx logic,
- non-canonical shortened Process-ID paths.

### Exit
One real case proves analyse → read in hub → download → deadline archive → ledger retrieval.

---

# WP08 — One Application & Outcome State Machine
**Issue:** #19

### Inversion
From:
```text
analysis state + application state + reminder state + outcome state
```

To:
```text
one case + one event history
```

### Deliverables
- one lifecycle,
- HRDM Process-ID binding,
- application artifact binding,
- external-use gate,
- priority/deadline/next-action,
- reminder projections,
- terminal outcomes,
- WP05 event emission.

### Must delete
- duplicate application status representations,
- separate reminder truth,
- profile-local case logic.

### Exit
One controlled job traverses the full lifecycle with one authoritative history.

---

# WP09 — One Hub Surface
**Issue:** #20

### Inversion
From:
```text
multiple dashboards + implementation surfaces
```

To:
```text
one user surface
Find → Analyse? → Apply
```

### Deliverables
- unified control room,
- live job shortlist,
- job vault,
- geographical map/drill,
- active HRDM reports,
- HRDM ledger,
- application monitor,
- career-learning explanations,
- Word/PDF download,
- Swedish/English profile presentation.

### Must delete
- overlapping dashboards,
- duplicate navigation,
- engine/version/migration UI.

### Exit
A normal user can complete the system journey without understanding CareerHub internals.

---

# WP10 — Contract, Audit and Lock 1.0
**Issue:** #14

### Inversion
From:
```text
final development phase
```

To:
```text
deletion + proof + lock
```

No feature work belongs here unless required to repair a failed audit gate.

### Deliverables
- remove all deprecated paths,
- one-source-of-truth audit,
- central regression suite,
- controlled Linus run,
- controlled Weronika run,
- controlled Grace run,
- live AI execution test,
- geography test,
- Career Learning Loop test,
- HRDM report/archive test,
- Full Audit Lock,
- exact release ledger,
- `VERSION = 1.0.0`,
- exact audited tag.

### Exit
All 1.0 gates PASS. WARN is not PASS.

---

# Sprint-level contraction metrics

The sprint is successful only if it reaches all of these:

| Surface | Start | Sprint target |
|---|---:|---:|
| Authoritative CareerHub runtimes | 3 | **1** |
| Profile-local motors | 2 | **0** |
| CareerHub software versions in profile nodes | multiple migration refs | **0** |
| Stable profile manifests | 3 | **3, one schema** |
| Cross-profile write secrets | migration concept | **0** |
| Search config dialects | >1 | **1** |
| HRDM implementations | >1 | **1** |
| HRDM run ledgers per profile | emerging | **1 canonical model** |
| Job geography truths | multiple inputs | **1 normalized object** |
| Application state truths | multiple projections | **1 case/event model** |
| Recommendation/learning models | ad hoc/static | **1 explainable loop** |
| Primary user surfaces per profile | overlapping | **1** |
| Stable release version | alpha | **CareerHub 1.0.0 after audit** |

---

# Sprint stop conditions

Stop and repair instead of expanding when any of the following occurs:

1. a new subsystem duplicates existing state,
2. a new profile-specific runtime branch appears,
3. a second schema is introduced for the same concept,
4. a UI requires storing a second truth,
5. learning starts mutating candidate evidence,
6. a migration workaround becomes part of the stable contract,
7. a WP increases authoritative surface without an explicit deletion path.

---

# Release sequence

```text
0.2.7-alpha
current audited integration baseline
        ↓
Silicon Sprint WP01–WP09
        ↓
0.3.0-alpha
one complete release candidate body
        ↓
WP10 Full Audit Lock
        ↓
1.0.0
```

The sprint does not create 1.0 by accumulation.

It creates 1.0 by **compression into one coherent body**.
