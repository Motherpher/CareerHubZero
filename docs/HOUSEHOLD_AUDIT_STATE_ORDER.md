# CareerHub 1.0 Silicon Sprint — Household Audit State Order

**Audit order ID:** CH-HH-ORDER-2026-09-25-01  
**Authority:** User-authorized operational Household clearance for WP01–WP10.  
**Release authority:** CareerHub 1.0 remains subject to WP10 Full Audit Lock; Household cannot fabricate or bypass that release gate.

## Household family authority

- **Director** — immutable WP progression/clearance decision from governed evidence.
- **Handyman** — bounded deterministic J1 repair only; never self-certifies PASS.
- **Janitor** — contradiction, drift, security, provenance, CI and hygiene surveillance.
- **Household controller** — orchestration only; gains no additional authority.

Repair classes:
- J0 — ephemeral cleanup.
- J1 — deterministic registered repair under path guard.
- J2 — interpretive/constitutional/integration stop requiring explicit resolution.

Blocking severities:
`CONTRADICTION → CONTROL_DEFECT → SECURITY_STOP → CONSTITUTIONAL_STOP`.

## Fixed state order

The audit record must be read in this exact order:

```text
S00 BASELINE
 ↓
S01 WP01 — Collapse Runtime to One CareerHub Body
 ↓ Household clearance C01
S02 WP02 — Invert Distribution
 ↓ Household clearance C02
S03 WP03 — Cut Over Profiles and Delete Legacy Motors
 ↓ Household clearance C03
S04 WP04 — Unify the Search Kernel
 ↓ Household clearance C04
S05 WP05 — Career Learning Loop
 ↓ Household clearance C05
S06 WP06 — Unified Geography
 ↓ Household clearance C06
S07 WP07 — Canonical HRDM
 ↓ Household clearance C07
S08 WP08 — One Application & Outcome State Machine
 ↓ Household clearance C08
S09 WP09 — One Hub Surface
 ↓ Household clearance C09
S10 WP10 — Contract, Audit and Lock CareerHub 1.0
 ↓ Household clearance C10
S11 FINAL JANITOR DEEP SCAN
 ↓
S12 DIRECTOR FINAL RECONCILIATION
 ↓
S13 AUDIT END REPORT
```

## State vocabulary

Each state record uses one of:

- `OPEN` — implementation/verification is active.
- `PASS` — Director machine gates and Household clearance pass at the recorded commit.
- `BLOCKED` — a blocking finding or failed gate prevents acceptance.
- `REPAIR_CANDIDATE` — Handyman has produced a bounded J1 candidate; not accepted.
- `DEFERRED_EXTERNAL_NON_BLOCKING` — external item explicitly proven non-blocking.
- `VOID` — superseded evidence/state; never silently reused.
- `FINAL` — WP10 release lock only after every required upstream PASS.

## Evidence order per WP

For each WP, the end audit must list evidence in this order:

1. WP objective.
2. Dependency state.
3. Required paths.
4. Machine checks/tests.
5. Janitor findings.
6. Handyman repairs, if any.
7. Director decision.
8. Repository commit SHA.
9. Residual risks / external blockers.
10. Deletion/contraction evidence.

## Non-fabrication rule

Implementation may continue on technically independent WPs even if another WP is blocked.  
**Clearance may not ignore declared dependencies.**

A later WP PASS never retroactively converts an earlier BLOCKED state into PASS.

## Final audit rule

CareerHub 1.0 may be released only if:
- WP01–WP09 are PASS,
- WP10 Full Audit Lock is PASS,
- final Janitor deep scan has zero blocking findings,
- Director final reconciliation is PASS,
- the exact audited commit is tagged.
