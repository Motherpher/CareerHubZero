# Development Principles

## 1. Capability and context stay separate
Central code is reusable. Profile evidence, search preferences and application state stay in the profiled instance.

## 2. Verified career sources only
The matchable candidate profile may be generated only from **verified career sources**.

Accepted source classes are CV, professional profile, employment record, qualification, certification, portfolio/work sample, employer reference and verified project record.

If a claim cannot be bound to one of these verified career sources, it is not matchable candidate evidence.

## 3. No private-life evidence
Private-life information must never enter the matchable profile.

Family, relationships, health, religion, ethnicity, sexual orientation, political affiliation, personal finance and unrelated private notes are outside the CareerHub candidate-evidence model.

Unknown means unknown. Unverified career claims go to verification, not into matching.

## 4. User wishes are a search raster, not evidence
A user may add **specific wishes or needs** when running a search.

That input must have source = user_input and scope = search_only. It may affect sourcing, filtering and ranking. It may never become a CV claim, candidate capability, HRDM proof point or matchable profile fact.

The profile answers **what is verified about the career**. The search overlay answers **what the person wants the search to consider right now**.

These layers must remain separate.

## 5. Human-facing simplicity
The visible journey is:

**Find → Analyse? → Apply**

Complexity belongs behind the interface.

## 6. Evidence before persuasion
Application drafting follows verified career evidence and the HRDM analysis. The system must not manufacture stronger claims because they would sound better.

## 7. HRDM remains explicit
HRDM-R is a canonical analytical sequence, not a vague prompt label.

## 8. State is durable
Jobs should not disappear merely because the latest sourcing run changes.

## 9. Development must not break live instances
Central changes are versioned, validated and tested before profiled instances adopt them.

## 10. Secrets are infrastructure, not content
API keys, phone numbers, notification credentials and other secrets must never be committed to source control.

## 11. Data minimisation is structural
CareerHub stores career evidence, search settings and application state only to the extent needed for the service.

## 12. Repository independence
Central code must not hard-code a specific GitHub owner/repository.
