# CareerHubZero 1.0 — Full Audit Lock Checklist

CareerHubZero may be tagged `1.0.0` only when every item below is recorded **PASS**.

## Architecture and ownership

- [ ] A01 One canonical motor: CareerHubZero is the only authoritative runtime.
- [ ] A02 Complete registry: Linus, Weronika and Grace are all registered.
- [ ] A03 Thin-profile invariant: no active profile hub contains authoritative motor code.
- [ ] A04 Motherpher ownership: all CareerHub repositories in the stable stack live under Motherpher.
- [ ] A05 Version harmonisation: all active hubs consume the same canonical VERSION.

## Evidence and profile integrity

- [ ] A06 Every matchable candidate claim is bound to verified career source IDs.
- [ ] A07 Private-life fields have no candidate-profile path.
- [ ] A08 User wishes/needs are search-only and cannot become candidate evidence.
- [ ] A09 Unknown candidate facts remain unknown.
- [ ] A10 Linus profile is migrated to the canonical verified-career schema.
- [ ] A11 Weronika profile is migrated to the canonical verified-career schema.
- [ ] A12 Grace profile passes the canonical schema and has explicit source provenance for every future claim.

## Runtime and HRDM

- [ ] A13 Sourcing is central and repository-independent.
- [ ] A14 Normalisation/deduplication is central and deterministic.
- [ ] A15 Triage remains distinct from HRDM.
- [ ] A16 HRDM-R sequence is canonical and full-sequence.
- [ ] A17 Candidate Positioning uses only supplied verified candidate evidence.
- [ ] A18 Application generation cannot emit unsupported candidate claims.
- [ ] A19 DOCX/artifact generation is reproducible and case-bound.
- [ ] A20 State lifecycle is consistent across all hubs.

## Migration and historical integrity

- [ ] A21 WPB dual-run parity passes before local motor removal.
- [ ] A22 Grace dual-run parity passes before local motor removal.
- [ ] A23 Grace's 159-job historical vault is preserved.
- [ ] A24 Grace Region Stockholm pre-firewall artifact is revalidated or explicitly retired.
- [ ] A25 Legacy repositories retain sufficient provenance/redirect documentation after relocation.

## Automation, security and repository governance

- [ ] A26 `CAREERHUB_STACK_TOKEN` is configured with least-privilege cross-repository access.
- [ ] A27 API secrets are repository/org secrets and never committed.
- [ ] A28 Remote stack verification reaches every active private hub.
- [ ] A29 Central CI passes all schema, policy, regression and version gates.
- [ ] A30 Canonical branch/release governance prevents unvalidated stable release.

## User contract and documentation

- [ ] A31 Every hub exposes **Find jobs → Analyse? → Apply**.
- [ ] A32 Implementation machinery is not presented as user workflow.
- [ ] A33 Architecture, migration, instance contract and versioning docs match implementation.
- [ ] A34 Swedish/English service language is internally coherent per profile surface.
- [ ] A35 Full controlled run passes on Linus + Weronika + Grace with the same CareerHubZero motor.

## Final gate

- [ ] A36 No unresolved architecture, evidence, privacy, migration, security or runtime blocker remains.
- [ ] A37 Release ledger for 1.0.0 is complete.
- [ ] A38 `VERSION` is changed to `1.0.0` only after A01–A37 PASS.
- [ ] A39 1.0.0 tag/release is created only after remote stack verification passes at that exact commit.

**Rule:** a WARN is not a PASS. An item may be waived only by an explicit audit record that explains why the condition is inapplicable without weakening the architecture.
