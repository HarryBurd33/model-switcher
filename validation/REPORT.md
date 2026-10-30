# Model Switcher validation history and current native evidence

The current 0.5.2 documentation correction reconciles the capability report with
the authorized native 0.5.1 follow-up recorded below. Historical build/test outcomes
remain scoped to their original revisions; they are not a current pending-approval
gate. No runtime behavior or native permission changes in this correction.

## Original 0.4.0 validation

2026-10-29. The current user requested automatic model and reasoning-effort switching
as a standing preference across their Codex chats, with a brief reason and verified
checkpoint/handoff resume, plus synchronization of the public repository.

The earlier global block requested routing but did not authorize automatic selection
or continuation. The updated installer exposes explicit `--automatic` and `--manual`
profile preferences. A loaded automatic instruction covers the authorized tasks in that
profile without repeated per-chat opt-in; fresh installs without that flag still grant
no automatic authority. Upgrades preserve the recorded mode. Secondary profiles need
their own explicit preference. Existing receipts, custom-file conflict protection,
unrelated instructions and primary/shared ownership remain intact.

**80 tests passed**, including eight new executed installer lifecycle cases and all
72 existing selection/transport/continuation/package regressions. The new cases exercise
saved automatic instructions, no-flag upgrades, manual downgrade, rollback to both
legacy policy and automatic preferences, separate profile consent, malformed options
before writes and customization refusal. This is executed local behavior, not proof
that every model follows an instruction in every chat.

Instructions now treat model-only and effort-only changes alike: verified handoff with
exact next action and acceptance check, current native selection/readback, one-use
continuation, and brief proposed/selected/scheduled/resumed status with a concrete reason.
Unchanged selections, trivial work, explicit model choices, stop/cancel, uncertain jobs
and unsupported hosts retain their existing boundaries. Global preference comes from
current human instructions, never from a checkpoint receipt. No installer schedule,
new daemon, account change, API spend or unrelated-chat message is introduced.

A fresh read-only existing-server proxy inspection succeeded in the actual current
chat and reported configured/latest-persisted Sol / High. The sandboxed probe was unable
to connect; the same supported read-only command succeeded with authorized local-server
access. No model change or new inference was part of that inspection. This does not
establish which model executed a particular turn. Live continuation was then observed: the origin completed, a distinct heartbeat turn
verified source/checkpoint/authority/resources, acquired the one-use claim, deleted its
exact schedule with confirmed retirement and received execute:true before publication
work. This establishes a real checkpoint-based resume, not per-turn inference telemetry.

Public release validation also includes independent contract review, installed file and
profile-block verification, deterministic ZIP/extracted rebuild, sanitized export and
remote CI/release checks. Exact final results are recorded in global-defaults-check.json
and global-defaults-review.md. Historical checks below keep their original scope.

---

# Model Switcher validation — 0.3.1

The first-use review identified a dependency gap in the earlier metadata inspector:
`app-server --stdio` starts a new server and may resolve persisted remote-control state.
The supported existing-daemon proxy avoids that startup, but requires WebSocket framing.
The current candidate adds bounded framing and refuses missing/incompatible transport
without starting a server or searching for another profile. The complete source suite passed **72 tests in 2.886 seconds**, including 24 active-chat
transport/selection cases. Independent Astra source review found no blocker. One real
proxy inspection completed successfully after a single authorized native selection;
the helper confirmed the exact same chat's latest-persisted GPT-6.1 Sol / Ultra setting.
No server start or configuration change was attempted. A prior guessed-path absence
was not evidence of daemon absence; the supported proxy resolved the actual endpoint.

Automatic continuation remains unverified until a distinct receiving turn claims once
and retires its schedule. The successful metadata readback is separate from that future
acceptance and does not prove the executing model of a turn.

---

# Model Switcher validation — 0.3.0

2026-10-27. Current requested extension is automatic same-chat continuation after an
explicitly authorized model transition. The helper reuses the existing checkpoint
store/lease and keeps one active intent plus immutable intent/spent/outcome receipts.
It never messages, schedules or invokes a model itself.

Thirty focused offline tests passed. They cover origin/receiving turn distinction,
wrong/stale/context/selection/resource/authority/lease/job evidence, expiry, cancellation,
concurrent claims and retirements, one executable emission, lost/uncertain results,
changed operation IDs, scheduler-retirement failure and cleanup under stop/revocation/
low quota. The complete source regression suite passed **61 tests in 2.426 seconds**, including
the original 31 selection/installer/package cases.
Independent Astra review found no blocking defect. Inputs remain cooperating operator
attestations rather than authentication or per-turn model telemetry.

Native end-to-end continuation has **not yet been observed**. A bounded first use is
planned in the human-authorized receiving chat after installation: configured selection,
recorded native heartbeat, completed origin, different receiving turn, one claim,
confirmed scheduler retirement, then the exact bounded continuation. Its real receipt
must be recorded separately; offline tests alone cannot certify that delivery or prove
which model executed a turn. No task continuation or new scheduler is implied by install.

