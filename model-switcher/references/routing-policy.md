# Bounded model and effort assignments

Use current human scope, risk, uncertainty, tools, acceptance and a fresh host catalog.
Classify a package from actual work; model names alone are not capability evidence.
These are conservative defaults, not a measured global price or quality ranking.

| Bounded work | Starting assignment | Escalation/review |
| --- | --- | --- |
| Simple extraction, checks or routine text | GPT-6 Luna Low/Medium | Sol if its tools/quality are needed |
| Well-scoped code or integration | GPT-6.1 Sol Medium | Sol High or Astra for harder review |
| Visual/document/computer-use work with clear scope | GPT-6.1 Terra Medium | Stronger model when ambiguity or risk requires it |
| Difficult diagnosis, architecture, conflicting evidence, high-risk review | Astra Extra High | Max for hardest serial reasoning |
| Hard work with independent parts and permitted delegation | Astra Ultra when supported | Retain one controlled writer and bounded acceptance |

Preserve explicit model/effort choices and opt-outs. A single trivial task can stay on
the current model when switching overhead would exceed the benefit. Reassess after
failed acceptance or a meaningful scope/phase change. Do not remain on an expensive
assignment by inertia once a substantial next package is safely bounded.

Ultra includes automatic delegation. Require both actual separable parts and current
delegation permission, plus catalog support. Serial workflows use Extra High/Max;
do not bypass a no-worker instruction. Unsupported preferred assignments produce an
honest supported fallback or ready manual handoff, never invented availability.

## Pure recommendation helper

Run scripts/routing_policy.py --input INPUT.json from the skill folder. Its input is:

- catalog: observed_at (timezone-aware, at most 120 seconds old), data from model/list.
  Each entry has model and supportedReasoningEfforts, or normalized efforts.
- task: kind (routine/coding/visual/analysis), difficulty (simple/bounded/hard/hardest),
  risk (low/high), objective, next_action, verification, permitted_files and
  permitted_actions. All scope/action/verification data comes from the current task.
  Optional failed_checks, trivial, independent_parts and delegation_allowed qualify
  escalation and orchestration.
- current_selection: observed model and effort; optional explicit_selection overrides
  one or both. routing_opt_out preserves the current assignment.
- stopped, provider_denied and at_limit represent ACTUAL independent controls. Under
  task-checkpoint 0.8, retired quota-stop files and unknown readings are not such stops.
  A selected exhaustion override ignores the numeric reserve; actual provider denial
  still controls. Determine at_limit with the installed runtime, not a new budget policy.

The helper only returns a recommendation, stronger review assignment and complete
handoff data. It performs no inference, messaging, scheduling, ownership or task writes.
execution_authorized is always false. Preserve the exact bounded goal, scope and
acceptance; save its assignment in the existing semantic metrics.model_assignment or
existing work-package contract. It is not a new queue or qualification certificate.

## Apply a meaningful transition

Before a model-only or effort-only change, save and verify the current checkpoint and
its complete next action, acceptance, selected model/effort and switching reason.
Use the current task-checkpoint contract and existing lease. Verify live catalog,
resources, instructions, jobs and host readback. Continue only in a distinct receiving
turn through the existing guarded one-use procedure. Selection is not mid-turn inference.

If a scheduler request is rejected by the host or automatic approval review, preserve
the rejection and verified handoff, cancel only an unarmed local intent after confirming
no scheduler exists, and request the missing approval. Do not replace it with an
indirect trigger, repeated message or another scheduler. Continue unrelated qualified
current-context work only within its existing authority; do not claim a new model ran.

Official guidance: [Codex models](https://learn.chatgpt.com/docs/models) and
[model selection](https://developers.openai.com/api/docs/guides/model-selection).
The live account catalog controls exact IDs and supported efforts.
