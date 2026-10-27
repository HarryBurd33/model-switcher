---
name: model-switcher
description: Route substantial multi-step work to suitable models and reasoning settings while conserving separate Codex allowance and API budgets. Use at task intake, expensive phases, handoff, scope changes, failed acceptance checks, or explicit $model-switcher. Keep trivial corrections lightweight; respect explicit model choices and routing opt-outs.
license: MIT
metadata:
  version: "0.1.1"
---

# Model switcher

Optimize resources through **verified completion**, including planning, context transfer,
validation, review, retries and repair. Quality and current authorization govern every
assignment. Savings are a hypothesis to measure, never a guarantee of minimum cost.

## Intake and boundaries

1. Respect project instructions, explicit model/effort choices, opt-outs, privacy,
   authorization, reserves and stop policies. For trivial work, do it directly without
   routing announcements, a planning phase or a new checkpoint. Explicit invocation
   permits a brief routing answer, not unnecessary orchestration.
2. For substantial work, inspect objective, deliverables, acceptance criteria, risk,
   ambiguity, dependencies, instructions, artifacts, tests and existing checkpoint/jobs.
   Read the installed `task-checkpoint` skill when available. Reuse its task identity,
   lease, `routing.work_packages`, journal and checkpoint store. Never initialize a
   second queue or database for the same task. [Runtime procedure](references/runtime.md).
3. Discover current tools, account restrictions, available models and supported
   efforts. Separate the effective current chat setting from a configured default.
   If the active setting cannot be inspected, mark it unknown. Catalog descriptions,
   current task-specific evidence and qualification determine suitability; a model
   name or list position alone does not establish strength or cost.
4. Use the strongest suitable available model for substantial planning and difficult
   decisions. If the current context cannot fill that role, use a verified supported
   worker route or give a ready manual handoff. A suitable specialist can beat a
   generally stronger model. An explicit user selection remains controlling; explain
   a consequential limitation and offer the appropriate recommendation.

Reconsider at task intake, before expensive phases, meaningful handoffs, material scope
changes and acceptance failures. Do not repeat unchanged routing analysis each tool
call. Keep the policy and next assignment in semantic checkpoint state on resumption.

## Assign bounded work

5. Establish the overall plan and consequential decisions first. Define each package's
   objective, dependencies, permitted files/actions, tools/capabilities/privacy,
   unchanged acceptance criteria, proposed model/effort with reason, attempt/time/API
   bounds, escalation condition and checkpoint boundary. Use the existing runtime's
   planned-task template, not a new schema. Changed contracts receive new IDs.
6. Choose the least expensive **qualified** assignment likely to meet those checks.
   Consider lower reasoning on the same model. Qualification must cover model, effort,
   task class, tools and privacy; a text-only result does not qualify coding. Treat
   price or relative-cost estimates as estimates, and unknown cost as unknown.
7. Compare expected useful completion cost including reconstruction, transfer,
   validation, review, retry and repair. Keep the current assignment if likely gains
   do not exceed overhead. Do not enforce a downward ladder. Use stronger review when
   consequences justify it; routine accepted work need not receive strongest review.
   In every consequential plan, explicitly name the review assignment and the acceptance
   gate before completion, including in a routing recommendation before execution.
8. Check fresh shared signals and approved router configuration immediately before a
   qualified dispatch. Review/attest the exact current plan, acceptance argv and scope
   when already authorized; a saved approval cannot grant new authority. Never weaken
   qualification or stops to force a route. If no qualified route exists, continue in
   a suitable authorized current context or prepare manual handoff.

## Preserve separate resources

Record subscription allowance, API dollars, token usage and context capacity separately,
with source, timestamp, units, scope and uncertainty. Missing, stale, future-dated or
unsupported observations remain unknown. Valid zero remains zero. Account percentages
are account-wide; do not turn them into task tokens, task costs or API dollars.

Honor existing reserves (including a configured 20% stop) and explicit stop events.
Save/verify and stop ordinary work at a resource boundary. Changing models or accounts
does not bypass that stop. Recovery needs fresh evidence and an explicit reviewed resume.
Unknown telemetry follows the configured manual/explicit-budget policy; never assume
recovered capacity. API execution requires an authorized provider **and an explicit
spending boundary**; subscription access never silently falls back to a paid API.

## Transition, validate, escalate

Before any model/worker/context transition, save and verify the existing checkpoint:
objective, constraints, criteria, decisions/reasons, completed work, artifact locations,
actual validation, unresolved issues, next bounded action/verification, recommended
model/effort/tools/reason, active jobs/uncertain effects, resource observations and current
authorization context. Transfer concise decisions and evidence, not private reasoning
transcripts. Use [the handoff template](templates/handoff.md) if durable runtime is absent;
label an unsaved emergency copy honestly and stop dependent execution.

Automate only through a verified interface. A separate selected-model worker, an owned
app-server thread override and a manual desktop model choice are different operations.
Changing configuration defaults or launching a CLI child does not switch the current
desktop chat. [Host capabilities and manual steps](references/host.md).

The receiver verifies intended task/project, artifact hashes and working state,
prerequisites/tools, current authority, resource sufficiency, every uncertain job and
exclusive ownership **before writing**. Interrupted/uncertain work blocks duplicate
execution and lease release until its actual outcome is reconciled. Never steal a lease.

Validate each result against the frozen acceptance checks; exit zero alone is insufficient.
On failure, preserve evidence, identify the faulty assumption or missing capability and
escalate within the authorized attempt/time/budget bounds. Revise material contracts and
re-review them; do not repeatedly retry or oscillate. If no qualified assignment remains,
prepare the handoff and state the real required user action. Continue to original task
completion unless a real authority, resource or capability boundary prevents progress.

## Record and communicate

Maintain assignments, evidence, accepted/rejected outcomes, retries and observed resource
use in the existing routing journal, with semantic explanations in task decisions/log
references. Proposed assignments are not executed assignments. Record unknown measurements
as null/unknown; include all orchestration overhead in comparisons.

Announce only a meaningful phase or transition: sufficient model/effort, why it is worth
the overhead, and whether the user must act. Manual handoffs must name an exact currently
available model and supported effort, verified checkpoint path, supported switching steps
and a copyable resume instruction. Claim completion only after original acceptance passes.

For setup, update, rollback and uninstall, see [README](README.md). For cases and evidence
limits, see [examples](references/examples.md) and [capability report](references/capabilities.md).
