# Migration: WPB CareerHub → CareerHubZero

## Objective

Extract the generic CareerHub capability currently embedded in `Hybrismannen/wpb` into `Motherpher/CareerHubZero` without disrupting the working WPB instance.

## Source implementation

Current source:

```text
Hybrismannen/wpb/CareerHub
```

The source contains both generic machinery and Weronika-specific profile/state. These must be separated.

## Migration sequence

### M0 — Establish central repository
Status: **IN PROGRESS**

- define architecture boundary
- define profiled-instance contract
- preserve HRDM canonical specification
- create version line
- establish validation

### M1 — Extract pure core
Move/generalize:

- models
- state primitives
- source adapters
- matching
- HRDM engine
- application generation
- document generation

No person-specific data may enter central core.

### M2 — Remove repository hard-coding
Known early implementation assumption:

```text
Hybrismannen/wpb
```

All repository/instance references must become injected runtime context.

### M3 — Extract workflow templates

Turn WPB-specific workflows into reusable workflow contracts.

The central engine must not assume:
- repository owner
- repository name
- candidate identity
- issue numbering
- profile path beyond declared instance configuration

### M4 — Profile WPB explicitly

WPB becomes a profiled instance with:
- candidate profile
- search preferences
- job/application state
- generated/user-facing views

### M5 — Dual-run validation

For a controlled test job:
1. run legacy WPB implementation
2. run CareerHubZero against the same WPB instance data
3. compare HRDM structure
4. compare application artifact generation
5. compare state transitions
6. verify no person-specific leakage into central repository

### M6 — Cutover

Only after parity:
- WPB calls CareerHubZero
- duplicate engine code is removed from WPB
- CareerHubZero becomes canonical central operations
- WPB remains canonical Weronika profile/state

## Non-goal

This migration does **not** merge private profiled data into CareerHubZero.
