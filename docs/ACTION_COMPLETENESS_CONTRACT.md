# CareerHub Action Completeness Contract

## Purpose

A CareerHub surface is not complete when it only describes a capability. Every primary user task must expose the control needed to perform the next governed action, or explicitly route the user to the surface where that action is performed.

The canonical journey is:

`Profile → Search → Analyse → Apply → Track`

with `Library` and `Improve my CareerHub` as supporting surfaces.

## Action rule

For every user-visible capability, CHZero must define all four layers:

1. **Visible control** — button, form, dropdown, file selector or link.
2. **Choice contract** — the user can make every decision required before execution.
3. **Execution path** — synchronous web API or central motor dispatch.
4. **Result state** — the user receives a result, reference, artifact, updated state or an explicit governed review request.

A surface that only explains a future capability fails this contract.

## Canonical action matrix

| Surface | User action | Required controls | Execution path | Result |
| --- | --- | --- | --- | --- |
| Home | Continue work | Profile / Search / Analyse / Apply / Track / Library navigation | route navigation | target workspace |
| Profile | Add or update evidence | Add evidence | Library | uploaded source |
| Profile | Resolve verification constraint | Add evidence / Request review | `/api/action` → `profile_review` | governed review request |
| Profile | Rebuild from active sources | Request rebuild | `/api/action` → `profile_rebuild` | governed rebuild request |
| Search | Run search | lane dropdown, session-only need, Run search | `/api/search` | ranked opportunities |
| Search | Inspect role | Open role | external vacancy URL | source vacancy |
| Search | Continue into analysis | Analyse in CareerHub | query handoff to `/analyse` | prefilled drill form |
| Analyse | Choose role | saved-role dropdown or manual role fields | client form | drill input |
| Analyse | Resolve blocked vacancy retrieval | pasted job text | drill form | manual source text |
| Analyse | Choose application lane | Core / Adjacent / Bridge dropdown | drill form | governed lane |
| Analyse | Choose Hybridianesque filter | Yes / No dropdown | drill form | explicit filter decision |
| Analyse | Run HRDM-R | Run HRDM-R and prepare application | `/api/action` → `analyse_role` → managed workflow | HRDM run + application package + case |
| Apply | Start application | Analyse a role and prepare application | `/analyse` | governed drill |
| Apply | Retrieve application | Download application / data | `/api/artifact` | generated artifact |
| Apply | Review analysis | HRDM report when bound | `/api/artifact` | report artifact |
| Apply | Continue to tracking | Update status | `/track` | tracking workspace |
| Track | Change state | status dropdown | `/api/action` → `track_status` | updated canonical case |
| Track | Change priority | priority dropdown | `/api/action` → `track_priority` | updated canonical case |
| Track | Set next action | text + date controls | `track_status` payload | updated next action |
| Library | Upload | file selector | `/api/library` | private Blob source |
| Library | Classify source | document-class dropdown | `/api/library` | classified source path |
| Library | Choose source state | ACTIVE / INACTIVE dropdown | `/api/library` | explicit initial state |
| Library | Open source | Open | `/api/library/file` | private file stream |
| Library | Activate / deactivate | Activate / Deactivate | `/api/library` PATCH | state change |
| Library | Request evidence review | Request evidence review | `/api/action` → `library_review` | governed review request |
| Library | Reload active index | Reload CareerHub Library | `/api/library/reload` | rebuilt active-source index |
| Library | Delete source | Erase + confirmation | `/api/library` PATCH | source removed |
| Improve | Submit product wish | text, category, context | `/api/wish` | Wish Bank record |

## Execution modes

### Synchronous web actions

Used when the personalised Vercel site can complete the action directly:

- search
- Library upload/open/activate/deactivate/erase/reload
- Wish Bank submission
- artifact download

### Central motor actions

Used when the canonical Python motor must execute the operation:

- HRDM-R role analysis
- application package generation
- application status / priority / event updates
- governed source/profile review requests

The personalised site calls `/api/action`. The gateway records the action where Blob storage is available and dispatches `.github/workflows/careerhub-operations.yml` when the profile deployment has its GitHub dispatcher configured.

Required profile-deployment environment variables:

- `CAREERHUB_GITHUB_REPOSITORY` — `owner/repo`
- `CAREERHUB_GITHUB_TOKEN` — credential allowed to dispatch the profile workflow
- optional `CAREERHUB_GITHUB_WORKFLOW` — defaults to `careerhub-operations.yml`
- optional `CAREERHUB_GITHUB_REF` — defaults to `main`

`sync_web_shell.py` installs both the managed web shell and the managed operations workflow. A profile must therefore not maintain a divergent local copy of the workflow.

## Evidence boundary

Action completeness never weakens the evidence policy.

- Upload does not equal verification.
- ACTIVE means available for governed use, not automatically true.
- Review/rebuild requests do not silently mutate the Career Profile.
- Search-only needs do not become candidate evidence.
- Application generation remains bounded by verified profile evidence.

## Acceptance gate

A CHZero release affecting the personalised surface must fail review if any primary route contains a user-facing promise such as “can”, “run”, “update”, “upload”, “analyse”, “apply”, “track”, “review” or “rebuild” without a corresponding visible control and execution path.
