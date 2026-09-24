# CareerHub Repository Ownership

## Stable ownership rule

All repositories that constitute the stable CareerHub stack belong under **Motherpher**. Repository naming is descriptive; ownership and contract compliance are architectural.

| Instance | Current location | State |
|---|---|---|
| Central motor | Motherpher/CareerHubZero | canonical |
| Linus Fast | Motherpher/CareerHub-LinusF | canonical |
| Weronika Pérez Borjas | Motherpher/wpb/CareerHub | ownership complete; local motor cutover pending |
| Grace | Motherpher/Gracey/CareerHub | ownership complete; local motor cutover pending |

## Transfer result

The existing Grace and WPB repositories were transferred intact to Motherpher. This preserves commit history, issues and provenance.

Weronika remains housed in the broader `Motherpher/wpb` repository. For CareerHub governance, the bounded `CareerHub/` subtree is the profile instance. This is acceptable provided that, after cutover, the subtree contains profile/config/state/artifacts only and no authoritative CareerHub motor.

Grace remains housed in `Motherpher/Gracey`; its `CareerHub/` subtree is the profile instance.

## Ownership completion criteria

Ownership is complete because:

1. all four active repositories are under Motherpher,
2. Grace issue/application provenance was preserved,
3. `stack/registry.yaml` points to the Motherpher paths,
4. stack locks record the canonical central engine,
5. the connector can read all four repositories.

Remaining local-motor code is a **centralisation** blocker, not an ownership blocker.

Repository renaming to `CareerHub-Grace` or `CareerHub-Weronika` is optional and does not block 1.0 unless a future governance decision makes naming canonical.
