# Model Switcher 0.1.1

A user-level Codex policy for strong planning, economical qualified work and verified
completion. Subscription allowance and API spending are separate resources. This is a
thin companion to `task-checkpoint` 0.5.0; it installs no router, queue or background service.

## Install and activate

Review the folder, especially `SKILL.md` and `scripts/install.py`, then from this folder:

```sh
python3 scripts/install.py install
python3 scripts/install.py status
```

Default destination: `~/.agents/skills/model-switcher/`. Default global instruction file:
`${CODEX_HOME:-~/.codex}/AGENTS.md`. Explicit locations use `--skills-dir PATH` and
`--codex-home PATH`. Python 3.9+ standard library is sufficient for installation.

The default installer appends a small managed global instruction block. It preserves
existing text, configuration and hooks, and refuses unmanaged/customized destinations,
changed activation blocks, symlinks and unresolved interrupted installs. No hook trust
or model defaults are changed. `--no-global` installs discovery only; using it on a later
install also removes the previously managed block while preserving other text.

Open a new local Codex chat after installation. Invoke `$model-switcher`, or ask for
substantial work. The metadata permits implicit invocation; the global instructions
request intake and meaningful phase checks. Availability, matching, instruction loading
and executed behavior are separate evidence. Instructions do not guarantee invocation
on every turn, existing chat, device or cloud host. An existing global
`AGENTS.override.md`, project overrides or instruction-size limits may change what loads;
verify the loaded sources and reconcile precedence rather than editing unrelated files.

For another local Codex profile, run `python3 scripts/install.py activate --codex-home PROFILE_HOME`.
This manages only that profile’s global instruction block and shares the primary skill.
Use `deactivate` with the same profile home before uninstalling the primary shared skill.
`status` reports whether a profile owns the skill or only activation. Other devices need
independent installation.

The basic mode needs skill access, artifact read/write and a verified checkpoint/handoff.
Automated workers additionally need installed task-checkpoint, Python/Git, a correct
binding, exclusive ownership, current authorization, qualified adapters, live model
availability and resource sufficiency. Without optional integrations the skill gives a
ready manual handoff. It requires no new paid service. The optional task-checkpoint runtime is not bundled
and is not currently provided as a public dependency; manual mode works without it.

## Use

`$model-switcher Complete this feature with these acceptance tests.`

At substantial intake the skill resolves difficult decisions with the strongest suitable
available model, then considers qualified cheaper assignments or lower reasoning effort.
It preserves user choices and skips expensive orchestration for trivial work. See
[examples](references/examples.md), [runtime mapping](references/runtime.md) and
[manual switching](references/host.md). A selected CLI worker is separate from the active
desktop conversation. This package cannot automatically switch that desktop chat.

## Update, rollback, uninstall

Keep the previous source package. Run a reviewed newer package's `scripts/install.py
install` with the same paths. Hashes must match the prior managed install; conflicts
preserve changes for review. One previous managed version is kept privately under
`CODEX_HOME/model-switcher-install/prior`.

```sh
python3 scripts/install.py rollback
python3 scripts/install.py uninstall
```

Rollback restores the previous managed skill and activation block, retaining unrelated
global edits. The first install has no prior version; uninstall removes it. Uninstall
removes only unchanged managed files and its activation block, preserving checkpoint
state and all existing services/hooks/settings. Preserve customized files and reconcile
them before retrying a blocked update/removal. The installer never resolves conflicts
by deleting user work. For an interrupted transaction, inspect `pending.json`,
`operation.lock`, target/global files and receipts; confirm no installer is running and
recover the previous state explicitly. Never blindly delete these evidence files.

Tests and build evidence ship alongside the package in the delivery archive. The installed
folder includes the concise [capability report](references/capabilities.md). Private task
state, account identities, approvals, raw logs and credentials are excluded.

## Foundations and rights

Original companion files are MIT licensed. No task-checkpoint or Codex source is copied.
The installed task-checkpoint runtime is an external dependency with independent update
and licensing history. Its installed 0.5.0 snapshot was inspected; installed revision
cannot be equated to a different source checkout. Official reference pages:
[Build skills](https://learn.chatgpt.com/docs/build-skills),
[App server](https://learn.chatgpt.com/docs/app-server),
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
Use current host evidence before relying on an interface.
