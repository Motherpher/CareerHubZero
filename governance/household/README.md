# CareerHub Household Support

CareerHub uses the Household family as an **external governance/clearance layer** for the CH-1.0-SILICON sprint. Household is not part of CareerHub product intelligence.

Roles:
- **Director** — progression and immutable clearance. Never repairs.
- **Handyman** — J1 bounded deterministic repairs only. Never self-certifies.
- **Janitor** — drift, contradiction, security, provenance and hygiene surveillance.
- **Household** — orchestrates the roles without acquiring additional authority.

## Audit state order

Every WP audit must preserve this order:

1. DISPATCHED
2. JANITOR_SCAN
3. HANDYMAN_PLAN
4. HANDYMAN_J1_APPLIED_OR_SKIPPED
5. JANITOR_RESCAN
6. DIRECTOR_RECONCILIATION
7. PASS_OR_BLOCKED
8. CLOSED_OR_HELD

A J2 finding is not downgraded because implementation work can continue elsewhere.

The user granted operational Household clearance for WP01-WP10 on 2026-09-24. This authorizes progression through machine/governance gates, but does not fabricate external GitHub administration, API credentials, successful live service calls, or a Full Audit PASS.
