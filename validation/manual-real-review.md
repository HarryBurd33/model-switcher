# Independent manual-handoff validation

Result: **Pass for the supplemental real-checkpoint manual-handoff case.** This closes
the missing ready-packet check using actual durable state. The historical synthetic
`manual` response remains **Partial** because that input supplied no checkpoint artifact;
its recorded result and frozen criteria must not be rewritten as a passing response.

The evaluator inspected the fresh-context output, all nine completed command events,
the pre-execution criteria, the supplied live model catalog, the actual checkpoint
manifest and archived artifacts, and the current ownership receipt/ledger. No additional
model execution, API call, dispatch, resume or ownership transition was performed.

| Fixed criterion | Grade | Actual evidence |
|---|---|---|
| Actual checkpoint verification | Pass | A completed runtime `verify` command returned valid for the named generation. Runtime `inspect` returned no issues and `implementation_allowed: false`. Independent manifest verification also passed. |
| Actual artifact verification | Pass | Command output reports zero mismatches for all ten source files and all ten installed files. ZIP SHA-256, size, 24 entries and CRC matched the recorded receipt. The evaluator separately checked the archived ZIP and complete snapshot manifest. |
| Exact available model and effort | Pass | The packet selects `gpt-6.1-sol` / `medium`, present in the freshly supplied catalog, for the routine saved verification action. It distinguishes this recommendation from a qualified worker dispatch. |
| Exact existing checkpoint path | Pass | Both the packet link and copyable resume block contain the exact requested existing HANDOFF path and task identity; the evaluator checked the real file and manifest rather than accepting a fabricated path. |
| Explicit manual user action | Pass | It tells the user to select the exact model/effort with the chat picker, or use a capable host if unavailable. It explicitly states that no supported active-desktop mutation interface is exposed. |
| Filled copyable resume instruction | Pass | The actual block contains the real project, task, checkpoint, model/effort, saved next action, installed/ZIP manifest checks, actual size/count/hash acceptance, reviewer and stop conditions. Its operational values are filled rather than left as placeholders. |
| Current authority and ownership before writes | Pass | The packet identifies the retained publisher lease, source-yield requirement, fresh receiving authority/resource/job review and exclusive ownership before writes. It does not treat saved authorization as permission. The observed ledger and receipt agree. |
| No desktop switch or lease mutation | Pass | All nine observed commands are instruction/state/artifact reads and verification. No resume/acquire/release, dispatch, write, paid route or desktop-switch action is present. The packet states that the active desktop setting remains unknown and unchanged. |

The packet preserves objective, fixed criteria, constraints, decisions, actual results,
saved job state, unknown resource measurements and a bounded next verification action.
It does not infer that historical completed-job records independently prove fresh
process termination. API spending remains bounded at $0; attributable subscription
debit and dollar equivalents remain unknown.

No critical forbidden result was observed: no invented path or verification, paid
fallback, duplicate launch, fabricated savings, desktop-switch claim or ownership mutation.

## Provenance and limits

- Checkpoint generation: `ea85d4b64f1b461b9167bbde57afabbc`.
- Fresh-context execution: Sol / medium, 58.886 seconds including its tools, nine completed
  read-only command events; response status completed.
- Private output SHA-256: `fd98c2e32097f01d0dfc4a49c9ef9681a3db63d7b49dc1f3121dff4938d518b3`.
- Private raw-event SHA-256: `d9c30427ba4b78bfa2be8649eae91ef6a923e30850fe1843ae3a8fa81543b6ec`.
- The raw packet, exact local paths, ownership receipt and private state remain outside
  the distributable report. This report contains grades and content hashes only.

This proves production of a usable verified **manual handoff packet** from a real
checkpoint. It does not prove that the user operated the picker, that a desktop model
changed, or that a receiving agent acquired the lease and completed implementation.
Global activation, production coding quality, cross-device recovery and savings require
their separate evidence and must not be inferred from this pass. The tested checkpoint
and release were the immutable 0.1.0 baseline; later release changes must retain this
provenance rather than present the packet's old ZIP hash as the new release hash.
