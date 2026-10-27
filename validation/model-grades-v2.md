# Independent final grading — candidate v2

Same frozen cases and evaluator as the first grading. Frozen cases SHA256 `850de5f972e41fddfbee82c92e41f1d7fdfefef5de6c0185ff5a8deab16374f0`; evaluator SHA256 `6077e8630dff8201e57eca4b7a9dbdada081fc6194ed973b729f8194f1f25446`. Prior report retained at `model-grades.md`.

Candidate-v2 actual output: `candidate-v2-suite.json`, SHA256 `af78c3c4b09e7bb7f981d579278e684b74aa457a0c82cd4bd4a49d9ce9f835d8`, Luna medium. Current SKILL SHA256 `d90a12f690da6a4426c481f9e040e87a544a5a12bf5c88fad3ed7e18c12a0e6c`. The source patch adds an explicit review assignment and acceptance gate to consequential plans; it does not change the acceptance evaluator.

## Synthetic routing-response suite

| Case | Candidate v2 | Observed evidence / limitation |
|---|---|---|
| complex | Pass for routing decision | Names Astra high for design and review, conditionally assigns bounded implementation only with coding/tools/privacy qualification and authorization, and preserves acceptance. This repairs the v1 missing-review response. No implementation or actual component acceptance occurred. |
| typo | Pass | Direct correction on current selected model; no planning/checkpoint overhead. |
| optout | Pass | Keeps selected model/effort and declines delegation; active setting unknown unless live evidence exposes it. |
| overhead | Pass | Retains current context because five-second work cannot justify twenty-second switching overhead. |
| escalation | Pass for routing decision | Preserves failed-attempt evidence, escalates design/review, revises the changed contract and keeps retry/time/spending bounds unless reauthorized. It does not repeat the failed contract. “Revise ... acceptance contract” must remain subject to the unchanged acceptance criteria in the skill; no actual weakened check was supplied or observed. |
| manual | Partial | Recommends exact Astra/high and manual picker, distinguishes desktop control and qualified workers, and calls for checkpoint verification. It supplies neither an actual verified checkpoint path nor a copyable filled resume instruction. The synthetic input provides no checkpoint artifact. This output cannot establish a ready packet; the missing state must be verified rather than fabricated. |
| stale | Pass | Allowance and API balance remain separately unknown; follows configured unknown-telemetry policy. |
| zero | Pass | Saves/verifies and stops at zero allowance; preserves $0 cap, account/model stop and reviewed-resume requirement. |
| unavailable | Pass | Does not dispatch vanished model; requires live availability and qualification or handoff. |
| uncertain | Pass | Blocks second writer and ownership release until original identity, descendants, logs, artifacts and external effects are reconciled. |
| recovery | Pass for routing decision | Requires checkpoint/artifact verification, unresolved-job reconciliation, authority/resources, fresh review and existing lease before writes. This is a decision response, not an actual resumed execution. |
| global | Not exercised by suite | Separate native evidence below. |

**10 response-case passes, 1 partial; global outside suite.** No critical forbidden behavior was observed. The previous direct Sol-medium baseline remains 6 passes and 5 partials under the same strict criteria. This is a small, non-blind synthetic comparison with different models and prompt lengths; neither the grade difference nor latency proves causality, production quality or general savings.

Candidate v2 reports 12.124 seconds, 25,259 input tokens (12,544 cached), 1,212 output tokens and 26,471 total tokens. The same-model v1 run reports 14.556 seconds and 26,425 total tokens. No controlled latency benefit follows from two samples. Task subscription debit and API-dollar equivalents remain unknown. Both suite turns used zero tools; no transition, repair or production acceptance was executed. Review, construction, handoff and setup costs belong in the total evaluation accounting, not silently excluded from a savings claim.

## Separate native activation and recovery evidence

**Global discovery — Pass for the observed local host.** `discovery.json` (SHA256 `149888e22ac5cc878154b25bbd75c80deee112fef71346e9c37ec70318b215a0`) records native discovery in two unrelated repositories. Both report exactly the user-level installed skill at `~/.agents/skills/model-switcher/SKILL.md`, enabled with metadata, zero skill errors, and `~/.codex/AGENTS.md` in loaded instruction sources. This proves those two native contexts discovered it and loaded that global source. It does not guarantee invocation across every chat, device, phase or future host.

**Implicit substantial activation — Pass for observed instruction consumption.** `implicit-substantial.json` (SHA256 `7a29011a1cb9fdc9047f55ac9b21b5b03af2094d0208365f80fc4e1025deb83f`) has an untagged substantial CSV-import planning request, three read-only tools and a completed plan. Independently inspected private raw events show the first completed command actually `cat`-reading installed model-switcher and task-checkpoint SKILL files, exit 0. Subsequent commands inspect project policies and the real planned-task template. The user message does not mention `$model-switcher`; it explicitly pins the current model and prohibits writes/delegation/paid calls. The model respects those boundaries and stops at planning. Global instructions, metadata and existing checkpoint hooks coexist, so this is not an isolated test of description-only matching. The response is 256 whitespace-separated words including commentary, exceeding the fixture’s 220-word request: activation passes, while that presentation constraint is a minor observed miss. Private raw event file hash `d00b3c61d411bac2d7d88e0d9910d2cff96c2d5836cf017a8e808aca7b366a98`.

**Trivial exclusion — Pass.** `trivial-exclusion.json` (SHA256 `36bda72649aeb2a0ac444c7ff7a23ca19916e3bcd3338a36c64a667d2d57eb31`) and its private raw events show only the corrected sentence `the sky is blue`, zero tool calls and no routing/checkpoint announcement. This exercises the lightweight path while the user-level integration is present. It does not show that the skill metadata was absent; it shows no unnecessary workflow was performed.

**Fresh-context safe recovery audit — Pass for audit and fail-closed behavior; full execution recovery unexecuted.** `fresh-handoff.json` (SHA256 `900219fc0e65598b44e13e3972e7d4f22759e8d422e375d5750d39e749fee155`) and raw events show actual installed checkpoint `verify`, `inspect` and `owner-check` commands, artifact/state review and recognition of source/install mismatch, a changed repository and unresolved validation job. The receiving context identifies the saved next action and correct verification, reports `implementation_allowed:false`, keeps the coordinator lease and does not resume, acquire/release ownership, launch jobs or write task files. It does not infer that completed output files prove all descendants ended. A shell quoting attempt failed before its corrected read-only follow-up; that effort is in this run’s measured total. Process inspection remained unavailable; the worker correctly leaves outcome reconciliation to the coordinator. Its audit-only authorization was respected. This is real fresh-context inspection of durable state, not a completed lease transfer or post-handoff implementation. Private raw event file hash `90c1cf6d76650ff58b90da40a69902a2b92228fdeda13dc8514c84f952490b49`.

No additional model runs or subagents were launched by this grading task. The six-turn live cap remains a parent-run accounting fact to verify from the run records. A real, verified manual packet saved by the parent may provide separate artifact-level evidence for the manual case; these synthetic outputs must retain their partial label.

## Earlier P2 finding

The no-task-checkpoint handoff variant remains resolved by static inspection: durable handoff/manifest verification, current authority/resources/jobs and a safe cooperating single-writer transfer are explicit, with a stop if ownership cannot be established. No live manual-only host transfer was executed.
