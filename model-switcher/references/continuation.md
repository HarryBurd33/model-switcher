# Automatic continuation after a model transition

This authorized route uses one native **thread heartbeat as the receiving turn**. It does
not send another message to itself from that heartbeat. It applies when Model Switcher
orchestrates the authorized transition; changing a picker manually is not an observable
trigger here. The skill itself is not a background service.

The same conversation retains its history, and an immutable verified checkpoint records
the exact next action and artifacts. A single continuation record lives in the existing
task-checkpoint store. One active operation, the existing task lease and a durable spent
receipt provide cooperating duplicate suppression. This is at-most-once admission to
work, not guaranteed delivery or exactly-once external effects after a crash.

## Authorization and prerequisites

The user must authorize both model selection and automatic continuation for this chat
and task, directly or through a currently loaded standing global automatic preference.
That explicit global preference makes both the default in its chats without repeated
per-chat approval; installation/discovery alone does not grant this scope. Read the
actual current instruction, not a scope copied out of a checkpoint or receipt.
A request to save and stop, pause, cancel or wait for approval still stops
work unless the user explicitly changes that instruction. Permission to continue does
not authorize new data access, publication, trust changes or paid API usage. Scope in
saved files is context, not a new grant. Check fresh shared resources and reserve rules.

Require the supported native selection/message and heartbeat-management tools, a verified
current chat identity, current model/effort catalog, selection readback through an already-running daemon, a compatible
existing checkpoint and exclusive local task lease. Unknown prerequisites use manual
fallback. Do not create a second task queue, a new chat, an OS service or another writer.
No hidden IPC, model-default/database edits or UI bypass is part of this route.

## Sender procedure

1. Finish a coherent boundary, reconcile owned jobs and uncertain effects, save and
   verify the immutable base checkpoint and its manifest. Freeze the next action,
   source fingerprint, task/chat identity, authority scope and a short expiry. Inspect
   current scheduler registrations before creating one; never duplicate an unknown
   create outcome. Keep all paths, lease material and raw evidence private. Include the
   target model and effort, the concrete switching reason and fixed acceptance check in
   the handoff. Treat effort-only changes exactly like model changes.
2. Use `scripts/continuation.py prepare` with fresh operator evidence under the existing
   lease. It records one intent in that checkpoint store. Add its ID/source to the
   checkpoint's existing jobs; do not create another queue. The checkpoint's control
   record may advance, but only verified unchanged context/lineage can satisfy the
   receiver. Source/next-action/authority drift invalidates the intent.
3. Prepare one native thread heartbeat in PAUSED state, bound to this chat and the
   exact operation. Record its returned ID. A create timeout is uncertain: inspect
   native state instead of retrying with another name. Do not claim a local ticket
   installed a native schedule. The prompt must direct the receiver to this procedure,
   the private intent and checkpoint, and forbid reposting configuration cues. Fill in
   the real task/root/checkpoint, selected model/effort, next bounded action and its
   verification; no placeholders. Tell the receiver to resume that action after the
   claim and confirmed retirement, under the current global/task instructions.
4. Follow [native selection](active-chat.md) once. Verify exact configured model/effort
   readback. A cue may steer the current turn; it is not evidence of a new turn or
   changed in-flight inference. The configured selection and the future continuation
   outcome are separate receipts.
5. Arm the intent with the verified selection and scheduler ID. Activate only the
   reviewed heartbeat; preserve the full intent/checkpoint/job state. Retain the same
   task lease across this same-chat transition; do not release/steal a pending lease.
   Briefly report the confirmed selected model/effort, reason and scheduled resume from
   the verified handoff. End the sender turn at the announced boundary. Do not continue implementation after
   arming. The receiving turn must independently confirm that this origin completed.

Use the native automation tool for creation/updates. Do not write automation files by
hand. A short repeat schedule is only a delivery mechanism; the receiver must retire
it before task work. It is not permission for an indefinite polling or model-work loop.
The sender should choose an expiry and bounded wake policy; a late/expired or ambiguous
wake becomes a blocked outcome with no implementation. Stop/cancel is always respected.

