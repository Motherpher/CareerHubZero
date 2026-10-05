# CareerHub Dual Web Architecture

Status: canonical design for Vercel-facing CareerHub sites.

## 1. System rule

CareerHub is one centrally developed motor with many individually designed hubs.

The split is strict:

1. **CareerHub Motor** — canonical capability, contracts, orchestration and managed web shell, owned by `Motherpher/CareerHubZero`.
2. **Personalised Hub** — person-specific evidence, search settings, state, content, tone, visual identity and UX composition, owned by the dedicated profile repository.

The personalised hub is not a fork of CareerHub. It is an instance that consumes the canonical motor and supplies a presentation layer.

## 2. Physical deployment model

Every personalised repository is Vercel-deployable and contains three zones:

```text
<profile-repository>/
├── careerhub.yaml                    # instance manifest
├── profile/                          # verified career evidence
├── config/                           # search and personal settings
├── personalisation/                  # PERSON-OWNED: never overwritten centrally
│   ├── hub.profile.yaml              # public-facing hub composition
│   ├── theme.tokens.json             # visual identity tokens
│   ├── voice.yaml                    # tone / copy behaviour
│   ├── navigation.yaml               # information architecture
│   └── content/                      # intros, labels, help copy, optional sections
├── data/                             # MACHINE-WRITTEN: jobs/application/runtime state
├── reports/                          # generated artifacts
└── site/
    ├── managed/                      # CENTRAL-OWNED: synced from CareerHubZero
    │   ├── app/
    │   ├── components/
    │   ├── lib/
    │   └── styles/
    ├── personal/                     # PERSON-OWNED optional custom components
    ├── package.json
    ├── next.config.mjs
    └── tsconfig.json
```

Ownership invariant:

- `site/managed/**` may be replaced by a CareerHub release.
- `personalisation/**` and `site/personal/**` may never be overwritten by a central sync.
- `data/**` and generated reports are state/artifact surfaces, not design sources.

## 3. What belongs in the CareerHub Motor

The motor owns all behaviour that should improve once for everybody:

- vacancy sourcing and normalization
- geography and location logic
- matching, ranking and triage
- verified-career evidence boundary enforcement
- HRDM-R execution and traceability
- role/employer contextual research
- candidate positioning
- application generation
- document generation
- job/application lifecycle state machine
- dashboard data contracts
- reusable UI primitives and accessibility behaviour
- navigation mechanics
- error/loading/empty states
- responsive behaviour
- telemetry hooks
- version/release compatibility
- Vercel-ready managed shell

Motor changes are made only in CareerHubZero.

## 4. What belongs in the Personalised Hub

The personalised layer owns everything that should feel specific to the person:

- display name and short identity line
- preferred language
- tone and vocabulary
- visual direction, typography scale, density, corner/radius character, imagery rules
- dashboard emphasis and ordering
- optional modules/sections
- guidance copy and microcopy
- portfolio framing
- evidence highlights
- preferred job-search views
- default filters and job families
- degree of explanation vs compactness
- public/private visibility choices

A person may therefore have a quiet editorial hub, a graphically expressive hub, a highly analytical control room, or a simpler guided job-search interface while running exactly the same motor.

## 5. User-facing information architecture

The primary interaction contract remains:

**Find jobs → Analyse? → Apply**

The web shell expands this into an intuitive surface without exposing implementation complexity.

Canonical top-level destinations:

- **Home** — current career position, priorities, next actions
- **Find** — job discovery, filters, geography, saved opportunities
- **Analyse** — HRDM role reading, fit, hidden need, assessment zones, positioning
- **Apply** — application workspace, evidence selection, drafts, documents
- **Track** — applied / contacted / interview / denied / withdrawn / accepted
- **Profile** — verified career evidence and source status
- **Library** — generated reports, CV variants, letters, portfolio artifacts

Each personalised hub may hide or rename secondary destinations but may not break the underlying state contract.

## 6. Home-screen composition contract

The central shell supplies slots; the personal layer determines ordering and emphasis.

Canonical slots:

1. identity / current direction
2. current priority
3. recommended next action
4. opportunity queue
5. application pipeline
6. recent HRDM analyses
7. evidence/profile health
8. search coverage / geography
9. generated artifacts

`hub.profile.yaml` controls which slots render and their order.

## 7. Design system strategy

CareerHub uses a two-level token system.

### Core tokens — central

Accessibility, spacing logic, breakpoints, focus treatment, semantic state colours, motion limits, component behaviour and minimum contrast are controlled centrally.

### Identity tokens — personal

The profile may set permitted variables such as:

- font families
- display/body scale preference
- surface density
- neutral/base palette
- accent palette
- radius family
- card treatment
- imagery mode
- illustration/photography preference
- motion character within central accessibility limits

Personal tokens are validated before build. Invalid or inaccessible combinations fall back to safe central defaults.

## 8. Runtime composition

At build/runtime the site resolves:

```text
CareerHub managed shell
        +
careerhub.yaml
        +
hub.profile.yaml
        +
theme.tokens.json
        +
voice.yaml
        +
verified profile/search/state data
        =
personalised CareerHub site
```

The motor never infers private-life facts into the matchable career profile. The existing separation between verified career sources, search wishes and private-life data remains mandatory.

## 9. Distribution model

CareerHubZero publishes a **managed web-shell payload**.

For each registered profile repository, the distribution process:

1. checks the profile manifest and compatibility
2. copies the current managed shell to `site/managed/`
3. updates the shell release marker
4. validates that personal-owned paths are unchanged
5. runs schema and build checks
6. opens or updates a release PR in the profile repository
7. Vercel creates a preview deployment from that PR
8. after validation, merge creates the production deployment

No central release may silently modify `personalisation/**`.

## 10. Vercel topology

Recommended stable topology:

```text
CareerHubZero
  └── develops/tests the shared motor and web shell

CareerHub-LinusF  ── Vercel Project: careerhub-linusf
wpb               ── Vercel Project: careerhub-wpb
Gracey            ── Vercel Project: careerhub-gracey
...
```

Each personalised repository gets its own Vercel project, production URL/domain, preview deployments and environment settings.

This gives independent presentation and release validation while retaining one upstream product body.

## 11. Release compatibility

A CareerHub release is valid only if:

- central motor tests pass
- managed shell tests pass
- personalisation schema tests pass
- each active profile manifest remains compatible
- each active profile web build succeeds
- protected personalisation paths are unchanged by sync

The central release ledger records the shell revision distributed to each profile.

## 12. Non-negotiable architectural sentence

**CareerHubZero owns capability and the reusable interaction shell. Each dedicated CareerHub repository owns the person, the presentation and the lived interface of that capability.**
