# CareerHub Non-Generic Profile Formula

Status: canonical derivation rule for personalised CareerHub presentation layers.

## 1. Purpose

Every CareerHub runs the same CareerHub Motor but must present as a genuinely person-specific career workspace. Personalisation may not be produced by changing a name, accent colour and hero sentence on a shared template.

A hub is considered personalised only when its information hierarchy, interaction emphasis, tone, visual grammar and profile/search presentation can be traced to evidence about that person's work, preferences and explicitly supplied visual references.

## 2. Core formula

```text
NGH(person) = CH-Core
            + Identity Signature
            + Work-Logic Signature
            + Information-Need Signature
            + Career-Surface Signature
            + Voice Signature
            + Visual-Grammar Signature
            + Interaction Signature
            + Reference Provenance
```

`CH-Core` is invariant CareerHub capability and accessibility behaviour. The remaining signatures are derived per person.

## 3. Source classes

Derivation must use only relevant, permitted sources:

1. **Verified career evidence** — current/historical CVs, verified project records, accepted profile evidence.
2. **Explicit user decisions** — stated workflow, navigation, information-density, search and presentation preferences.
3. **Conversation-derived working style** — repeated non-sensitive interaction preferences that materially affect usability, such as directness, compactness, analytical depth, or preferred information ordering.
4. **Visual references** — Pinterest/Behance/design links or supplied images explicitly nominated as references.
5. **Observed usability evidence** — feedback from the person using their CareerHub.

Sensitive personal attributes must never be inferred into a design profile. Private-life information does not become a visual, career or matching signal.

## 4. Eight derivation vectors

### V1 — Identity Signature

Defines how the person is named and professionally framed on the site. It derives from verified career positioning, not repo names or product labels.

Outputs: display name, professional framing, profile headline, identity prominence.

### V2 — Work-Logic Signature

Defines how the person's work is naturally organised. Examples include systems/process, portfolio/craft, operational delivery, advisory practice, analytical research, creative production or mixed modes.

Outputs: primary information groupings, dashboard module families, profile section architecture.

### V3 — Information-Need Signature

Defines what the person needs to understand first and how much explanation they need.

Outputs: density, progressive disclosure, guidance level, dashboard ordering, advanced/audit visibility.

### V4 — Career-Surface Signature

Defines which distinct professional surfaces should be visible without fragmenting the underlying evidence profile.

One person may legitimately need several views of the same verified evidence with different signal ordering.

Outputs: surface/view definitions, evidence emphasis, portfolio emphasis, search entry points.

### V5 — Voice Signature

Defines wording behaviour.

Outputs: posture, sentence length tendency, directness, terminology, microcopy style, prohibited generic phrases.

### V6 — Visual-Grammar Signature

Derived from explicit visual references. The visual harvest records:

- typography character
- grid/layout rhythm
- whitespace/density
- geometry
- hierarchy
- colour logic
- card/surface behaviour
- iconography
- data-visualisation language
- imagery/illustration language
- motion character

A Pinterest URL alone is not sufficient for `VISUAL_LOCK`; a visual-harvest record must state what was actually observed. If a reference cannot be directly inspected, register it as `REFERENCE_PENDING` rather than inventing design attributes.

### V7 — Interaction Signature

Defines how the person moves through Profile → Search → Analyse → Apply → Track.

Outputs: default landing emphasis, primary actions, search-control exposure, library prominence, edit/review behaviour.

### V8 — Reference Provenance

Every non-default design decision records why it exists and where it came from.

Recommended source states:

- `VERIFIED_CAREER`
- `EXPLICIT_USER`
- `CHAT_PATTERN`
- `VISUAL_HARVEST`
- `USABILITY_TEST`
- `REFERENCE_PENDING`

## 5. Derivation sequence

```text
S1 Gather permitted sources
S2 Extract working/profile signals
S3 Build eight-vector signature
S4 Harvest nominated visual references
S5 Resolve information architecture
S6 Resolve voice grammar
S7 Resolve visual tokens and component character
S8 Resolve interaction emphasis
S9 Build personalised configuration
S10 Anti-generic audit
S11 User preview/usability pass
S12 PERSONALISATION_LOCK
```

If S4 cannot be completed, the hub may reach `STRUCTURE_READY` but not `PERSONALISATION_LOCK`.

## 6. Anti-generic audit

A profile fails if any of the following is true:

- identity differs from the template but module order and information hierarchy do not;
- only colour, avatar or headline changed;
- voice is the default CareerHub template voice with no source-backed adaptations;
- visual attributes are claimed from an uninspected reference;
- the hub cannot explain at least five material person-specific design decisions with provenance;
- career surfaces are collapsed into one generic CV view when evidence supports materially different professional readings;
- design introduces unsupported career claims;
- personalisation relies on sensitive/private-life attributes.

Minimum lock conditions:

1. at least five material person-specific decisions;
2. at least four active derivation vectors beyond identity;
3. explicit provenance for each major deviation from the central defaults;
4. no unresolved accessibility failure;
5. no unsupported career evidence;
6. usability preview completed with the person or authorised reviewer.

## 7. Genericity distance

The motor should calculate a simple audit value, not as aesthetic truth but as a guardrail.

```text
G = changed_material_dimensions / eligible_material_dimensions
```

Eligible material dimensions are: information hierarchy, module ordering, career surfaces, voice, density, visual grammar, interaction defaults and content framing.

`G < 0.35` = likely cosmetic personalisation — FAIL/WARN.

`0.35 <= G < 0.60` = differentiated but requires audit.

`G >= 0.60` = materially differentiated; still requires provenance and usability validation.

A high G never compensates for weak provenance or poor usability.

## 8. Output files per personalised repo

```text
personalisation/
  hub.profile.yaml
  theme.tokens.json
  voice.yaml
  derivation.yaml
  references.yaml
  visual-harvest.yaml
```

`derivation.yaml` explains why the interface is shaped this way. `references.yaml` registers source references. `visual-harvest.yaml` separates actual observed visual characteristics from pending references.

## 9. Central invariant

**CareerHubZero supplies capability, safety, accessibility and reusable interaction primitives. The person-specific repo supplies an evidence-derived composition of those primitives. No personalised hub is valid merely because it looks different; it must work differently where the person's actual career workflow requires it.**
