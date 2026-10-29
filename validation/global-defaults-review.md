# Independent global preference review — 0.4.0

An independent read-only reviewer inspected the changed instructions, installer,
continuation guard, fixed acceptance cases and supporting references. The reviewer ran
all **80 tests** successfully and compared the candidate with immutable committed prior
source `844567dc81d861b6c622ee48d1ffd8150ff07247` in temporary profiles.

Executed comparison: the prior installer rejects `--automatic` without mutation;
legacy install followed by candidate automatic activation succeeds; unrelated prefix
and suffix instructions are byte-preserved; unflagged upgrades retain automatic mode;
manual downgrade and rollback restore the appropriate preference. These are actual
installer behaviors, not model-generated claims of correct behavior.

The reviewer found no blocking source defect. One example could imply work had resumed
immediately after selection; it was corrected to “checkpoint verified, resume pending.”
The current task-checkpoint 0.8 direct-resume contract is separated from the historical
0.5 optional worker workflow. Baseline preservation initially raced the constructor;
the comparison used committed prior source and the private installer baseline was
restored from that commit rather than relying on the raced copy.

Contract review covers model-only/effort-only/combined changes, no-op/trivial exclusion,
loaded standing human instructions instead of checkpoint authority, explicit selections
and stop/cancel precedence, and proposed/selected/scheduled/resumed distinctions.
Existing one-use guards preserve uncertainty, current resources and exclusive ownership.

This review is source inspection plus executed offline behavior. It does not certify
native scheduler delivery, per-turn executing model, universal automatic invocation or
savings. Parent verification owns final installation, public export and remote release.
