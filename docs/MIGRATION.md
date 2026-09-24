# Migration: Legacy CareerHubs → CareerHubZero

## Objective

Extract the generic CareerHub capability embedded in legacy profile repositories into `Motherpher/CareerHubZero` without losing profile evidence, job history, application state or provenance.

## Active migration sources

### Weronika
Legacy source:
```text
Hybrismannen/wpb/CareerHub
```

Stable target:
```text
Motherpher/CareerHub-Weronika
```

### Grace
Legacy source:
```text
Hybrismannen/Gracey/CareerHub
```

Stable target:
```text
Motherpher/CareerHub-Grace
```

Grace has already been policy-normalised to the verified-career evidence firewall and registered in the central stack, but her local motor remains until central parity is available.

## Already-central profile

### Linus
```text
Motherpher/CareerHub-LinusF
```

Linus is already a thin repository but must still be migrated to the current candidate-evidence contract before 1.0.

## Migration sequence

### M0 — Central repository and governance
Status: **ACTIVE**

- architecture boundary defined,
- profiled-instance contract defined,
- version governance defined,
- Grace registered,
- 1.0 Full Audit Lock defined,
- Motherpher stable ownership boundary defined.

### M1 — Extract pure core
Move/generalize:

- models,
- state primitives,
- source adapters,
- matching,
- HRDM engine,
- application generation,
- document generation,
- dashboard/rendering,
- workflow/bootstrap logic.

No person-specific data may enter central core.

### M2 — Remove repository hard-coding

All repository/instance references must become injected runtime context.

The same engine must operate against Linus, Weronika and Grace without source-code changes.

### M3 — Extract workflow templates

Turn profile-specific GitHub Actions implementations into reusable CareerHubZero workflows.

The central engine must not assume:
- repository owner,
- repository name,
- candidate identity,
- issue numbering,
- profile path beyond declared instance configuration.

### M4 — Profile every instance explicitly

Each active hub receives:
- canonical `instance.yaml`,
- canonical verified career profile,
- canonical search profile,
- job/application state,
- generated `stack.lock.yaml`.

### M5 — Preserve and classify legacy state

For Grace:
- preserve the 159-job history,
- preserve application issue #2,
- keep the pre-firewall application artifact for provenance,
- block that artifact from external use until revalidated.

For Weronika:
- preserve existing job/application/corpus-derived professional state,
- migrate only source-supported candidate evidence into the current contract.

### M6 — Dual-run validation

For controlled jobs:
1. run the legacy profile implementation,
2. run CareerHubZero against the same profile state,
3. compare HRDM structure,
4. compare application artifact generation,
5. compare state transitions,
6. verify no person-specific leakage into central repository.

Run this separately for Weronika and Grace.

### M7 — Repository relocation to Motherpher

After state preservation is verified:

- relocate Grace to `Motherpher/CareerHub-Grace`,
- extract Weronika CareerHub into `Motherpher/CareerHub-Weronika`,
- update the central registry,
- update generated locks,
- update any remaining repository references,
- preserve legacy source repositories as provenance/redirect sources as appropriate.

### M8 — Cutover

Only after parity:
- profile hubs call CareerHubZero,
- duplicate engine code is removed from WPB and Grace,
- CareerHubZero becomes the only canonical motor,
- all profile repositories remain profile/config/state/artifact only.

### M9 — Full audit and 1.0 lock

Run the complete 1.0 audit across:
- CareerHubZero,
- Linus,
- Weronika,
- Grace.

Only a full PASS permits `VERSION = 1.0.0`.

## Non-goal

Migration does **not** merge private profile data into CareerHubZero.
