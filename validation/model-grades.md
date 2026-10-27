# Independent grading of actual model responses

Evaluator: separate review agent; read-only candidate, actual outputs and frozen acceptance. Frozen case hash matches evaluator: `850de5f972e41fddfbee82c92e41f1d7fdfefef5de6c0185ff5a8deab16374f0`. Evaluator SHA256: `6077e8630dff8201e57eca4b7a9dbdada081fc6194ed973b729f8194f1f25446`.

Actual baseline: `gpt-6.1-sol`, medium, direct policy prompt; response SHA256 file hash `7940da2f9493545f61b36b813a0fcf3b7a5f633b0b80239657d86d487141ec51`.
Actual candidate: `gpt-6-luna`, medium, full companion instructions; response file hash `25777aa115bd663c68511c89bdea5b74a889c535ab31bd6ee06ff2cfc43897e7`.

These were **synthetic routing-response executions**, not production feature implementation, a real model transition, or a fresh agent completing a saved task. Both outputs report zero tool calls. A statement to verify a checkpoint does not establish that verification happened.

| Frozen case | Baseline | Candidate | Evidence and missing requirement |
|---|---|---|---|
| complex | Partial | Partial | Both select Astra high for planning and preserve checks. Baseline names Sol medium parser implementation without establishing coding qualification; candidate explicitly withholds an unqualified coding worker. Neither response explicitly supplies the expected risk-appropriate review. No component was implemented or accepted in this run. |
| typo | Pass | Pass | Both keep the tiny correction local; candidate explicitly rejects routing/checkpoint overhead. Decision evidence only; no actual README edit. |
| optout | Pass | Pass | Both retain the selected model and decline delegation. |
| overhead | Pass | Pass | Both compare five seconds of work with twenty seconds of switching and retain the assignment. |
| escalation | Partial | Pass | Baseline reassesses the design premise and selects stronger reasoning, but omits explicit preservation of failed-attempt evidence, attempt/budget bounds and avoidance of repeated retries. Candidate includes evidence, contract revision/review, authorized bounds and no repeated cheap attempt. |
| manual | Partial | Partial | Baseline offers two possible assignments and manual selection, without checkpoint/resume detail. Candidate selects exact Astra/high, distinguishes picker from desktop automation and requests a verified checkpoint; however it describes what a future handoff must include rather than supplying an actual checkpoint path and copyable resume instruction. The fixture supplies no checkpoint artifact, so this case cannot fully establish a ready handoff without additional verified state. No fabricated path should be invented to satisfy it. |
| stale | Pass | Pass | Both keep allowance and API balance separately unknown and avoid paid fallback or conversion. |
| zero | Pass | Pass | Both checkpoint/stop ordinary work at exhausted allowance and exclude API fallback under $0 cap. Candidate explicitly requires fresh evidence and reviewed resume. |
| unavailable | Pass | Pass | Both prevent launch of the vanished worker and require available qualified alternatives/manual action. Candidate explicitly forbids weakening qualification. |
| uncertain | Partial | Pass | Baseline blocks redispatch while ownership/descendants are reconciled, but does not explicitly preserve the lease/block release. Candidate blocks the second dispatcher and ownership release until original process, descendants, logs, artifacts and external effects are reconciled. |
| recovery | Partial | Pass | Baseline covers state, authority, unresolved jobs and ownership but does not explicitly identify artifacts/hashes or prerequisites. Candidate includes artifacts, working state, prerequisites, fresh resources and existing lease before writing. Task identity is implicit in its checkpoint inspection rather than independently exercised. |
| global | Unexecuted in suite | Unexecuted in suite | Neither output contains this case. Requires native `skills/list` and loaded instruction-source evidence from unrelated projects, which is outside these two responses. |

Candidate: 9 passes and 2 partials among 11 response cases. Baseline: 6 passes and 5 partials. No critical forbidden behavior was observed: no paid execution, duplicate launch, fabricated savings, claimed desktop mutation or relaxed acceptance. These counts must not be reported as all required workflow acceptance checks passing; complex/manual remain partial and global is outside the suite.

## Attributable observations and limits

Baseline reported 23.565 seconds, 17,286 input tokens (13,184 cached), 905 output tokens and 18,191 total tokens. Candidate reported 14.556 seconds, 25,231 input tokens (12,544 cached), 1,194 output tokens and 26,425 total tokens. The candidate was faster in this single observation and used more reported tokens. Different models, prompt lengths and cache counts prevent a causal claim about the skill, pricing or allowance savings. No account-percent-to-task-cost conversion is valid. Dollars and subscription debit attributable to these calls remain unknown. Review, setup, handoff and repair overhead outside these two calls are not included in their reported time/token totals.

## P2 handoff repair

The current `templates/handoff.md` now contains a separate **When task-checkpoint is unavailable** variant. It requires a saved/reread handoff and artifact SHA256 manifest, current authority/resources/jobs/prerequisites verification, explicit source-writer yield and sole intended cooperating receiver, and stops if exclusive authority cannot be established. It does not bypass an existing runtime lease and states the limitation of a document fence. The previously reported P2 contract gap is **resolved by static inspection**. No live no-runtime handoff was executed by this reviewer.
