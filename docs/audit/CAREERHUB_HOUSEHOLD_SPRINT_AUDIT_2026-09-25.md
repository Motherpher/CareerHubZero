# CareerHub 1.0 Silicon Sprint — Household Execution Audit End Report

**Audit order:** CH-HH-ORDER-2026-09-25-01  
**Audit date:** 2026-09-25  
**CareerHub line:** 0.2.9-alpha  
**Audited implementation commit:** `3a32f03c68110c951c9236828d3bc21fa76ea768`  
**Household clearance run:** `36073576772`  
**Canonical validation run:** `36073576839` — PASS  
**Overall sprint clearance:** **BLOCKED — 1.0 RELEASE NOT PERMITTED**

---

## 1. Audit authority and method

This sprint was executed under user-authorized **Household family operational clearance**.

The Household authority split is preserved:

- **Director** governs WP progression and immutable acceptance.
- **Handyman** is limited to bounded deterministic J1 repair and never self-certifies PASS.
- **Janitor** scans entropy, contradiction, drift, provenance, CI, security and repository hygiene.
- **Household controller** orchestrates these roles and acquires no additional authority.

CareerHub 1.0 release authority is not delegated away from WP10 Full Audit Lock.

The sprint followed the Silicon rule:

> **Invert before adding. Unify before optimizing. Replace, delete, then prove.**

---

# 2. Fixed audit state order

The governed state order was:

```text
S00 BASELINE
S01 WP01 → C01
S02 WP02 → C02
S03 WP03 → C03
S04 WP04 → C04
S05 WP05 → C05
S06 WP06 → C06
S07 WP07 → C07
S08 WP08 → C08
S09 WP09 → C09
S10 WP10 → C10
S11 FINAL JANITOR DEEP SCAN
S12 DIRECTOR FINAL RECONCILIATION
S13 AUDIT END REPORT
```

No later PASS is allowed to overwrite an earlier blocker.

---

# 3. S00 — Baseline

**State:** PASS as execution baseline, not as stable release.

Baseline entering the Household sprint:

- CareerHubZero was already the intended canonical software body.
- `careerhub.yaml` existed as the stable versionless profile-node contract.
- Linus was already a thin profile node.
- Grace and Weronika still contained legacy local motors.
- central CLI/runtime modules existed but integration quality had not been Household-cleared.
- geographical geotagging and clustering existed but live full drill was incomplete.
- HRDM, report lifecycle and Hybridianesque code existed but needed integration audit.
- private CareerHubZero Action sharing to other Motherpher repositories was not enabled.
- live OpenAI semantic execution had not been revalidated after previous API credit exhaustion.

---

# 4. S01 / C01 — WP01: Collapse Runtime to One CareerHub Body

**Director state:** **PASS**

## Objective
Establish one authoritative central runtime and one execution spine.

## Evidence
Central runtime contains:

- `src/careerhub/cli.py`
- `scripts/careerhub.py`
- `src/careerhub/sources.py`
- `src/careerhub/matching.py`
- `src/careerhub/search_contract.py`
- `src/careerhub/learning.py`
- `src/careerhub/geography.py`
- `src/careerhub/country_adapters.py`
- `src/careerhub/hrdm.py`
- `src/careerhub/hrdm_trace.py`
- `src/careerhub/hybridianesque.py`
- `src/careerhub/hrdm_reports.py`
- `src/careerhub/application.py`
- `src/careerhub/state.py`
- `src/careerhub/hub.py`
- central `action.yml`

Machine compilation and unified-body tests passed.

## Contraction evidence
During sprint execution, duplicate/parallel geography code introduced during development was detected and removed:

- deleted `src/careerhub/geo_country.py`
- deleted `config/geo/countries.yaml`
- deleted `tests/test_geo_country.py`

The existing, more mature `country_adapters.py` remained canonical.

A second duplicate event contract was also removed later under WP05/WP08 integration.

## Residual
Profile-local legacy motors are deliberately handled under WP03, not treated as a failure of the central body gate.

---

# 5. S02 / C02 — WP02: Invert Distribution

**Director state:** **BLOCKED**

## Objective
Profile repositories should invoke the central CareerHub body and write only to themselves.

