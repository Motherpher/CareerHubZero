# CareerHub Personal Workspace — Profile, Library and Search Architecture

Status: canonical UX/data architecture for personalised CareerHub sites.

## 1. Product rule

A personalised CareerHub is not presented as a repository or technical system. It is presented as the **person's own career workspace**.

The visible site identity is the person's name and chosen professional framing. Repository names, internal profile IDs, Motor versioning and deployment infrastructure remain implementation details.

Examples:

- site title: `Linus Fast`
- site title: `Weronika Perez Borjas`
- site title: `Grace ...`

A Vercel project may use an internal technical slug such as `careerhub-linusf`; the rendered product must not expose that as the person's identity.

## 2. Primary user journey

The canonical user-facing sequence becomes:

**Profile → Search → Analyse → Apply → Track**

This replaces a system-centric navigation model with a task-oriented career journey.

### Profile

Understand and manage what CareerHub currently knows about me.

### Search

Use my saved search preferences as the starting point, then override them for this search if needed.

### Analyse

Understand the role, fit, hidden need, assessment logic and positioning through HRDM-R.

### Apply

Build the application from verified/active evidence and the current role analysis.

### Track

Follow application state, contacts, interviews, outcomes and next actions.

Secondary destinations:

- **Library** — source documents and generated artifacts
- **Settings** — persistent search preferences, language and presentation choices

## 3. Home screen

The home page must answer three questions without requiring the user to understand CareerHub internals:

1. **Where am I now?**
2. **What should I do next?**
3. **What has changed?**

Recommended composition:

- personal identity header
- current career direction / target profile
- primary next-action card
- profile status: current / needs review / new evidence available
- saved search area summary
- recent opportunities
- active applications
- recent uploaded documents
- recent HRDM analyses

Avoid exposing internal labels such as schemas, ledgers, Process-ID or engine terms unless the user enters an advanced/audit view.

## 4. Profile workspace

`Profile` is the canonical visual representation of the person's **latest active CareerHub profile**.

It must show, in human-readable sections:

- identity / professional summary
- current career direction
- experience timeline
- education
- competencies
- methods / tools / systems
- sector/domain experience
- languages
- selected achievements/evidence
- portfolio/public artifacts where relevant
- current search defaults
- source freshness / evidence status

Every rendered profile claim must retain source provenance internally.

### Profile states

- `CURRENT` — no unresolved accepted evidence changes
- `REVIEW_AVAILABLE` — new extracted evidence is ready for review
- `DRAFT_CHANGED` — user has edited profile fields not yet confirmed
- `REBUILD_REQUIRED` — active source library changed and profile should be regenerated

The user must always be able to see which profile version is currently active.

## 5. Personal document library

Each personalised CareerHub gets a private document library for user-supplied career material.

Typical uploads:

- CV versions
- certificates
- diplomas
- employment certificates
- role descriptions
- work samples
- portfolio documents
- project descriptions
- reference material
- course records
- previous applications when intentionally supplied as evidence/context

Files are not automatically treated as truth merely because they were uploaded.

## 6. Document lifecycle

Each uploaded document follows an explicit lifecycle:

```text
UPLOAD
  ↓
STORED
  ↓
EXTRACTED
  ↓
REVIEW / CLASSIFICATION
  ↓
ACTIVE  ↔  INACTIVE
  ↓
DELETED
```

### UPLOAD / STORED

The original file is stored privately.

Recommended Vercel implementation: **private Vercel Blob storage**, authenticated through the personalised site. The file itself should not be committed to GitHub merely to make the Motor read it.

### EXTRACTED

CareerHub extracts machine-readable content and metadata:

- filename
- MIME/type
- upload date
- document class
- text content
- dates/entities when detectable
- source hash
- extraction status

### REVIEW / CLASSIFICATION

The user can see what was extracted and how CareerHub proposes to use it.

Proposed evidence must be distinguishable from already verified active profile evidence.

### ACTIVE

The document is available to the CareerHub Motor as an authorised source.

### INACTIVE

The document remains in the user's library but is excluded from profile rebuilding, matching and application evidence.

### DELETED

The source file and its active library reference are removed according to deletion rules. Historical generated artifacts may retain a provenance statement that a now-deleted source had previously contributed, without retaining the deleted file content unless required by explicit archival policy.

## 7. Library controls

The Library UI must support:

- Upload document
- Open / preview document
- See extraction status
- See document classification
- See where the document contributes to profile data
- Activate source
- Deactivate source
- Delete source
- Re-run extraction
- **Reload CareerHub Library**

### Reload CareerHub Library

This is an explicit user action that tells the Motor to rebuild its readable source index from all `ACTIVE` library items and canonical verified profile sources.

The action should produce a simple result such as:

> Library reloaded — 14 active sources read. 2 new profile changes are available for review.

It must not silently rewrite the active profile.

## 8. Evidence promotion into the profile

Document ingestion and profile mutation are separate operations.

```text
ACTIVE SOURCE
   ↓
EXTRACTED EVIDENCE
   ↓
PROPOSED PROFILE CHANGE
   ↓
USER REVIEW
   ↓
ACCEPT / REJECT / EDIT
   ↓
ACTIVE PROFILE
```

This prevents a badly parsed document or obsolete CV from silently overwriting the person's current profile.

