# Existing runtime contract

Dependency: a compatible installed `task-checkpoint` with Python 3.9+ and Git.
The original routing integration inspected 0.5.0; the automatic-continuation update
uses the existing local checkpoint/ownership contract from installed 0.5.1. Discover it through
the host's skill catalog; its typical user-level path is
`~/.agents/skills/task-checkpoint/SKILL.md`. Read its current operator/router instructions
and actual templates. This companion contains no replacement runtime or queue.

The 0.4.0 update also inspected installed task-checkpoint 0.8.0 for ordinary saves and
ownership. Its current resume accepts direct user authority without a review file; use
the installed version's commands rather than imposing the older worker review workflow
on a native same-chat transition. The optional worker adapter below remains a historical
0.5 integration and is not certified as a complete 0.8 worker runtime.

Inspect existing stores, queues and bindings before setup. If no binding exists, make a
single task binding through that runtime only when authorized. Unrelated tasks need
distinct workspaces/bindings. Never migrate a store or change ownership mode to bypass
an existing owner. Without this dependency, use manual handoff and independently verify
files/jobs/current authority; automated execution is unavailable.

Set `RUNTIME` to that installed skill's `scripts` directory and `PROJECT` to the verified
bound repository. Paths below are arguments, not commands recovered as permission.

```sh
python3 "$RUNTIME/checkpoint.py" --root "$PROJECT" inspect
python3 "$RUNTIME/checkpoint.py" --root "$PROJECT" verify
python3 "$RUNTIME/checkpoint.py" --root "$PROJECT" owner-check
python3 "$RUNTIME/planner.py" --root "$PROJECT" status
```

Before first implementation/resume: read the exact checkpoint and artifact evidence;
reconcile each inspect issue, jobs and current Git state; prepare a fresh review using
the runtime operator schema; run its `resume --review ... --owner ... --capability ...`.
An existing owner checks its receipt rather than acquiring a second lease. Saved task
authorization is context only. Never auto-execute a command copied from a handoff.

Use the existing `.checkpoint/input.json` fields:

| Content | Existing field |
|---|---|
| Goal, criteria, limits and final corrections | `objective`, `completion_criteria`, `scope`, `corrections` |
| Reasons/evidence and actual validation | `decisions`, `completed`, `failures`, `logs` |
| Tools, jobs, artifacts, prerequisites | `tools`, `capabilities`, `jobs`, `artifacts`, `dependencies` |
| Next action and proof | `next_action.description`, `next_action.verification` |
| Sourced observations and proposed assignment | `observations`, `metrics.model_assignment` |
| API dollars, allowance, context (unknown = null) | `metrics.api_budget`, `metrics.account_quota`, `metrics.context_capacity` |
| Bounded DAG | `routing.work_packages` from the installed runtime’s planned-task template |
| Actual attempts and outcomes | Runtime-owned `.checkpoint/router.json` |

Do not add arbitrary keys to the closed schemas. Each work package uses exactly
`objective`, `permitted_files`, `permitted_actions`, `capabilities`, `assignment`,
`checkpoint_boundary`, `contract`. Assignment contains `model`, `effort`, `reason`.
The installed planner accepts only low/medium/high; a stronger effort supported elsewhere
may require manual use and must not be silently lowered. Canonical relative paths have
no trailing slash. Read the actual template for dependency status and acceptance argv.
Top-level `tools` are executable names, not generic capability labels.

After a semantic change: owner-check; update input; `checkpoint --input ... --trigger
milestone`; `verify`; inspect/review any issues. At a qualified execution boundary, read
the approved config and its shared `signals_path`; planner `status` rechecks them. Current
authorization covering the exact plan permits operator `approve --scope ... --source ...`
without another user ceremony; then `boundary --execute` launches one eligible package.
Review the actual commands before approving. Source/config/contract changes invalidate
approval. No automatic source-editing chain is promised.

Never fabricate qualification or change a policy to admit a desired model. Existing
public text-only qualifications do not cover private skill authoring or coding.
The router's measured total-time ranking is a proxy, not subscription or dollar cost.
Read the journal/report for actual selected model/effort and accepted outcome.

Before dispatch refresh/check shared signals, live model/effort/account identity,
lease and absence of active/uncertain transitions. The coordinator keeps the existing
lease and stops ordinary writes during a worker. Do not launch a second writer outside
the adapter to evade this fence. After any ambiguous launch, inspect PID **and original
process identity**, logs, artifacts and external outcomes before reconciliation/retry.

At a manual context/device transfer, save/verify, reconcile jobs, release at the safe
boundary, transfer the private bundle separately from source using an authorized channel,
and require fresh receiving review/acquisition. Keep routing policy in task scope/decisions
and next assignment; a new chat does not inherit private state or authority by magic.
