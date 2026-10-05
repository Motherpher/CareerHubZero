# CareerHub Wish Bank — User Wish to Development WP

Status: canonical low-fi product feedback and development-routing architecture.

## 1. Purpose

Every personalised CareerHub must let the person submit a wish, friction point or improvement idea directly from their site.

The submission is routed to one central CareerHub Wish Bank. The Wish Bank is not a generic support inbox; it is a structured product-development source that can be reviewed, clustered, prioritised and converted into formal CareerHub development work packages (WPs).

## 2. User-facing rule

Every personalised site exposes a persistent action labelled in the person's language, for example:

- `Förbättra min CareerHub`
- `Jag önskar...`
- `Suggest an improvement`

The form should require only enough information to make the wish useful:

- What would you like to be easier, clearer or possible?
- Optional: where in CareerHub did this come up?
- Optional category

The site automatically adds technical context that the user should not have to know:

- profile/hub ID
- current page/route
- CareerHub version
- site language
- timestamp
- source site

No career evidence or uploaded document content should be copied into the Wish Bank automatically.

## 3. Wish lifecycle

```text
SUBMITTED
   ↓
NEW
   ↓
TRIAGED
   ↓
CLUSTERED / STANDALONE
   ↓
CANDIDATE_WP
   ↓
ACCEPTED | DEFERRED | DECLINED
   ↓
WP_CREATED
   ↓
IN_DEVELOPMENT
   ↓
RELEASED
   ↓
VALIDATED / REOPENED
```

## 4. Central Wish Bank record

Each wish receives a stable `wish_id` and retains:

- source profile ID
- display-name-safe source label
- submitted text
- optional location/page
- optional user-selected category
- automatically assigned triage categories
- status
- cluster ID if applicable
- affected capability/module
- frequency across users
- usability severity
- development leverage
- candidate WP ID
- created WP ID
- release/version if resolved
- validation result

## 5. Privacy boundary

The Wish Bank is a product-development dataset, not a career-evidence source.

Never automatically include:

- CV contents
- uploaded files
- application text
- sensitive profile attributes
- private-life information
- HRDM source material

A wish may include text intentionally typed by the user. The UI should remind the user not to paste sensitive personal information unless it is essential to the product issue.

## 6. Triage model

Initial triage dimensions:

### Category
- navigation / comprehension
- profile
- search
- geography
- analyse / HRDM
- apply
- track
- library / uploads
- accessibility
- visual / interaction design
- performance / reliability
- new capability
- other

### Scope
- one personal hub
- multiple hubs
- central motor
- managed web shell
- integration / infrastructure

### Severity
- `S0` cosmetic/minor
- `S1` inconvenience
- `S2` task friction
- `S3` blocks or materially impairs a core task

### Development leverage
- `L1` individual/local value
- `L2` reusable improvement
- `L3` system-wide product improvement

## 7. Clustering

The development review process should identify wishes that describe the same underlying user need even when users phrase them differently.

Example:

```text
Wish A: "I don't understand what profile the search is using."
Wish B: "Can I see my settings before I search?"
Wish C: "I keep forgetting which cities are active."

→ Cluster: SEARCH-CONTEXT-VISIBILITY
```

The cluster, rather than each sentence independently, can become the basis of a development WP.

## 8. WP derivation gate

A Wish or Wish Cluster becomes a candidate WP when the development review can state:

1. observed user problem;
2. affected CareerHub capability;
3. users/hubs affected;
4. evidence/frequency;
5. intended outcome;
6. likely central vs personal implementation boundary;
7. acceptance criteria;
8. regression risks.

Recommended WP source marker:

```text
source: WISH_BANK
wish_ids: [WISH-...]
cluster_id: WB-CLUSTER-...
```

This preserves the path from user experience to development decision.

## 9. Priority aid

The Wish Bank may calculate an advisory score:

```text
P = (severity × affected_users × recurrence × development_leverage) / estimated_effort
```

This is a prioritisation aid only. Human product/development review remains authoritative.

## 10. Site-to-bank routing

Personalised sites must not hold a central GitHub token.

Recommended topology:

```text
Personal CareerHub
      ↓
POST /api/wish   (same-site server route)
      ↓
central CAREERHUB_WISH_ENDPOINT
      ↓
Wish Bank service
      ↓
central structured store / development intake
```

The personal site route adds trusted hub metadata server-side. A shared server-to-server secret or equivalent authenticated mechanism protects the central endpoint.

## 11. Low-fi product requirement

For the current low-fi CareerHub product, the minimum viable implementation is:

- persistent `Wish / Improve` action on every managed site;
- simple form;
- confirmation with generated submission ID when accepted;
- central machine-readable Wish Bank contract;
- central triage states;
- explicit pathway from wish/cluster to development WP.

A later product iteration may add:

- user's own submitted-wishes history;
- status updates visible to the user;
- voting/"this affects me too";
- release notes linked back to wishes;
- automatic clustering suggestions;
- dashboard for Wish Bank trends.
