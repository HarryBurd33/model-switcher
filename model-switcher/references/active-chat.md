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

- The human must authorize automatic selection/configuration cues in this chat/task,
  either directly or through their currently loaded global automatic preference.
  “Make Model Switcher switch models automatically in this active chat” supplies that
  scope. An explicit standing global instruction covers each authorized task in chats
  loading that profile; do not demand another per-chat opt-in. Verify that live source,
  rather than deriving authority from a saved task. Reuse it within scope, without asking for every selection. Honor opt-outs
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
   operation ID and prepare the context privately. Record the exact next action,
   acceptance check, target model/effort and reason in the verified checkpoint/handoff.
   Briefly announce the proposed change and reason; effort-only changes count too.
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
   profile. Version 0.3.1 uses the supported `codex app-server proxy` connection to an
   already-running local daemon, with its required WebSocket protocol. It sends only
   initialization and `thread/read`, then closes its connection. It does not start a
   server, resume a thread, or create a model turn. A missing socket, incompatible
   protocol or unverifiable selection blocks continuation; never fall back to starting
   an app-server, searching other sockets, or changing profiles. Capture output privately.
6. Run `python3 scripts/active_chat.py verify --request REQUEST.json --readback READBACK.json`.
   Only exact fresh thread/model/effort readback confirms selection. Execution confirmation
   remains false. `notLoaded` on a separate connection means latest-persisted selection.
7. Mark the existing job completed on a verified match and record the observed scope in
   task observations. Give one brief confirmed-selection notice with model, effort and
   reason; distinguish a scheduled resume from an observed one. If the boundary requires
   the changed setting, end this turn and use the authorized continuation procedure.
   Continue only within actual current capability; do not credit
   subsequent current-turn work to the newly selected model without execution evidence.

On rejection, interruption, mismatch or ambiguous outcome, preserve evidence and keep
the intent unresolved until reconciled. Do not resend, create another writer, edit
defaults or reach around a denied tool. If the turn must end before a differently
modeled phase, provide its verified handoff. A normal next message may be needed to
start that turn; it no longer needs a manual picker change. Automatic next-turn execution is separate from this selection route; use the
[authorized continuation guard](continuation.md) and its actual native acceptance evidence.

The tested host explicitly denied computer-use access to Codex. Do not replace that
route with AppleScript, hidden IPC, database writes or another UI bypass. Native messaging
and read-only app-server metadata are the supported interfaces exercised here.

## Metadata transport boundary (0.3.1)

The older inspector launched `app-server --stdio`. Read-only RPC intent does not make
that server's startup read-only: pinned CLI 0.164.0 can resolve persisted remote-control
enrollment. The current inspector therefore connects only through the public proxy
command to an already-running daemon. It cannot supply this capability on a host where
that daemon is absent, and does not create or configure a service to fill the gap.

The proxy relays bytes; the control socket requires a WebSocket upgrade and frames.
Source evidence: [proxy dispatch](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/cli/src/main.rs#L1478),
[relay](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/stdio-to-uds/src/lib.rs#L12),
[acceptor](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/app-server-transport/src/transport/unix_socket.rs#L193).
This establishes the transport path, not universal host availability or globally
write-free CLI behavior. Earlier successful selection observations retain their
historical scope; they do not certify the current transport on another host.
