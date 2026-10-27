# Independent active-chat selection review

Result: **Source and observed selection behavior approved within the stated scope.**
The evidence supports native configuration of the same chat's selected model/effort for
subsequent turns. It does not prove that an already-running inference changed model,
that a new turn started, or that a saved record supplied new authority.

## Observed native behavior

The reviewer inspected the private operation record and both host readbacks. They
identify the same chat and report first Luna/medium, then Sol/medium, from separate
read-only app-server connections. Both metadata responses have `notLoaded` status on
that separate connection, so their proper scope is **latest persisted selection**.
The same original turn remained in progress and the configuration cue was delivered
as steering. Tool acceptance and persisted selection are not per-turn execution telemetry.

The native tool's structured model/thinking override is a supported interface separate
from the computer-use route, which explicitly rejected Codex access. The implementation
neither automates that rejected UI nor edits hidden state/default model settings.
Private chat IDs, local paths, account state and raw conversation data are not reproduced
in this report.

## Guard and protocol checks

- All **13 active-chat tests passed**. They cover exact native arguments, wrong chat/host,
  missing authority, stale/future/missing observations, resource stops/unknown values,
  missing or ambiguous models/efforts, pending operations, no-op behavior, readback
  mismatches, prompt injection, regular JSON inputs and the read-only inspection protocol.
- All **16 existing installer/profile tests passed**.
- The helper's inspector sends only initialize, initialized and metadata-only thread/read;
  it starts/resumes no thread or model turn. The subprocess is terminated and waited.
- Verification always reports `execution_confirmed: false`. A matching readback confirms
  only configured/persisted selection, with loading scope named explicitly.
- The guard receives caller attestations for current identity, human scope, catalog,
  resources and pending operations. It cannot authenticate those facts or create authority.
  The instructions require actual current evidence, the existing lease, durable intent
  before messaging, one native request and independent readback before completing a job.
- The helper creates no queue, checkpoint database, scheduler, service or paid API route.
  A failed/unknown request must remain unresolved; it is not automatically resent.

An additional reviewer characterization confirmed that an assumed no-op followed by a
mismatched fresh host readback is rejected. `current_selection` itself has no timestamp;
therefore **inspect and verify remain required even when plan returns no_op**. That is the
success gate rather than a stale supplied selection being accepted as host evidence.

## Claims, compatibility and privacy

The new common instructions and conditional host reference distinguish selection,
mid-turn inference, worker execution and automatic continuation. They preserve explicit
model choices, opt-outs, current-chat-only authorization, resource stops and manual
fallback. They do not advertise the private optional worker runtime as a public bundled
capability. The local host is the supported native adapter; other hosts need verification.

The explicit release map lists 37 candidate public files and excludes private checkpoint,
operation/readback files, raw transcripts, account data and local Git history. Root and
skill MIT notices remain consistent. The new source itself contains no personal absolute
paths or credentials. Final package privacy/integrity and installed correspondence still
need their release checks after all evidence files are present.

## Release gates still required at source-review time

1. Preserve the original prototype readbacks as historical evidence. They predate the
   helper's exact source/timestamp format; run the helper's actual read-only inspect and
   verify with fresh host output rather than refreshing timestamps on old evidence.
2. Create the public-safe active-chat evidence record and rerun package tests. Both package
   tests initially failed solely because that new allowlisted evidence file was not yet
   present, not because an archive invariant passed. This report's creation alone does not
   close that gate.
3. Refresh final source hashes; verify managed installation, native profile loading, exact
   public export, deterministic archive and downloaded release bytes. Existing 0.1.1
   installation or CI evidence does not certify new 0.2.0 bytes.
4. Read back the authorized remote commit, release asset and hosted CI outcome separately.

No additional model turn, native selection, message, ownership transition, installation
or publication was executed by this reviewer. The source review must not be reported as
proof that those later release gates have already passed.

## Follow-up verification — source gates closed

The no-op instructions now explicitly require fresh inspect and verify even when no
message is sent. The reviewer inspected the new private live-proof record: it contains
actual fresh catalog/resource context, helper-produced readback with the required source
and observation time, a `no_op` plan, and successful verification. Independent replay
using the captured observation time reproduces both plan and verification exactly:
selection confirmed, execution unconfirmed, latest-persisted scope. No new native message
or model turn was needed for that check. The historical prototype readbacks remain
unchanged rather than receiving invented fresh timestamps.

The public evidence record's proof hash matches the inspected private proof. It contains
only sanitized selection facts, limitations and hashes, with no chat ID, local path,
account/resource record or transcript. The full **31-test suite now passes**: 13 selection
guards, 16 installer/profile regressions and two deterministic package tests. Public
release-map validation passes for all 37 listed files. The earlier missing-evidence
package errors are therefore resolved; they are retained above as historical outcomes.

No implementation, source-claim or source-publicity blocker remains within the documented
scope. Final installation/profile readback, final source/export/archive correspondence,
remote commit/asset checks and hosted CI remain separate parent-owned release gates.
