# CareerHub External Gates E01–E03 — Authorized Activation Record

**Authorization:** GRANTED by user on 2026-09-25  
**Purpose:** Clear the remaining external dependencies for the CareerHub 1.0 Silicon Sprint without reintroducing cross-repository write secrets.

## E01 — Private CareerHubZero Action access

**State:** BLOCKED_REPOSITORY_ADMIN_SETTING

User authorization is granted.

Verification reruns:
- Linus: workflow run `36052388116`, attempt 2 — failed at **Set up job**.
- Weronika: workflow run `36052385689`, attempt 2 — failed at **Set up job**.
- Grace: workflow run `36052392296`, attempt 2 — failed at **Set up job**.

No CareerHub code executed in those runs.

### Required repository-admin change

In GitHub:

1. Open `Motherpher/CareerHubZero`.
2. Open **Settings**.
3. Open **Actions → General**.
4. Under **Access**, select:
   **Accessible from repositories in the 'Motherpher' organization**.
5. Save.

After this setting is applied, rerun the three compatibility workflows.

This is the preferred architecture because GitHub supplies a scoped, short-lived token to the runner for private-action download; CareerHub does not need `CAREERHUB_STACK_TOKEN`.

---

## E02 — Google Maps Platform

**State:** BLOCKED_MISSING_GOOGLE_MAPS_SECRET

User authorization is granted.

Live probe:
- CareerHubZero workflow run `36079668823`
- result: `BLOCKED_MISSING_SECRET`
- missing secret: `GOOGLE_MAPS_API_KEY`

### Required provider/account change

Google Cloud project requirements:
- billing enabled,
- **Places API (New)** enabled,
- **Routes API** enabled,
- API key created,
- API key restricted to required APIs and appropriate application restrictions.

Then add the key to:

`Motherpher/CareerHubZero → Settings → Secrets and variables → Actions → New repository secret`

Name exactly:

`GOOGLE_MAPS_API_KEY`

Do not place the key in source files, issues, logs or chat.

Once present, the existing `CareerHub External Gates E02-E03` workflow performs:
- Places Text Search against Stockholm Centralstation and Uppsala Centralstation,
- Routes `computeRouteMatrix`,
- machine PASS only if both provider calls succeed.

---

## E03 — OpenAI semantic runtime

**State:** BLOCKED_CREDIT_BALANCE_EXHAUSTED

User authorization is granted.

Live probe:
- CareerHubZero workflow run `36079668823`
- model: `gpt-5.6-sol`
- OpenAI Responses API reached successfully,
- HTTP status: `429`
- error code: `credit_balance_exhausted`
- error type: `insufficient_quota`

This proves the existing `OPENAI_API_KEY` secret is wired and accepted far enough to reach the API. Creating another key will not resolve the current blocker.

### Required provider/account change

For the OpenAI API organization/project owning the existing key:
- add API credits or restore billing capacity,
- verify organization/project spend limits are not blocking usage.

Then rerun `CareerHub External Gates E02-E03`.

The workflow uses a minimal Responses API call and passes only after receiving `CAREERHUB_GATE_OK`.

---

## Clearance sequence after activation

```text
E01 PASS
  ↓
WP02 rerun
  ↓
WP03 parity / local-motor deletion

E02 PASS
  ↓
WP06 live geography clearance
  ↓
WP09 unified hub clearance

E03 PASS
  ↓
live HRDM + application proof
  ↓
WP10 Full Audit Lock inputs complete

then:
WP10 → Final Janitor → Director reconciliation → 1.0 audit decision
```

Authorization is not equivalent to PASS. Each external gate remains blocked until machine verification succeeds.
