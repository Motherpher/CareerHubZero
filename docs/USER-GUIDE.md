# CareerHubZero — User Guide and Operating Navigation v0.1

**Document ID:** FF-GH-WO-002-WP01-CareerHub-UG · **Date:** 2026-11-03  
**Status:** SOURCE-LINKED GUIDE CANDIDATE — **not** independently tested against a deployed, authenticated CareerHub profile instance.  
**Audience:** authorised users of CareerHub profile hubs, administrators and support reviewers.  
**Canonical software body:** [CareerHubZero](../README.md). **In-app Help source:** [Help page](../web-shell/site/app/help/page.tsx) and [bilingual content](../web-shell/site/app/help/HelpClient.tsx).

## 1. What the system is

CareerHubZero is the reusable software body and managed web shell for CareerHub. Individual profile nodes carry verified personal career evidence, preferences and protected presentation. They do not create independent versions of the shared engine. The user contract in the canonical [README](../README.md) is:

**Profile → Search → Analyse → Apply → Track**, supported by **Library** and **Help**.

CareerHub's current `0.2.9-alpha` line and its source-defined routes are not proof of full 1.0 readiness or completed production/profile cutover; check current Issues and release gates before claiming functionality.

## 2. Find your workspace

| User objective | Source-defined route | Meaning |
|---|---|---|
| See your hub | `/` or `/career` | Profile-hub overview; available screens may vary by profile |
| Review professional evidence | `/profile` | Verify and maintain professional facts |
| Find jobs | `/find` | Search and filter vacancies |
| Assess roles | `/analyse` | Structured role analysis and evidence |
| Work on applications | `/apply` | Application actions and outputs |
| Follow the process | `/track` | Application tracking and statuses |
| Read supporting evidence | `/library` | Source and artifact Library |
| Ask a question | `/help` | Searchable in-app Help, Swedish or English by profile language |
| Suggest an aspiration | `/wish` | Temporary wish/search intent, not verified career evidence |

These routes were identified in `web-shell/site/app/` on repository `main` (2026-11-03). **Source code does not prove your deployed instance or permissions expose the exact same routes.** Use the navigation actually available in your authorised hub.

## 3. Profile — verified evidence first

1. Open the Profile workspace.
2. Review existing professional records, documents and source status for accuracy.
3. Add or request correction through the application's available controls when your career evidence changes.
4. Where provided, request rebuild/review. Treat the outcome as pending until the system explicitly verifies it.

**Critical distinction:** Saved Search Profile, transient search filters and aspirational Wishes must not silently modify verified candidate evidence. Your application assertions should be supported by current, relevant evidence, not the mere presence of a user preference.

## 4. Search — separate successful zero from failure

1. Use Search to define role, sector, geography or other applicable criteria.
2. Check whether you are editing the *saved Search Profile* or temporary Search-page filters.
3. Run the search where the current, authenticated instance allows it.
4. Interpret source/run status before interpreting count or geographic distribution.

The source Help defines `NEW`, `SEEN` and `CHANGED` for comparable successful runs. A genuine successful `0 new jobs` is **not** the same as a source/API/execution error. Do not convert an unavailable source into a valid zero.

**Potential external limits:** Third-party APIs, rate limits, geocoding and credentials may restrict a route. The [capability audit](CAPABILITY_AUDIT_0.2.7.md) is historical evidence of specific earlier incomplete parts, not a replacement for an exact current deployed run.

## 5. Analyse — read the evidence and the rationale

1. Select a vacancy or role with appropriate source context.
2. Open Analyse, inspect the role context and the relevant evidence-backed comparison.
3. Review HRDM-R results and report state where the feature is present.
4. Distinguish actual vacancy data, inference, candidate evidence and unsupported assumptions.

The current [Motor Guide source](../web-shell/site/app/_components/MotorGuide.tsx) describes HRDM-R as reverse role analysis and Hybridianesque as a conditional depth filter. A visible analysis output must not be treated as a verified external employer decision or a guaranteed prediction.

Some analyses execute asynchronously: use the source-defined action/reference status. A pending/failed action is not a completed analysis.

## 6. Apply — produce a bounded submission artifact

1. Select the role and correct candidate profile context.
2. Review draft material for factual truthfulness, relevance and proper use of evidence.
3. Ensure the document's target employer, deadline, source and output version are clear.
4. Treat generation/export and **actual submission** as separate states.
5. Never assume an external application was submitted without an explicit confirmation/receipt.

Do not copy identifying personal data into public GitHub Issues or documentation; profile privacy controls apply.

## 7. Track — maintain reconstructable application history

The Track workspace should distinguish draft, ready, submitted, interview, outcome and blocked state according to the **actual** available implementation. Confirm source references, timestamps and any external receipts rather than inferring completion from a dashboard colour or newly created artifact.

Unexpected failures or duplicate records should be reported using the appropriate protected channel with IDs and non-sensitive diagnostics.

## 8. Library, Help and Wish

- **Library:** use the permitted workspace for underlying files/evidence/artifacts. A source being uploaded does not itself make its content verified.
- **Help:** open `/help`, search in the current profile language. The source provides searchable topics for Profile, Search, Job Analysis, Apply, Track, Library, statuses/background work, sources/evidence, errors and privacy.
- **Wish:** a wish affects intended search scope or exploration, not candidate facts. Preserve the distinction between *what you want* and *what is verified about you*.

## 9. Troubleshooting

| Symptom | Correct interpretation and action |
|---|---|
| No access | Check authorised profile-instance URL/login and deployment state; don't invent credentials |
| 0 results | First confirm a successful comparable search; inspect source errors separately |
| No current analysis | Check the action status and source; don't assume a queued task has completed |
| Job data inaccurate | Verify original vacancy and timestamp; flag discrepancy without altering source facts silently |
| Profile fact missing | Ask for source-backed review/rebuild; Search filters are not substitutes |
| Saved application but no confirmation | Treat submission as UNVERIFIED until an independent receipt exists |
| Feature documented but not functioning | Record actual instance/version and error; do not declare release readiness from guide text |

## 10. Source provenance and change control

This guide interprets these repository sources (main as of 2026-11-03):

- [CareerHubZero README](../README.md) (identity, alpha state, user contract, profile separation)
- [Help page](../web-shell/site/app/help/page.tsx) and [Help content](../web-shell/site/app/help/HelpClient.tsx)
- [Motor Guide](../web-shell/site/app/_components/MotorGuide.tsx)
- [Web route tree](../web-shell/site/app/)
- [Historical capability audit 0.2.7](CAPABILITY_AUDIT_0.2.7.md)
- [Source Issues](https://github.com/Motherpher/CareerHubZero/issues) for current defects and releases

**Maintenance trigger:** Changes to the user journey, profile contract, source API binding, Help text, actual deployed routes or verified runtime status require guide/source reconciliation through a reviewed PR. The source owner must confirm the appropriate maintainer.

**Independent usability test:** NOT RUN in this WP01 source-documentation pass. A real user must complete Profile → Search → Analyse → Apply → Track in the authorised running instance before that end-to-end workflow is described as verified.
