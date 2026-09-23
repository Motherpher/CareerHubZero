# Market Response Layer

CareerHub distinguishes **candidate evidence** from **market response**.

A profiled instance may expose multiple positioning surfaces. Those surfaces can change signal order and framing, but they may not change the underlying candidate evidence.

## Response ledger
A response event may record opportunity/job ID, application ID, search lane, positioning surface, inbound/outbound direction, response stage, date/time, source and notes.

The response layer exists to answer: **what does the market actually respond to?**

It must not turn a small sample into a deterministic candidate ranking. Report counts, conversion and sample size.

## Funnel
Recommended stages:

exposed → interested → contacted → qualified_contact → interview → case/test → references → offer/assignment

Negative and terminal states such as denied, withdrawn, archived and no_response remain explicit.

## Separation rule
- HRDM evaluates a role and positions a candidate using supplied evidence.
- Market response records what happened afterwards.
- Market response may guide future search strategy, but it may never rewrite past evidence.
