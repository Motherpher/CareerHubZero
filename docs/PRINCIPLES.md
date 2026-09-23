# Development Principles

## 1. Capability and context stay separate
Central code is reusable. Personal profile and application state stay in the profiled instance.

## 2. No invented candidate evidence
Unknown means unknown.

## 3. Human-facing simplicity
The visible journey is:

**Find → Analyse? → Apply**

Complexity belongs behind the interface.

## 4. Evidence before persuasion
Application drafting follows the evidence and HRDM analysis. The system must not manufacture stronger claims because they would sound better.

## 5. HRDM remains explicit
HRDM-R is a canonical analytical sequence, not a vague prompt label.

## 6. State is durable
Jobs should not disappear merely because the latest sourcing run changes.

## 7. Development must not break live instances
Central changes are versioned, validated and tested before profiled instances adopt them.

## 8. Secrets are infrastructure, not content
API keys, phone numbers, notification credentials and other secrets must never be committed to source control.

## 9. Privacy is structural
The central repository must be safe to inspect without revealing any profiled user's private career data.

## 10. Repository independence
Central code must not hard-code a specific GitHub owner/repository.
