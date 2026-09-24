# CareerHub Stack Versioning

## Canonical source

`Motherpher/CareerHubZero/VERSION` is the single canonical engine version for the entire CareerHub stack.

Profiled hubs do not create their own motor versions. They record the CareerHubZero version they consume.

## Repository ownership boundary

The stable CareerHub stack is owned under the **Motherpher** GitHub organization.

Canonical targets:

- `Motherpher/CareerHubZero` — central motor
- `Motherpher/CareerHub-LinusF` — Linus profile
- `Motherpher/wpb` — Weronika repository; `CareerHub/` is the bounded profile instance
- `Motherpher/Gracey` — Grace repository; `CareerHub/` is the bounded profile instance

Legacy repositories may remain as migration sources until their history/state has been preserved and parity has passed, but no non-Motherpher CareerHub repository may be part of the 1.0 aligned stack.

## Stack rule

A CareerHub release is **stack-current** only when every active registered profiled hub:

1. points to `Motherpher/CareerHubZero`,
2. records the canonical `VERSION`,
3. has a generated `stack.lock.yaml`,
4. contains no profile-local CareerHub motor implementation,
5. passes the base instance contract,
6. is located under Motherpher for stable releases.

Profile content, search preferences, evidence, application state and generated artifacts may vary. Motor code, schemas, HRDM core and reusable workflow logic may not.

## Release sequence

```text
change in CareerHubZero
        ↓
VERSION bump + release ledger entry
        ↓
central validation
        ↓
stack registry check
        ↓
sync version into every registered profile hub
        ↓
profile compatibility check
        ↓
release/tag only if full stack is aligned
```

A failed or unreachable profile hub blocks stack-wide release completion. The system must not silently call a version harmonised when one hub is behind.

## Version line to 1.0

### 0.2.x-alpha
Contract, evidence, registry and governance repair.

### 0.3.0-alpha
Full central-motor cutover candidate. All active profile hubs must run through CareerHubZero rather than profile-local motor code.

### 0.3.x-alpha
Audit-repair line. Use only as required to close findings from the full-stack audit.

### 1.0.0
**Full Audit Lock release.**

1.0.0 is not reached by feature count. It is reached only when the complete audit checklist passes for CareerHubZero and every active profile hub.

The 1.0 gate includes:
- complete Motherpher ownership boundary,
- complete central-motor cutover,
- verified-career evidence provenance,
- search-only raster separation,
- HRDM sequence integrity,
- application-claim provenance,
- state lifecycle integrity,
- regression and remote-stack checks,
- security/secret review,
- documentation/operational coherence,
- revalidation or retirement of pre-firewall artifacts.

## Version format

CareerHub uses SemVer-style versions during alpha:

- patch: contract/governance/bug correction,
- minor: new reusable motor capability or contract extension,
- major: stable breaking contract revision.

The transition to 1.0.0 is the first stable audit-locked release.

## Release ledger

Every version has a machine-readable record under `stack/releases/<version>.yaml` recording purpose, user contract, motor/contract contents, schemas, migration state, known limitations and compatibility expectations.

Historical alpha entries reconstructed from repository history are explicitly marked `reconstructed: true`.

## Profile locks

Each profiled hub receives a generated `stack.lock.yaml` beside its instance file. It records the engine repository/version, alignment state and blockers. It is generated from CareerHubZero; it is not a second source of truth.

## Automation token

Cross-private-repository writes cannot be performed by a repository-scoped GitHub `GITHUB_TOKEN`. Full automatic propagation therefore uses one shared infrastructure credential: `CAREERHUB_STACK_TOKEN`.

It must have read/write Contents access to every registered private profiled hub and read access to CareerHubZero. A GitHub App installation token is preferred; a fine-grained PAT is acceptable.

If the credential is absent or a registered hub cannot be updated, the release workflow fails. It does not silently skip the hub.
