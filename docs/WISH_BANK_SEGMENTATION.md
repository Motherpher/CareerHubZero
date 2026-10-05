# Wish Bank Segmentation and Development Routing

Status: canonical routing rule.

Every wish is analysed on two independent axes before development work is created.

## Axis A — development target

- `MOTOR`: reusable CareerHub capability. If accepted, development belongs in CareerHubZero and propagates to all compatible personalised hubs.
- `PROFILE`: need specific to one person's profile, presentation, workflow or configuration. If accepted, development belongs on that profile's development line and must not silently alter other profiles.
- `BOTH`: contains a reusable motor improvement plus a person-specific adaptation. Split into linked motor and profile work where necessary.
- `UNTRIAGED`: automated intake could not safely determine scope. Human review is required before WP creation.

## Axis B — functional domain

Top-to-bottom domain tags are:

`PROFILE → SEARCH → GEOGRAPHY → ANALYSE → APPLY → TRACK → LIBRARY → UX → ACCESSIBILITY → PERFORMANCE → NEW_CAPABILITY → OTHER`

Additional cluster tags may be added during triage.

## Wishlists

The central bank therefore exposes two logical views from the same source records:

1. **Motor Wishlist** — wishes tagged `MOTOR` or `BOTH`; source for central CareerHubZero development WPs.
2. **Profile Wishlist** — wishes tagged `PROFILE` or `BOTH`, grouped by `profile_id`; source for that person's dedicated DevOp line.

No profile wish may change other personal profiles solely because it was implemented once. No motor wish should be repeatedly reimplemented in each profile when the underlying capability belongs centrally.

## Development gate

Automated segmentation is advisory at intake. Every record has `review_required=true`. WP derivation requires confirmation of target, domain, underlying user need, affected users, intended outcome and acceptance criteria.

The resulting WP must retain `wish_id` provenance so a released change can be traced back to the original user need and validated afterwards.
