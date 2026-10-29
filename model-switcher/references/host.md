# Host discovery and manual operation

Recheck the current host before automating. Observed during this build: macOS, Codex CLI
0.164.0; supported `codex exec -m MODEL -c model_reasoning_effort=EFFORT`, read-only or
workspace-write sandboxes, and app-server `model/list`. The existing task-checkpoint
adapter verifies ChatGPT identity and live model/effort availability. Do not replace it
with a raw CLI command when its protections apply.

`model/list` provides available IDs and supported efforts, not a universal strength or
price order. Use its current account catalog plus relevant observed capability evidence.
`config/read` can report defaults; an explicit turn override can differ. A current model
reported by a trusted thread surface is stronger evidence than a config default. If no
such surface is exposed, effective desktop model/effort remain unknown.

App-server `turn/start` supports model/effort for threads owned by that server. That is
not evidence of control over an unrelated live desktop chat. The native app messaging
tool is a separate verified surface: model/effort overrides can set this same chat's
selection for subsequent turns. Use the [guarded native procedure](active-chat.md).
Do not guess thread IDs or call another session to change this one. This does not prove
mid-turn inference switching. Default edits do not retroactively change the active chat.

With continuation authority from the current user or loaded standing global automatic
preference, and verified scheduling, use the
[continuation procedure](continuation.md). Otherwise, when automatic continuation or
its verification is unavailable, use manual desktop transition:

1. Choose an exact model and effort from the current catalog/picker and record why.
2. Save/verify the complete task-checkpoint bundle, jobs and artifacts; release the lease
   only at a safe handoff boundary. If a durable save fails, stop dependent work and give
   an explicitly unsaved emergency handoff.
3. Tell the user: “In Codex, use this chat's model/reasoning picker to choose MODEL,
   EFFORT. If unavailable there, start a chat on a host that offers it. Resume using the
   instruction below.” Picker placement can change; do not invent a slash command.
4. Give the exact checkpoint HANDOFF.md path and a copyable instruction filled from
   [the template](../templates/handoff.md). State that user action is required.
5. The receiver reads/inspects, verifies artifacts/jobs/state/current authority/resources,
   uses the current installed checkpoint contract, acquires only a vacant matching
   lease without a 0.8 recovery review, then performs the bounded action.

Global availability: `~/.agents/skills/model-switcher/SKILL.md`; metadata permits implicit
matching. Skill discovery and invocation differ. A managed global AGENTS.md rule provides
an intake reminder in new local sessions and policy calls at phase boundaries; it remains
an instruction interpreted by the model, not an enforced execution hook. Retired checkpoint hooks are not required for cooperative 0.8 use. An optional
quota collector only observes allowance. This installer
does not modify their configuration or establish guaranteed continuous invocation.

Official sources inspected 2026-10-26 (America/Denver):
[Build skills](https://learn.chatgpt.com/docs/build-skills),
[App server](https://learn.chatgpt.com/docs/app-server),
[Global AGENTS instructions](https://developers.openai.com/codex/guides/agents-md).
Installed CLI help and runtime inspection supply the host-specific evidence; future
documentation may describe features absent from that installed version.
