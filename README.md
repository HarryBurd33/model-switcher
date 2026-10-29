# Model Switcher

[MIT licensed](LICENSE) Codex skill for strong planning, qualified economical assignments,
and verified completion. It treats Codex subscription allowance and API spending as
separate resources, and counts handoff, validation, review, retries and repair as overhead.

## What it does

- Requests the strongest suitable available model for consequential planning, then
  considers qualified cheaper workers or lower reasoning effort for bounded work.
- Keeps acceptance criteria, privacy, explicit model choices and stop policies intact.
- Automatically selects this active chat’s model/effort for subsequent turns when the
  native app interface is present and this chat’s user has authorized it.
- Can schedule a guarded automatic continuation after that transition when explicitly
  authorized, including by a saved global preference, using one checkpoint-bound claim
  and retiring the schedule before work.
- Briefly explains each model or effort change and resumes its saved next action from
  a verified checkpoint/handoff when the host supports automatic continuation.
- Produces a verified manual handoff when an automatic route is unavailable.
- Installs a user-wide skill and global instructions requesting its use for substantial
  work. Trivial corrections stay lightweight.

This is an instruction policy with tested setup and a guarded native selection route.
It can update the same active chat’s selected model/effort for subsequent turns. It does
not switch an inference already running or guarantee delivery, invocation in every
chat, exactly-once external effects, or lower cost. Global instructions are interpreted by Codex; project overrides, opt-outs, alternate
profiles and host capabilities still apply. A selected-model CLI worker is a separate
operation. [Capabilities and evidence](model-switcher/references/capabilities.md).

## Install globally for your user

Requires Python 3.9+ and a Codex host that loads local skills and AGENTS instructions.
The installer and native integration were exercised on macOS; other OS environments
have not been certified by this project.

```sh
git clone https://github.com/HarryBurd33/model-switcher.git
cd model-switcher
python3 model-switcher/scripts/install.py install
python3 model-switcher/scripts/install.py status
```

To make automatic model **and reasoning effort** switching with checkpoint-based resume
your default in every chat using this Codex profile, run:

```sh
python3 model-switcher/scripts/install.py install --automatic
```

This saves your standing instruction in the managed global block. It authorizes suitable
same-chat transitions and bounded resume of already authorized tasks without another
per-chat opt-in. Each switch saves/verifies the handoff, selects/verifies the target,
briefly names the model/effort and reason, then schedules the saved next action and ends
the origin turn. The guarded receiver resumes once after retiring the schedule.
It never changes an inference already running. An unavailable interface yields a ready
handoff with the required action. Installation creates no schedule or background service.

Use `install --manual` to return this profile to recommendations/manual handoffs.
Updates without either flag preserve the saved mode; a fresh install without either
flag supplies policy guidance and requires explicit automatic authorization. `status`
reports `automation_mode`. An explicit current model/effort choice, opt-out or stop
overrides the standing preference. Automatic mode adds no paid API or external-action
permissions. Existing chats may need a new turn or reopening to load changed global
instructions; it does not broadcast instructions to other chats.

Default skill location: `~/.agents/skills/model-switcher`. Default global instructions:
`$CODEX_HOME/AGENTS.md`, or `~/.codex/AGENTS.md` when CODEX_HOME is unset. Existing text
and configuration are preserved. No hook trust, account setting, model default, queue,
service or scheduler is installed.

Start a new Codex chat after installing. Substantial requests should use the policy
automatically through the global instructions. To request it explicitly:

```text
$model-switcher Implement this feature and verify the supplied acceptance tests.
```

You can also say “Use Model Switcher for this task.” To opt out: “Stay on my selected
model and do not route or delegate this task.” Without a global automatic preference,
to authorize native automatic selection once for the current chat/task, say:

```text
$model-switcher Automatically select models and reasoning effort in this chat.
```

The native route uses a user-visible configuration cue and verifies host readback.
It requires the Codex app messaging tool plus the CLI for readback; CLI-only and
unverified hosts retain manual fallback. [Native procedure](model-switcher/references/active-chat.md).

Without the standing preference, to also continue without another typed resume message,
explicitly request:

```text
Use Model Switcher to change models and automatically continue this task at safe
boundaries, preserving its checkpoint and preventing duplicate work.
```

This opts in only the current task. Follow the [continuation procedure](model-switcher/references/continuation.md);
manual picker changes alone do not trigger it. Context and control state stay private.
The same-chat heartbeat is the receiver, not a message-sending loop. Current permissions,
resource stops and cancellation still apply. Native acceptance is reported separately
from offline guard tests.

When a manual transition is useful, follow
the packet's exact model/effort, picker steps and resume instruction.

If you use another local Codex profile, keep one shared skill install and activate that
profile's own global instructions:

```sh
python3 model-switcher/scripts/install.py activate --codex-home /absolute/path/to/other-codex-home
python3 model-switcher/scripts/install.py status --codex-home /absolute/path/to/other-codex-home
```

Add `--automatic` to `activate` to save the same standing preference in that profile.
Profiles retain independent preferences; sharing the skill does not copy consent.

The extra profile owns only its activation block, never the shared skill. On another
device, install there independently. `--no-global` with `install` supplies discovery only.
See [setup, update, rollback and uninstall](model-switcher/README.md).

## Execution modes

**Manual mode works without another skill.** Use available file tools to save/reread a
handoff and artifact-hash manifest, establish a cooperating single writer, and obtain
fresh authority/resources before continuing. See both variants in the
[handoff template](model-switcher/templates/handoff.md).

**Automated workers are an optional external integration.** The documented integration
uses task-checkpoint 0.5.0, its existing identity/store/lease/router, and independently
qualified model/effort/tools/privacy assignments. That runtime is not bundled and is not
currently supplied as a public dependency by this repository. Public installation alone
provides policy/manual mode and the conditional native selection route, not automatic
worker execution. A host
with that compatible runtime can follow the [runtime procedure](model-switcher/references/runtime.md).
No paid API fallback is enabled; API execution needs a separate authorized provider and
explicit spending boundary. Unknown telemetry and unmeasured savings remain unknown.

## Validation and releases

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output dist/model-switcher-0.4.0.zip
```

The build validates metadata, relative links, MIT notices and the explicit public file
map, then produces a deterministic installable ZIP. It performs no inference or account
calls. Release assets are available on the [releases page](https://github.com/HarryBurd33/model-switcher/releases).

The missing manual case was exercised against a real immutable checkpoint by a fresh
read-only model context and independently graded against all eight fixed checks. It
returned an exact verified path, supported model/effort, manual steps and filled resume
instruction. It did not switch the desktop model or perform receiving implementation.
Historical synthetic results remain unchanged. [Validation report](validation/REPORT.md).

No production coding benchmark, full device transfer or general savings guarantee is
claimed. Private checkpoints, raw account observations, transcripts, approvals and local
Git history are excluded from public exports.

## License and contributions

Original files are [MIT licensed](LICENSE), including the installed skill. Dependency
rights remain separate; no external runtime source is vendored. Contributions should
include a reproducible case and preserve existing fixed acceptance criteria and evidence.
Do not include credentials or private task state in issues or pull requests.