Accepted changes become part of the active profile and retain source lineage.

## 9. Search defaults

Each person has a persistent **Search Profile** that supplies the default starting point for job discovery.

Recommended default fields:

- geographic areas
- maximum travel/commute logic
- remote/hybrid/on-site preferences
- role families
- target role level
- sectors/domains
- employer types
- employment type
- workload preference if used
- language requirements/preferences
- salary constraints where intentionally configured
- explicit exclusions
- weighting/priorities

These settings are persistent and editable in Profile/Settings.

## 10. Search-session overrides

A search must always start from the user's saved Search Profile, but the user may alter parameters **for this search only**.

Example:

```text
My defaults
Stockholm + Uppsala
Hybrid preferred
Strategy / development / analysis
Public + civic + selected private

[Change for this search]
```

A session override can change geography, role family, sector or other search criteria without mutating the persistent profile.

After the search, CareerHub may offer:

- `Keep as one-time search`
- `Save these changes to my Search Profile`

Persistent settings therefore remain stable unless the user deliberately updates them.

## 11. Geography interaction

Geography should not be presented as a technical query field.

Recommended interface:

- map + searchable place selector
- saved areas displayed as chips/cards
- `Add area`
- `Remove area`
- radius / commute options where meaningful
- remote/hybrid overlay
- country/region/municipality hierarchy when supported by authoritative adapters

The search page displays the active geographical scope before the search runs.

## 12. Search page sequence

```text
1. CareerHub loads saved Search Profile
2. User sees the active search scope in plain language
3. User may edit temporary filters
4. User presses Search
5. Results are ranked against:
      a. the active career profile
      b. current search parameters
      c. CareerHub matching logic
6. User can save, dismiss, analyse or open a role
```

The user should never need to understand the distinction between config files, match vectors or internal ranking structures to perform this operation.

## 13. Profile and search separation

Two concepts remain separate:

### Career Profile

**What can this person credibly claim and carry?**

Derived from verified/accepted career evidence.

### Search Profile

**What does this person currently want CareerHub to look for?**

Derived from explicit user preferences and search choices.

A Search Profile may influence sourcing and ranking but may never create career claims.

## 14. Full runtime composition

```text
PRIVATE SOURCE LIBRARY
       ↓
active verified/accepted evidence
       ↓
CAREER PROFILE ───────────────┐
                             │
SEARCH PROFILE ───────┐       │
                      ↓       ↓
              SEARCH / MATCHING
                      ↓
                 OPPORTUNITY
                      ↓
                   HRDM-R
                      ↓
              APPLICATION WORKSPACE
                      ↓
                    TRACK
```

Personal presentation wraps the whole experience but does not alter the evidence boundary.

## 15. Storage architecture

Recommended deployment split:

### Dedicated GitHub profile repository

Owns durable structured CareerHub state/configuration intended for versioned audit and Motor compatibility.

### Private Vercel Blob

Owns uploaded binary source documents and other private user files.

### CareerHub Motor

Reads authorised structured state + active source library through authenticated interfaces.

The Motor should never expose private Blob URLs directly in public UI.

## 16. Authentication and access

Every personalised CareerHub is a private personal workspace unless deliberately configured otherwise.

Uploads, profile editing, source activation/deactivation/deletion and application content require authenticated access.

Private source files must be served through authenticated routes rather than public blob URLs.

## 17. Site identity rule

Visible product identity is configured separately from repository identity.

Example:

```yaml
identity:
  display_name: "Linus Fast"
  workspace_title: "Career Workspace"
  professional_line: "Strategic process designer"
```

Rendered header:

```text
Linus Fast
Career Workspace
```

Not:

```text
CareerHub-LinusF
Motherpher/CareerHub-LinusF
careerhub-linusf
```

Repository and deployment identifiers are visible only in advanced technical/audit contexts.

## 18. Motor-owned components required

CareerHubZero should centrally provide reusable components for:

- ProfileSummary
- ProfileTimeline
- ProfileEvidenceStatus
- SearchProfileEditor
- GeographyPicker
- SearchSessionOverrides
- DocumentUploader
- SourceLibrary
- SourceStatusControl
- ExtractedEvidenceReview
- ReloadLibraryAction
- OpportunityList
- OpportunityCard
- HRDMWorkspace
- ApplicationWorkspace
- PipelineTracker

Individual hubs control styling, density, ordering and copy through their protected presentation layer.

## 19. Usability acceptance criteria

A new user should be able to perform the following without explanation of CareerHub architecture:

1. identify that the site belongs to them;
2. see their latest profile;
3. understand which sources CareerHub currently uses;
4. upload a new career document;
5. activate/deactivate/delete an uploaded source;
6. reload the source library;
7. review proposed profile changes;
8. see and change their saved geographical/search settings;
9. run a search from those defaults;
10. temporarily alter a search without destroying the defaults;
11. analyse an opportunity;
12. start an application;
13. understand the state of active applications.

If these tasks require knowledge of repository structure, HRDM internals, config files or Motor vocabulary, the interface has failed.

## 20. Architectural sentence

**The CareerHub Motor maintains the intelligence. The personalised site maintains the person's working relationship with that intelligence: their evidence, profile, search intent, documents, decisions and career journey.**