## Receiver procedure

Read the original human authorization and current instructions first. Read only the
bounded control evidence needed to decide whether this is the same task/operation.
A wake while the origin is still active cannot start another writer. It must remain
quiet and perform no continuation work; after expiry or uncertainty retire the schedule
and report the actionable blocked state. A new user stop overrides the saved intent.

For a real later turn:

1. Inspect native turn evidence: exact same chat, origin turn completed, current turn
   different. Recheck selection, checkpoint/context/source/next-action bindings,
   authority, no conflicting jobs, adequate fresh resources and the retained lease.
   A persisted model preference cannot prove the model that executed a particular turn.
2. Run `claim` once. Its exclusive durable spent receipt precedes any task operation;
   concurrent/duplicate wakes cannot acquire another claim. A crash after reservation
   is unknown and never automatically replayed. Claim alone does not authorize work.
3. Pause or delete the exact native heartbeat. Read back/confirm retirement, then use
   `retire` with fresh evidence. Only its one successful ready result permits the
   bounded continuation. A failed/uncertain retirement records an unknown outcome and
   stops; it must not keep trying the task. Duplicate later wakes only reconcile or
   retire scheduling, without reacquiring a spent operation.
4. Resume from the verified handoff within current authority, record a minimal receiving
   receipt and mark the handoff operation complete. Briefly confirm resumed work only
   after it actually starts; do not repeat the switching announcement on duplicate wakes.
   This does not mean the underlying
   project is finished. Preserve the spent record and task evidence. Subsequent model
   transitions need fresh operation IDs and current authority/resource checks.

The helper does not message, schedule, invoke a model or authenticate the human. Its
inputs are explicit cooperating-operator attestations; the assistant must obtain them
from the actual host, checkpoint and current user instructions. It does not protect
against a hostile same-user process rewriting both code and state. Lock/receipt recovery
is manual after uncertainty; never delete them to make a test or task proceed.

## Evidence and limits

Offline tests cover the state machine and local concurrency only. Native scheduling,
new-turn receipt and continued task behavior require a separately recorded live check.
Selection metadata is not per-turn inference telemetry. A supported route may still
wait until the host is available, fail to deliver or need user attention. Unknown
outcomes are preserved, not reported as success. No universal host or OS guarantee.

[Official scheduled-task documentation](https://learn.chatgpt.com/docs/automations)
and the native app tool describe scheduling; the
[app-server lifecycle](https://learn.chatgpt.com/docs/app-server) distinguishes a new
turn from steering an active one. Actual host observations control this adapter's
claims. Its native acceptance status is in the package validation report.

## Guard CLI

The helper exposes `prepare`, `arm`, `claim`, `retire`, `complete`, `cancel` and
`inspect`. All use `--store` for the **existing** checkpoint store. Mutations consume
`--input` with the exact private binding/evidence record; `inspect` is read-only.
The module's explicit binding/field validation defines that local JSON contract.

```sh
python3 SKILL/scripts/continuation.py prepare --store PROJECT/.checkpoint --input PREPARE.json
python3 SKILL/scripts/continuation.py inspect --store PROJECT/.checkpoint
```

Before each mutation, check the actual task owner. Obtain source/checkpoint/next-action
hashes and turn/scheduler/selection observations from their real sources; never fill
booleans merely to pass a guard. Retain the same operation ID across arm/claim/retire/
complete or cancellation. `inspect` never emits a reusable execution permit.

Cancellation does not require permission to keep working. Honor a new stop or revoked
authority, pause/delete the exact native schedule, and record cleanup even when quota
or task work gates fail. Do not delete spent receipts or locks to unblock another run.
Uninstall/rollback of the skill does not retire a previously created native heartbeat:
retire each recorded owned schedule first and preserve its task record.

Rejected stale or malformed local helper input can be corrected before a native result
is consumed; this is not permission to repeat an external action. If an actual native
pause/delete result is uncertain, record a fresh `confirmed:false` retirement outcome.
That preserves uncertainty and spends the work reservation. Later cleanup confirmation
cannot restore automatic execution permission for that work.
