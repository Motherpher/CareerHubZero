# CareerHub 1.0 — Full Audit Lock Checklist

CareerHub may be tagged `1.0.0` only when every item below is recorded **PASS**.

## Architecture and ownership

- [ ] A01 One software body: CareerHubZero is the only authoritative runtime.
- [ ] A02 One version: `VERSION` in CareerHubZero is the only CareerHub software version.
- [ ] A03 Profile-node invariant: active profiles contain data/context/artifacts only, no authoritative runtime.
- [ ] A04 Motherpher ownership: all stable CareerHub repositories live under Motherpher.
- [ ] A05 Manifest contract: Linus, Weronika and Grace expose valid `careerhub.yaml` manifests with no engine/version pin.

## Evidence and profile integrity

- [ ] A06 Every matchable candidate claim is bound to verified career source IDs.
- [ ] A07 Private-life fields have no candidate-profile path.
- [ ] A08 User wishes/needs are search-only and cannot become candidate evidence.
- [ ] A09 Unknown candidate facts remain unknown.
- [ ] A10 Linus profile passes the canonical verified-career schema.
- [ ] A11 Weronika profile passes the canonical verified-career schema.
- [ ] A12 Grace profile passes the canonical schema and every future claim has explicit source provenance.

## Runtime and HRDM

- [ ] A13 Sourcing is central and repository-independent.
- [ ] A14 Normalisation/deduplication is central and deterministic.
- [ ] A15 Geographical drill is central, precision-aware and country-adapter capable.
- [ ] A16 Triage remains distinct from HRDM.
- [ ] A17 HRDM-R sequence is canonical and full-sequence.
- [ ] A18 Candidate Positioning uses only supplied verified candidate evidence.
- [ ] A19 Application generation cannot emit unsupported candidate claims.
- [ ] A20 DOCX/artifact generation is reproducible and case-bound.
- [ ] A21 State lifecycle is consistent across all profile nodes.

## Migration and historical integrity

- [ ] A22 WPB central-body parity passes before local motor removal.
- [ ] A23 Grace central-body parity passes before local motor removal.
- [ ] A24 Grace's 159-job historical vault is preserved.
- [ ] A25 Grace Region Stockholm pre-firewall artifact is revalidated or explicitly retired.
- [ ] A26 `instance.yaml` and `stack.lock.yaml` are removed or explicitly archived as migration-only provenance.
- [ ] A27 Grace and Weronika local runtime/HRDM copies are removed after parity.

## Automation, security and distribution

- [ ] A28 Profile repositories invoke the centrally released CareerHub body through the approved reusable action/workflow mechanism.
- [ ] A29 Normal CareerHub operation requires no cross-profile write token.
- [ ] A30 Each profile repository writes only to itself with repository-scoped credentials.
- [ ] A31 API secrets are repository/org secrets and never committed.
- [ ] A32 Central CI passes all schema, policy, regression and version gates.
- [ ] A33 Profile compatibility validation passes for Linus, Weronika and Grace against the same CareerHub release candidate.
- [ ] A34 Stable-release governance prevents a 1.0 tag without Full Audit Lock.

## User contract and documentation

- [ ] A35 Every profile exposes **Find jobs → Analyse? → Apply**.
- [ ] A36 Implementation machinery is not presented as user workflow.
- [ ] A37 Architecture, migration, manifest, geography and versioning docs match implementation.
- [ ] A38 Swedish/English service language is coherent per profile surface.

## Final gate

- [ ] A39 A full controlled run passes on Linus + Weronika + Grace against the exact same CareerHub release candidate.
- [ ] A40 No unresolved architecture, evidence, privacy, migration, security or runtime blocker remains.
- [ ] A41 Release ledger for 1.0.0 is complete.
- [ ] A42 `VERSION` is changed to `1.0.0` only after A01–A41 PASS.
- [ ] A43 `stack/FULL_AUDIT_PASS.yaml` records PASS at the exact release commit.
- [ ] A44 1.0.0 tag/release is created only from that audited commit.

**Rule:** WARN is not PASS. A waiver is valid only when an explicit audit record explains why the condition is inapplicable without weakening the architecture.
