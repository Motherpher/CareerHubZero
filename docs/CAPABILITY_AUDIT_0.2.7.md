# CareerHub 0.2.7-alpha — Executable Capability Audit

Date: 2026-09-24

## Audit question

Does CareerHubZero currently contain and integrate the code required to operate as a genuinely intelligent job-search, role-analysis and application system for multiple profile nodes?

## Summary

**Not yet at 1.0 completeness.**

CareerHubZero now contains a real central execution spine and the majority of reusable runtime components. The remaining blockers are distribution/cutover, global geography depth, sourcing breadth and live external-service verification.

## Capability matrix

| Capability | Code exists centrally | Joined to central CLI | Proven on profile nodes | 1.0 status |
|---|---:|---:|---:|---|
| Versionless profile manifest | yes | yes | manifest present on all three | near-pass |
| Verified career evidence firewall | yes | yes | existing profile validation passes | near-pass |
| Search-profile normalization | yes | yes | central regression tested | near-pass |
| Platsbanken sourcing | yes | yes | legacy proven; central cutover pending | pending parity |
| Remote source feeds | yes | yes | legacy proven; central cutover pending | pending parity |
| Adzuna / Jooble optional adapters | yes | yes | credential dependent | conditional |
| Dedupe / normalization | yes | yes | legacy proven; central cutover pending | pending parity |
| Triage / ranking | yes | yes | central code + legacy experience | pending parity |
| Search-only user overlay | yes | yes | policy tested | near-pass |
| Job geotagging | yes | yes when Google key exists | unit tested, not live-profile proven | pending live |
| Zoom-aware map aggregation | yes | yes | unit tested | frontend pending |
| Google Maps interactive frontend | no | no | no | blocker |
| Sweden country matrix adapter | specification only | no | no | blocker |
| Radius / travel-time drill | contracts only | no | no | blocker |
| HRDM-R execution | yes | yes | legacy proven; new trace model pending live profile | pending parity |
| Canonical HRDM Process-ID | yes | yes | regression tested | pending live |
| HRDM run ledger | yes | yes | regression tested | pending profile cutover |
| HRDM active report shelf | yes | yes | regression tested | pending profile cutover |
| Deadline-driven HRDM archive | yes | yes | regression tested | pending profile cutover |
| HRDM Markdown report | yes | yes | regression tested | pending profile cutover |
| HRDM DOCX export | yes | yes | code exists | pending live |
| HRDM PDF export | yes | yes | code exists | pending live |
| Hybridianesque Hy-Filter | yes | yes | gate/activation regression tested | pending live |
| HCC-Lite output | yes | yes | central HRDM prompt/schema | pending live |
| Application generation | yes | yes | legacy proven; central cutover pending | pending parity |
| Application DOCX | yes | yes | legacy proven | pending parity |
| Application state lifecycle | yes | yes | legacy proven | pending parity |
| Deadline reminders | yes | module exists | not yet central-action cutover | pending |
| Swedish/English hub rendering | yes | central renderers exist | local surfaces still authoritative | pending cutover |
| Central composite GitHub Action | yes | yes | cannot yet start in profile repos | blocked by Actions access |
| Cross-profile write token | not required | n/a | architecture removed it | solved |
| Grace local motor removed | no | n/a | no | blocker |
| Weronika local motor removed | no | n/a | no | blocker |
| Full controlled Linus/Weronika/Grace run | no | n/a | no | final blocker |

## Main findings

### 1. Central body is now executable

The body is no longer only modules/specification. `src/careerhub/cli.py` and `scripts/careerhub.py` provide one execution path through:

```text
careerhub.yaml
  -> profile/evidence validation
  -> search normalization
  -> sourcing
  -> dedupe
  -> triage/ranking
  -> optional geotagging
  -> job vault
  -> HRDM-R
  -> Hybridianesque gate
  -> HRDM report/ledger
  -> application generation
  -> case/state updates
  -> hub rendering
```

### 2. Distribution is the immediate cutover blocker

The central composite action exists at repository root `action.yml`.

Compatibility workflows in Linus, Weronika and Grace currently fail at GitHub job setup before CareerHub code executes. This indicates that private-action sharing from CareerHubZero has not yet been enabled for the other Motherpher repositories.

Once that repository/organization Actions-access setting is enabled, profile-side execution can be tested without any cross-profile write token.

### 3. Geography is partially intelligent, not complete

Geotagging and clustering exist, but the complete drill still requires:

- interactive Google map surface,
- Sweden/SCB country adapter,
- local-labour-market relationships,
- radius/travel-time execution,
- global country-adapter registry.

### 4. Discovery breadth is not yet global

The central source layer currently supports Platsbanken plus several remote feeds and optional Adzuna/Jooble adapters.

That is a functioning source layer, not yet a comprehensive world/job-board discovery fabric.

### 5. AI execution needs a live service test

HRDM/application code is present and centrally joined, but real semantic execution still depends on:

- usable `OPENAI_API_KEY`,
- available API credit,
- valid deployed model identifier,
- successful structured-output schema execution.

Fallback mode deliberately refuses to invent a completed analysis.

## 1.0 rule

CareerHub 1.0 must not be declared until:

1. central action execution works from all three profile repositories,
2. Grace and Weronika local motors are removed after parity,
3. geography drill is runtime-complete,
4. live AI HRDM/application execution passes,
5. active HRDM report/ledger lifecycle passes on real cases,
6. full controlled runs pass for Linus, Weronika and Grace,
7. the Full Audit Lock records PASS.