Historical evidence below is preserved with its original scope. Private current task
state, identity/lease details, raw account observations and scheduler records are excluded
from public packaging. This candidate adds no paid API fallback or autonomous service.

---

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

## 0.5 bounded policy and compatibility

A pure live-catalog recommender covers hard/easy/specialist model and effort policy,
explicit choice/opt-out, Ultra delegation, supported-effort and overhead boundaries.
Current 0.8 checkpoint commands replace retired review/planner requirements. Defaults
are policy guidance, not benchmarks proving universal best-model performance.

Existing native continuation guards remained unchanged. The original 0.5 repair case encountered
automatic approval rejection of a recurring heartbeat before registration/selection;
the local intent was cancelled after registry absence was confirmed. Live verification
was pending at that time. Later authorized observations below supersede that status
without changing the historical rejected outcome or claiming a workaround.

Offline 0.5 validation: 95 package/installer/native-guard/policy tests passed,
including 15 behavioral routing cases. Three disposable Git fixtures saved and
verified Sol Medium, Astra Extra High and Luna Low assignments through actual
task-checkpoint 0.8.3 without a worker planner or recovery review. No model inference
was invoked by those fixtures. Those offline checks are separate from the later native
handoff observations below; neither exposes per-turn inference telemetry.


## Authorized native follow-up — 2026-10-29

The earlier 0.5 pending-approval result above is historical. The human subsequently
authorized temporary one-use native handoff schedules across projects. One real
same-chat test passed with a verified source-bound checkpoint, exact Sol Medium
configured readback, completed origin and a distinct receiving turn. The receiver
claimed the intent once, deleted its exact native heartbeat, received the guard
execution permit and ran bounded read-only verification. It completed the operation,
saved and verified a final checkpoint, then released only its own lease.

All 16 installed skill files matched the published 0.5.0 package; the release ZIP
checksum and recorded main/tag CI passed. Both profiles retained guidance, config,
hooks and modes except for the explicit scheduling permission addition. Only the
test chat changed effort; 39 other inspected selections were unchanged. Fresh
account allowance was 45% remaining. No paid inference or domain implementation
was invoked. Configured host metadata is not per-turn execution telemetry.

Three immediate COUNT=1 rule variants failed validation before creation. A finite
COUNT=3 minute rule was accepted, delivered once and was deleted before work.
This confirms at-most-once admission for that observed handoff, not guaranteed
delivery or future behavior in every chat. Cross-chat readiness and native
automatic delivery remain separate acceptance claims.

Cross-project follow-up independently verified configured model/effort readback in
13 other owning chats through the supported existing-daemon proxy with permitted
local socket access. Initial sandboxed readbacks in several chats failed before a
reply. The permitted probe succeeded without a server start, model/config change
or task write. This is a host-access diagnostic, not evidence of failed native
continuation, and does not prove automatic delivery in those chats.

## Protected readback and same-chat follow-up — 0.5.1

On 2026-10-29 the human explicitly authorized an EPERM readback repair and a bounded
native switching/resume check in the affected desktop chat. The ordinary sandbox
probe failed on protected socket access; a normally approved read-only probe against
the existing daemon succeeded without a permission/profile change or fallback server.
The diagnostic was made precise and secret-safe; optional fixed model/list supplies
the live model/effort catalog.

Host readback confirmed Astra / Extra High as latest-persisted configuration. A
distinct native receiver confirmed the origin completed, verified matching ownership,
base/current checkpoint lineage, source/action/authority and fresh 43% allowance,
claimed once and deleted its exact finite native heartbeat. Only after confirmed
retirement returned execute:true did the receiver review/publish the candidate.
It completed the guard, restored original Sol / Extra High with readback, saved and
verified its final checkpoint, and normally released its own lease. One malformed
CLI store path was rejected before mutation; only one durable claim occurred.

101 source and 101 exported-package tests passed. Candidate/main/tag CI passed at
the published 0.5.1 revision. Downloaded release and immutable source matched all 45
public files; all 16 installed files matched. Existing 21 uid/gid/mode records and
eight protected records were unchanged. An initially detected activation-block
reorder was restored exactly and the installer/regression corrected before the final
tested installation. No paid API calls, foreign task changes or permission weakening.

This is actual configured-selection and distinct-turn admission evidence. Executing
model identity for the historical turn is unavailable; guaranteed future delivery,
universal activation, cross-device operation and cost/quality savings remain unproven.
Private chat/task identifiers, lease tokens and raw account/approval receipts remain
outside the public package. The 0.5.2 correction retains those limits and the original
101-test acceptance; it requires no repeat notification or native handoff experiment.
