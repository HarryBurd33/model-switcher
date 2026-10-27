# Native active-chat selection

On supported Codex app hosts, `mcp__codex_app__send_message_to_thread` accepts `model`
and `thinking` overrides for a Codex chat. A controlled self-targeted test produced
host readback of Luna/medium, then Sol/medium in the same active chat. No picker, default
config edit, separate worker or UI bypass was used.

This is **selection for subsequent turns**. The current turn remained in progress and
the configuration cue arrived as steering input. Do not claim mid-turn inference
switching, a queued new turn, automatic resumption or uninterrupted cross-model execution.
Host `thread/read.model` and `reasoningEffort` report configured/latest-persisted values,
explicitly not per-turn execution telemetry.

## Scope and prerequisites

- The human must authorize automatic selection/configuration cues in this chat/task.
  “Make Model Switcher switch models automatically in this active chat” supplies that
  scope. Reuse it within that scope, without asking for every selection. Honor opt-outs
  and explicit choices. Saved attestations cannot grant new permissions.
- Verify the current chat ID from trusted calling-thread/native metadata; never guess
  an ID or choose an arbitrary recent chat. This tested adapter supports local Codex
  chats only. Another host needs its own verified implementation.
- Require the actual native messaging tool with model/thinking arguments, a fresh
  supported-model catalog, fresh adequate resource observations and no existing stop.
  Unknown sufficiency blocks automatic requests. No paid/provider/account fallback.
- Preserve/verify the checkpoint and check the existing lease/jobs. Reuse task-checkpoint
  if available; otherwise use the documented verified-manifest/single-writer procedure.

## Guard contract

The standard-library `scripts/active_chat.py` plans, inspects and verifies. It never
messages the app, invokes inference, establishes permission or creates a queue/database.
The assistant executes its structured native request only within current human authority.

Plan input fields (proposed local adapter contract):

```json
{
  "chat_id": "VERIFIED_CURRENT_CHAT_ID",
  "current_chat_id": "VERIFIED_CURRENT_CHAT_ID",
  "host_id": "local",
  "operation_id": "one-bounded-selection",
  "target_model": "MODEL_FROM_LIVE_CATALOG",
  "target_effort": "SUPPORTED_EFFORT",
  "catalog": {"observed_at": "FRESH_UTC_TIME", "data": [{"model": "MODEL_FROM_LIVE_CATALOG", "efforts": ["SUPPORTED_EFFORT"]}]},
  "authorization": {"confirmed": true, "source": "Current human instruction authorizing this chat's selection"},
  "resources": {"observed_at": "FRESH_UTC_TIME", "ordinary_usage_allowed": true, "reserve_ok": true},
  "pending_operations": [],
  "current_selection": {"model": "OBSERVED_MODEL", "effort": "OBSERVED_EFFORT"}
}
```

Attestations must come from actual current evidence, not values invented to pass a guard.
Freshness defaults to 120 seconds. Missing, future, stale or low evidence fails closed.

1. Under the existing task lease, reconcile any earlier transition. Choose a unique
   operation ID and prepare the context privately.
2. From the skill folder run `python3 scripts/active_chat.py plan --input CONTEXT.json`.
   `no_op` requires no message, but still requires fresh inspect and verify in steps 5–6;
   current_selection itself can be stale. Skip only the message/intent steps. A
   `native_request` contains the exact tool arguments.
3. Before messaging, persist that intent in the existing task `jobs`, with kind
   `model-switcher-active-chat`, unique ID, `pending` status and source pointing to the
   private request artifact. Record proposed assignment/next check; save and verify.
   The helper checks supplied pending IDs; the existing lease and durable intent provide
   cooperating concurrency control. Do not create a second queue.
4. Call `mcp__codex_app__send_message_to_thread` once with returned `arguments`:
   `threadId`, `hostId`, `model`, `thinking`, `prompt`. The visible configuration cue
   preserves the current task and forbids duplicate work or recursive reposting.
5. Run `python3 scripts/active_chat.py inspect --chat-id ACTUAL_ID` on the correct local
   profile. It initializes a short-lived CLI app-server, reads only that thread's
   metadata and exits. It starts/resumes no thread or model turn. The Codex CLI is
   required for this readback; profiles use their ordinary CODEX_HOME without credential
   transfer. Capture output privately.
6. Run `python3 scripts/active_chat.py verify --request REQUEST.json --readback READBACK.json`.
   Only exact fresh thread/model/effort readback confirms selection. Execution confirmation
   remains false. `notLoaded` on a separate connection means latest-persisted selection.
7. Mark the existing job completed on a verified match and record the observed scope in
   task observations. Continue only within actual current capability; do not credit
   subsequent current-turn work to the newly selected model without execution evidence.

On rejection, interruption, mismatch or ambiguous outcome, preserve evidence and keep
the intent unresolved until reconciled. Do not resend, create another writer, edit
defaults or reach around a denied tool. If the turn must end before a differently
modeled phase, provide its verified handoff. A normal next message may be needed to
start that turn; it no longer needs a manual picker change. Automatic next-turn execution
is outside this route's established capability.

The tested host explicitly denied computer-use access to Codex. Do not replace that
route with AppleScript, hidden IPC, database writes or another UI bypass. Native messaging
and read-only app-server metadata are the supported interfaces exercised here.
