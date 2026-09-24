# CareerHub Repository Ownership

## Stable ownership rule

All repositories that constitute the stable CareerHub stack belong under **Motherpher**.

| Instance | Current location | Stable target | State |
|---|---|---|---|
| Central motor | Motherpher/CareerHubZero | Motherpher/CareerHubZero | already canonical |
| Linus Fast | Motherpher/CareerHub-LinusF | Motherpher/CareerHub-LinusF | already canonical |
| Weronika Pérez Borjas | Hybrismannen/wpb/CareerHub | Motherpher/CareerHub-Weronika | relocation/extraction pending |
| Grace | Hybrismannen/Gracey/CareerHub | Motherpher/CareerHub-Grace | relocation pending |

## Why Weronika is an extraction rather than a whole-repository transfer

`Hybrismannen/wpb` contains material beyond CareerHub. The CareerHub profile/state must therefore be extracted into a dedicated Motherpher repository while preserving WPB as its original broader repository.

## Why Grace can be relocated as a dedicated hub

`Hybrismannen/Gracey` is functioning as Grace's CareerHub repository. Its state/history should be preserved and moved into the dedicated stable target `Motherpher/CareerHub-Grace`.

## Relocation completion criteria

A relocation is complete only when:

1. profile/config/state/artifacts are present in the Motherpher target,
2. issue/application provenance is preserved or mapped,
3. registry points to the target,
4. stack.lock is regenerated,
5. repository-hard-coded links are eliminated,
6. central compatibility passes,
7. old location is archived or documented as migration provenance.

Repository creation/ownership transfer is an administrative GitHub operation and must not be simulated by merely changing repository strings in code.