## Implemented
- central composite action exists at `action.yml`
- profile compatibility workflows were installed in Linus, Weronika and Grace
- `CAREERHUB_STACK_TOKEN` is not required by the stable architecture
- central push/version propagation is deprecated

## Blocking evidence
Compatibility workflows in all three profile repositories fail during GitHub **job setup before CareerHub code executes**.

The blocking condition is:

> Private GitHub Action sharing from `Motherpher/CareerHubZero` to the other Motherpher repositories has not been enabled.

This is a repository/organization Actions-access setting, not a CareerHub code defect and not a reason to recreate a cross-repository write token.

## Clearance
C02 withheld.

---

# 6. S03 / C03 — WP03: Cut Over Profiles and Delete Legacy Motors

**Director state:** **BLOCKED**

## Objective
Run parity, switch Grace and Weronika to central execution, then delete local motors.

## Current state
- **Linus:** thin profile; no local CareerHub motor.
- **Weronika:** unified manifest exists; local motor remains.
- **Grace:** unified manifest exists; local motor remains.
- Grace historical 159-job vault remains protected.
- Grace pre-firewall Region Stockholm application remains subject to revalidation or explicit retirement.

## Blocker
WP03 depends on successful WP02 central-action execution.

Deleting local motors before parity would violate the migration and evidence-safety rules.

## Clearance
C03 withheld.

---

# 7. S04 / C04 — WP04: Unify the Search Kernel

**Director state:** **PASS**

## Objective
Collapse search-profile dialects and source-specific query logic into one central search runtime.

## Implemented
- `search_contract.py` normalizes supported profile search shapes.
- lane/query configuration collapses into one runtime representation.
- verified career terms may broaden core discovery.
- user overlay remains search-only.
- source adapters consume normalized query inputs.
- query provenance is retained.
- deduplication occurs before final ranking.

## Tests
`tests/test_search_kernel.py` verifies:
- legacy/canonical lane-shape collapse,
- verified evidence broadens core discovery only,
- search overlay remains a query input rather than candidate evidence.

## Contraction
No new profile-specific search engine was created.

---

# 8. S05 / C05 — WP05: Career Learning Loop

**Director state:** **PASS**

## Objective
Turn existing outcome history back into bounded search intelligence without creating a second analytics truth.

## Implemented
The learning loop derives signals from the existing canonical case history.

Learning dimensions include:
- role family,
- function family,
- employer type,
- arrangement,
- geography.

Outcome signals include:
- viewed,
- ignored,
- selected for HRDM,
- user rejected,
- applied,
- contacted,
- test,
- interview,
- offer,
- denied,
- withdrawn.

Learning includes:
- provenance,
- observation count,
- small-sample shrinkage,
- confidence,
- bounded ranking adjustment.

The post-triage learning adjustment is limited and explainable.

## Evidence firewall
The learning function neither accepts nor mutates the verified candidate profile.

## Silicon repair
Two event schemas existed during sprint development.

They were contracted into one canonical:
- **kept:** `schemas/outcome_event.schema.json`
- **deleted:** `schemas/career_event.schema.json`

Compatibility functions used by the hub are projections over the same canonical learning model, not a second model.

---

# 9. S06 / C06 — WP06: Unified Geography

**Director state:** **BLOCKED**

## Implemented
Central geography now contains:

- one vacancy geo object,
- source-coordinate precedence,
- Google Places geotagging adapter,
- precision levels,
- world/country/region/locality aggregation,
- high-zoom precise points without fabricated precision,
- total and newly sourced job counts,
- Google Routes matrix support,
- country enrichment interface,
- canonical Sweden adapter,
- Swedish county/municipality dataset,
- Swedish local-labour-market dataset,
- dynamic SCB WFS discovery for RegSO/DeSO.

The Sweden adapter enriches the canonical geo object; it does not create a parallel geography truth.

## Silicon contraction
The sprint initially produced a second country-adapter abstraction. Household audit identified the duplication and it was removed in favour of the existing canonical `country_adapters.py`.

## Blocking gate
The full runtime gate remains unproven because:

