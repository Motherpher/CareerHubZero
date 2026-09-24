# CareerHub Versioning

## One product, one version

CareerHub has one software version.

The canonical source is:

`Motherpher/CareerHubZero/VERSION`

Profile repositories do not have independent CareerHub software versions and do not pin a separate engine version.

## Stable architecture

The stable CareerHub body lives in `Motherpher/CareerHubZero`.

Active profile nodes:

- `Motherpher/CareerHub-LinusF`
- `Motherpher/wpb/CareerHub`
- `Motherpher/Gracey/CareerHub`

A profile node contributes verified career evidence, search configuration, state and generated artifacts through `careerhub.yaml`.

## Release rule

A CareerHub release is valid only when the whole body passes its release gate:

1. central runtime and schemas pass,
2. evidence and privacy invariants pass,
3. geography, sourcing, matching, HRDM, application and state tests pass,
4. the profile-manifest contract passes,
5. Linus, Weronika and Grace compatibility passes,
6. legacy local motors have been removed,
7. the Full Audit Lock passes.

Only then is `VERSION` advanced and the CareerHub release tagged.

## Distribution model

The stable distribution model is profile-side execution of the centrally released CareerHub body.

Profile repositories invoke the central reusable action/workflow and use their own repository-scoped GitHub token for local writes.

This means CareerHub does **not** require a central token with write access to every profile repository.

## Migration-only artifacts

The following belong to the pre-1.0 migration architecture and are not part of stable 1.0:

- `instance.yaml`
- `stack.lock.yaml`
- per-profile `engine.version`
- central version propagation
- `CAREERHUB_STACK_TOKEN`

They may remain temporarily while Grace and Weronika are cut over from their local motors.

## Version line

### 0.2.x-alpha
Contract repair and unified-body migration.

### 0.3.x-alpha
Complete central body, reusable workflow/action distribution, profile-local motor removal, and audit repair.

### 1.0.0
**Full Audit Lock of the unified CareerHub body.**

There is no separate engine release and no independent profile release.

## 1.0 meaning

`CareerHub 1.0.0` means that all capabilities are released together:

- sourcing,
- geography,
- matching,
- evidence firewall,
- HRDM,
- application/document generation,
- state lifecycle,
- UI/workflows,
- profile-manifest contract,
- regression/audit governance.

A profile either satisfies the current CareerHub contract or it does not.
