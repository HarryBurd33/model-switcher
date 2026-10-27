# Model Switcher validation — 0.2.0

## Native same-chat model selection

The supported Codex app messaging tool accepted two self-targeted model/effort overrides
in the actual active chat. Read-only app-server metadata for that exact identity first
reported **gpt-6-luna / medium**, then **gpt-6.1-sol / medium** after the second request.
The matching identity and differing states provide observed selection-change evidence,
without picker automation, default edits, another worker or a new conversation.

The original turn remained in progress and configuration cues arrived as steering input.
This establishes configured/latest-persisted **selection for subsequent turns**, not a
changed model executing the current inference, a new turn or automatic continuation.
The schema itself labels thread model/effort as configuration rather than per-turn
telemetry. Separate readback connections reported notLoaded/latest-persisted state.
Computer use denied access to Codex; that route was not bypassed. A shared-daemon proxy
read probe timed out and is not the implemented mutation or verification route.

The new standard-library helper plans guarded native arguments and performs read-only
inspection/verification. It never calls messaging or starts/resumes inference itself.
Thirteen new deterministic tests cover wrong chat/host, missing authority, stale/future
observations, low/unknown resources, unavailable/ambiguous model or effort, pending
duplicates, unchanged selection, prompt-safe IDs, readback mismatches, no execution
claims, a read-only protocol and process cleanup. The original 16 installer/profile and
two package tests remain regressions. Real helper inspect/plan/verify was also exercised
on this current chat with fresh catalog and resource observations, without another cue.

See active-chat-check.json and active-chat-review.md for sanitized evidence and independent
review. Native cues require current human authority for this same chat, durable intent
and the existing task lease, live catalog/resource checks and exact host readback.
Context booleans are operator attestations, not authentication or restored permissions.
The helper alone does not fence concurrent writers. Unknown or ambiguous outcomes block
reposting until reconciled. No paid API route, worker, hidden IPC or new service was used.

Other hosts without the native tool/readback keep manual fallback. No production-quality,
savings, universal activation, mid-turn inference or automatic-follow-up execution claim
follows from this configuration test. Private chat IDs, messages and current task state
are excluded from exports. Historical results below retain their original scope.

---

# Model Switcher validation — 0.1.1

The missing ready-handoff capability check is **resolved by an executed real-checkpoint
test**, independently graded against all eight frozen criteria. The historical synthetic
manual result remains partial; it was not rewritten or relabelled as a pass.

## Real manual handoff

A fresh Sol/medium model context received the actual immutable 0.1.0 release checkpoint,
a live model catalog and read-only authority. It used nine tools and took 58.886 seconds.
Independent review inspected commands, checkpoint manifest, archived ZIP, installed hashes
and ownership. All eight fixed checks passed:

1. Actually run checkpoint verification and inspect state.
2. Actually check relevant artifact, installed-file and ZIP hashes.
3. Recommend an exact available model/effort suited to the next action.
4. Supply the exact existing verified HANDOFF path.
5. Give supported picker steps and identify required user action.
6. Return a filled copyable resume instruction with real task/path/action/check values.
7. Require current authority/resources, job reconciliation and ownership before writes.
8. Avoid desktop-switch claims, lease mutation, new dispatch and paid execution.

The packet selects Sol/medium for routine verification, observes the publisher's lease,
and requires safe yielding plus fresh receiving review. [Public evidence](manual-real-check.json)
and [independent grade](manual-real-review.md) retain results and hashes. User paths,
checkpoint content, account state and raw transcripts remain private. This test applies
to the immutable original artifacts; new 0.1.1 bytes receive separate release checks.
No picker action, desktop switch, lease transfer or receiving implementation occurred.

## Historical evidence

| Check | Observed result | Type |
|---|---|---|
| Synthetic routing suite | Baseline 6 pass / 5 partial; v1 9 / 2; v2 10 / 1 | Actual response comparison |
| Synthetic manual case | Partial: no checkpoint artifact was supplied | Retained history, supplemented above |
| Substantial activation | Untagged request read installed skill; no writes/delegation | Native model/tool events |
| Trivial correction | Only `the sky is blue`; zero tools | Native model/tool events |
| Fresh-context audit | Ran verify/inspect/owner-check; detected stale state and withheld implementation | Native read-only audit |
| Global discovery | Enabled skill and global instructions loaded in two unrelated repositories | Native skills/list and thread/start |
| Resource/qualification/recovery safeguards | 106 dependency-source tests passed | Deterministic fixtures |

Frozen cases/evaluator and previous grades remain in `cases.json`, `evaluator.json`,
`model-grades.md` and `model-grades-v2.md`. The implicit response exceeded a separate
220-word evaluation request (256 words including commentary): activation passed; that
presentation constraint did not. No critical forbidden behavior was observed.

The 106 dependency-source tests comprise policy 23, router runtime 20, checkpoint 18,
automation/planner 28 and profile/local-worker 17. Core installed checkpoint/router/planner/
router-policy/telemetry files match that source. Two of 28 dependency files differ (the
account collector and its reference), so these tests do not certify the whole installed
collector or native service. No dependency code was copied or modified. A timeout fixture
emitted a ResourceWarning while passing; it does not prove production descendant cancellation.

The original build used six bounded subscription turns. This requested follow-up used
one additional read-only turn capped at 180 seconds in a separate validation phase, with
no paid API route. It did not silently extend the earlier six-turn evaluation or add a
production/savings benchmark.

## Release and installation

- **16 installer tests** cover the original nine lifecycle checks and seven extra-profile
  activation checks: shared-target preservation, idempotence, status, changed block and
  symlink refusal, text preservation and deactivation after primary removal.
- **Two package tests** verify deterministic ZIP bytes, exact public file map/CRC,
  exclusion of private state/logs and refusal to overwrite a nonempty export.
- Standalone build validation checks discovery metadata, relative links, implicit metadata
  and matching root/skill MIT notices without needing Skill Forge.
- Native discovery/global-source checks are repeated after installation for both configured
  local profiles in unrelated repositories; see `native-checks.json`.
- ZIPs are built twice and tested after extraction. Public source uses a fresh sanitized
  export and history, excluding the private checkpoint and local build Git history.

The CI workflow runs installer/package tests and a deterministic build. It makes no model,
account or billing calls and schedules no work. Repository Actions status is evidence for
each commit; merely having a workflow file does not prove a hosted pass.

## Limits and accounting

Public installation supplies the policy, global instructions and manual handoff mode.
Automatic selected-model workers need a compatible external task-checkpoint runtime with
current authority, leases, qualification and signals. That private runtime is not bundled
or made public by this repository.

Global instructions request use for substantial work. The tested host loaded them and
one untagged substantial request consumed the skill. Invocation still depends on host
loading, overrides, opt-outs, explicit choices and model behavior. No continuously running
service, active-desktop mutation, universal invocation, cross-device implementation or
production coding benchmark is claimed. No-runtime recovery is statically reviewed.

The real manual case reported 264,129 cumulative tokens including 229,504 cached input
tokens. Those are observations, not remaining context, dollars or subscription debit.
Parent/helper/review/startup/setup/packaging usage is not fully attributable, so total
workflow cost and savings remain unknown. Prior observations remain in
`live-observations.json`. Account percentages are never converted to task tokens or API
dollars. No minimum-cost or general quality guarantee is made.