- live Google Maps/routing execution requires a working `GOOGLE_MAPS_API_KEY`,
- interactive map/product execution is not yet proven end-to-end,
- full country-matrix drill must be exercised in a real profile run.

## Clearance
C06 withheld.

---

# 10. S07 / C07 — WP07: Canonical HRDM

**Director state:** **PASS**

## Objective
One canonical HRDM v6.3 execution path with trace, Hybridianesque, report lifecycle and ledger.

## Implemented
- canonical Reverse Mode execution path,
- canonical Process-ID syntax,
- atomic daily RUNSEQ,
- S01–S08 locked trace components,
- S09 starts OPEN and is finalized only after semantic execution,
- successful semantic run ends FINAL,
- fallback/incomplete semantic run ends WARN and is not bank-eligible,
- HCC-Lite integration,
- Hybridianesque four-criterion gate,
- explicit Yes/No activation requirement,
- active HRDM report shelf,
- historical HRDM ledger,
- vacancy-deadline archive lifecycle,
- Markdown report,
- DOCX export,
- PDF export.

## Household repair
An earlier regression test incorrectly expected a newly created HRDM trace to already be FINAL.

The test was corrected to verify the actual canonical lifecycle:

```text
OPEN → semantic completion → FINAL
```

rather than weakening the runtime to satisfy the incorrect test.

## Source alignment
The implementation preserves the HRDM v6.3 requirements for run registry, Process-ID discipline, banking state and optional Hybridianesque enclosure.

---

# 11. S08 / C08 — WP08: One Application & Outcome State Machine

**Director state:** **PASS**

## Objective
Use one case object and one event history rather than separate analysis, application, reminder and outcome truths.

## Implemented
The central case model carries:
- job identity,
- priority,
- deadline,
- status,
- next action,
- HRDM Process-ID,
- HRDM report paths,
- application paths,
- external-use gate,
- notification history,
- canonical outcome history.

State progression supports:
- saved,
- preparing,
- ready,
- applied,
- contacted,
- test/portfolio,
- interview/meeting progression,
- offer,
- denied,
- withdrawn,
- archived.

The same history is projected into WP05 learning.

## Contraction
No separate learning-event datastore was introduced.

---

# 12. S09 / C09 — WP09: One Hub Surface

**Director state:** **BLOCKED**

## Implemented
The central hub renderer derives one operational surface from canonical state:

```text
Find jobs → Analyse? → Apply
```

It exposes:
- current shortlist,
- historical job vault,
- geography clusters,
- active HRDM reports,
- HRDM ledger,
- cases/applications,
- career-learning interpretation,
- history links.

## Blocker
WP09 depends on WP06.

The unified surface cannot be declared complete until the geographical map/drill is proven live end-to-end rather than merely represented as backend map payloads.

## Clearance
C09 withheld.

---

# 13. S10 / C10 — WP10: Contract, Audit and Lock CareerHub 1.0

**Director state:** **BLOCKED**

The Full Audit Lock cannot pass while WP02, WP03, WP06 and WP09 remain blocked.

Additional final-release proof still required:
- live OpenAI HRDM structured-output execution,
- live AI application generation,
- all three profile nodes running the same central body,
- Grace/Weronika legacy motor removal after parity,
- live geography/map execution,
- controlled three-profile end-to-end run,
- final removal/archive of migration-only runtime metadata.

**CareerHub 1.0.0 is therefore correctly withheld.**

---

# 14. S11 — Final Janitor deep scan

**State:** **PASS with nonblocking findings**

Household run `36073576772` reported:

- findings: **6**
- blocking findings: **0**

The findings are advisory/hygiene class and do not authorize bypass of Director blockers.

No blocking Janitor finding prevented progression independently of the WP gates.

---

# 15. S12 — Director final reconciliation

**State:** **BLOCKED**

Authoritative Director states from Household run `36073576772`:

| WP | State |
|---|---|
| WP01 | **PASS** |
| WP02 | **BLOCKED** |
| WP03 | **BLOCKED** |
| WP04 | **PASS** |
| WP05 | **PASS** |
| WP06 | **BLOCKED** |
| WP07 | **PASS** |
| WP08 | **PASS** |
| WP09 | **BLOCKED** |
| WP10 | **BLOCKED** |

