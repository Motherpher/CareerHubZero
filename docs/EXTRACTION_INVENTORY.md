# Extraction Inventory

This inventory classifies the first working WPB CareerHub implementation before centralization.

## Centralize

These are generic capabilities and belong in CareerHubZero after repository-independence review:

| WPB component | Target |
|---|---|
| `src/careerhub/models.py` | central runtime |
| `src/careerhub/state.py` | central runtime |
| `src/careerhub/sources.py` | central runtime |
| `src/careerhub/matching.py` | central runtime |
| `src/careerhub/hrdm.py` | central runtime |
| `src/careerhub/application.py` | central runtime |
| `hrdm/HRDM_R_v6.3.md` | canonical core |
| `hrdm/hrdm_result.schema.json` | canonical core |
| source configuration defaults | central configuration |
| issue/update request parsers | reusable adapters |
| deadline notification logic | reusable operations |

## Generalize before centralizing

| Component | Reason |
|---|---|
| `dashboard.py` | currently contains repository-specific links/context |
| `cli.py` | currently assumes WPB directory layout |
| GitHub workflows | currently assume one profiled repository and local paths |
| search profile | contains candidate-oriented search logic/keywords and needs defaults + instance overrides |

## Remain profiled

These belong to WPB, not CareerHubZero:

- `profile/candidate.yaml`
- private CV / LinkedIn reconciliation
- `data/job_vault.json`
- `data/applications.json`
- generated application cases
- candidate-specific search preferences
- candidate-specific dashboards and rendered case state
- personal notification destinations

## Rule

No file is moved merely because it exists inside the current CareerHub folder. Each component is classified by whether it represents **capability**, **configuration default**, **profile context**, or **live state**.
