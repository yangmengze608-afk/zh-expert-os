# Gate-based Expert Governance

## Why

Zh Expert OS should spend expert-review time where judgment can change the product, not on every implementation milestone.

Core rule:

> Expert review is triggered by decision risk and product maturity, not implementation cadence.

## Preflight

Before spawning Experts, produce:

```text
EXPERT_REVIEW_DECISION
Decision: INVOKE | SKIP
Gate: DIRECTION | PROTOTYPE | RELEASE | CRITICAL_RISK | NONE
Reason: ...
Decision reversibility: LOW | MEDIUM | HIGH
Expected rework cost: LOW | MEDIUM | HIGH
External impact: LOW | MEDIUM | HIGH
Security/legal risk: NONE | LOW | HIGH
Product maturity: IDEA | BUILDING | PROTOTYPE | RELEASE_CANDIDATE
```

Default is `SKIP`.

## Gates

### DIRECTION

Use for product positioning, core architecture, major dependency choices, build-vs-buy, or pivot decisions where a wrong choice causes meaningful rework.

### PROTOTYPE

Use after the core user loop actually works. Review real artifacts: runnable prototype, real output, tests, known limitations, and relevant diffs. Do not review an abstract idea as if it were a finished product.

### RELEASE

Use before public GitHub release, competition submission, external demo, production beta, funding/application claim, or other external commitment.

### CRITICAL_RISK

May trigger at any time for security, privacy, licensing, data loss, dangerous execution, destructive migration, or other irreversible/high-consequence behavior.

## Default skip cases

Do not invoke an Expert Team for ordinary bug fixes, unit tests, fixtures, lint/typecheck, naming, docs wording, small schema changes, internal refactors, or incremental parser support unless they introduce a Gate-level risk.

## Minimal sufficient review team

Default per Gate:

1. one domain Expert;
2. either Auditor **or** Red Team.

Run both Auditor and Red Team only when the risk genuinely spans both evidence integrity and adversarial failure modes.

## Review Packet

Give each reviewer only the smallest sufficient packet:

- decision/question;
- relevant artifact or diff;
- test results;
- known risks and unknowns;
- prior relevant decisions.

Do not make every reviewer reread the full repository by default.

## Stop conditions

- No P0/P1: close the Gate.
- P2 only: record and continue; no re-review.
- P0/P1 fixed: allow one targeted re-review of the blockers.
- Same core artifact/commit: do not rerun the same Gate without new critical evidence or explicit human request.

## Human override

If the user explicitly asks for expert review, invoke the most appropriate Gate, but still use the minimal sufficient team instead of automatically starting a full committee.

## Example: Guose

Wrong:

```text
Phase A -> Expert
Phase B -> Expert
Phase C -> Auditor
Phase D -> Red Team
```

Right:

```text
Choose migration-engine direction -> DIRECTION_GATE
Normal implementation -> SKIP
Core repo -> recover -> plan -> patch -> verify loop works -> PROTOTYPE_GATE
Ready for public OSS release / Codex application -> RELEASE_GATE
Untrusted code execution question -> CRITICAL_RISK_GATE
```

The point is not fewer reviews at all costs. The point is higher-value reviews at the moments where review can materially change the outcome.