Canonical CareerHub validation on the same audited implementation commit passed.

The Household workflow itself correctly ended **failure** because at least one Director state was not PASS. This is expected and is evidence that the clearance layer is enforcing the sprint rather than masking blockers.

---

# 16. S13 — Audit end report

**Report state:** COMPLETE  
**Programme verdict:** **BLOCKED / CONTINUE 0.2.9-alpha**  
**Stable release verdict:** **1.0 NOT PERMITTED**

## Passed WPs
- WP01 — central body
- WP04 — search kernel
- WP05 — learning loop
- WP07 — HRDM
- WP08 — case/outcome state

## Blocked WPs
- WP02 — private central Action access
- WP03 — central profile cutover depends on WP02
- WP06 — live geography runtime proof
- WP09 — depends on WP06
- WP10 — upstream gates and final live proof incomplete

## Remaining external gates

### E01 — GitHub private Action sharing
Enable `Motherpher/CareerHubZero` for use by the other Motherpher profile repositories.

This must solve WP02 without reintroducing `CAREERHUB_STACK_TOKEN`.

### E02 — Google Maps runtime
Provide/configure a valid `GOOGLE_MAPS_API_KEY` with required Places/Routes/Maps capabilities and run the full geo drill.

### E03 — OpenAI live semantic execution
Restore usable API credit/access and re-run full HRDM + application structured-output path.

---

# 17. Household repairs recorded during the sprint

Household/audit execution exposed and corrected:

1. **Director portable-path defect**  
   Audit paths were resolved incorrectly after porting. Corrected to absolute resolved paths.

2. **False-green Household workflow condition**  
   Workflow initially trusted Director process return code while `stop_on_blocker:false` allowed the sequence to continue. Enforcement now reads recorded WP states.

3. **Missing central test import path**  
   Director test checks did not expose `src` on `PYTHONPATH`. Corrected in Household workflow.

4. **Forward dependency contradiction**  
   WP05 initially depended on WP08 despite fixed WP01→WP10 audit order. WP05 now depends on WP04 and consumes the already-existing canonical case history; WP08 subsequently tightens the state contract.

5. **Learning compatibility fracture**  
   New learning implementation removed functions already consumed by the central hub. Compatibility projections were restored over the single canonical learning model.

6. **HRDM test/state mismatch**  
   Test expected premature FINAL. Test corrected to canonical OPEN → FINAL lifecycle.

7. **Duplicate geography abstraction**  
   Newly introduced geo adapter path was deleted in favour of the existing mature country-adapter implementation.

8. **Duplicate outcome-event schema**  
   Two event schemas were collapsed into `outcome_event.schema.json`.

These repairs are evidence that Household operated as a real control layer rather than a ceremonial PASS generator.

---

# 18. Silicon-rule assessment

The sprint moved CareerHub in the intended direction:

```text
more capability
      +
fewer authoritative truths
```

Confirmed contractions:
- one CareerHub software version,
- one stable profile manifest concept,
- one central execution body,
- one search normalization path,
- one learning model,
- one outcome-event schema,
- one country-adapter path,
- one HRDM path,
- one case/outcome history,
- one intended user journey.

Not yet contracted:
- Grace legacy motor,
- Weronika legacy motor,
- migration-only instance/lock artifacts in affected profiles,
- incomplete live map/product boundary.

---

# 19. Final conclusion

CareerHub is materially closer to a defensible **personal labour-market intelligence system**, not merely a job-search automation stack.

The Household sprint has proven that the central architecture can now support:

```text
verified profile
    ↓
search hypotheses
    ↓
sourcing / triage
    ↓
career-learning adjustment
    ↓
geographical enrichment
    ↓
HRDM / Hybridianesque
    ↓
report ledger
    ↓
application state
    ↓
outcome
    ↺
next search hypothesis
```

The sprint has **not** proven the complete distributed/live system.

Therefore:

> **Keep CareerHub on 0.2.9-alpha. Resolve E01–E03, rerun WP02→WP10 in the same Household state order, and only then consider 0.3.0-alpha / Full Audit Lock.**

No 1.0 tag or `FULL_AUDIT_PASS.yaml` is authorized by this report.
