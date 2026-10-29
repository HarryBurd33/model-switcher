import copy
import datetime as dt
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / 'model-switcher/scripts/continuation.py'
spec = importlib.util.spec_from_file_location('continuation', SCRIPT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
NOW = dt.datetime(2026, 10, 27, 8, 0, tzinfo=dt.timezone.utc)


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Path(self.tmp.name)
        self.b = {'operation_id': 'switch-1', 'chat_id': 'chat-one', 'task_id': 'task-one',
                  'host_id': 'local', 'base_checkpoint': {'id': 'base-1', 'manifest_sha256': 'a'*64},
                  'source_fingerprint': 'b'*64, 'next_action_sha256': 'c'*64,
                  'origin_turn_id': 'turn-original', 'target': {'model': 'model-b', 'effort': 'ultra'},
                  'lease': {'owner': 'logical-owner', 'token': 'private-token'},
                  'authorization_scope_sha256': 'd'*64,
                  'expires_at': (NOW + dt.timedelta(minutes=10)).isoformat()}
        self.e = {'observed_at': NOW.isoformat(), 'source': 'Synthetic current observation',
                  'chat_id': self.b['chat_id'], 'task_id': self.b['task_id'], 'host_id': 'local',
                  'lease': {**self.b['lease'], 'verified': True},
                  'base_checkpoint': copy.deepcopy(self.b['base_checkpoint']),
                  'current_checkpoint': copy.deepcopy(self.b['base_checkpoint']),
                  'context_unchanged': True, 'source_fingerprint': self.b['source_fingerprint'],
                  'next_action_sha256': self.b['next_action_sha256'],
                  'authorization': {'confirmed': True, 'continuation_allowed': True,
                                    'scope_sha256': 'd'*64, 'source': 'Synthetic human authorization'},
                  'resources': {'adequate': True, 'reserve_ok': True}, 'stopped': False,
                  'jobs_verified': True, 'jobs': []}
        self.s = {'confirmed': True, 'observed_at': NOW.isoformat(), 'source': 'Synthetic host readback',
                  'chat_id': self.b['chat_id'], **self.b['target']}
        self.scheduler = {'id': 'schedule-one', 'confirmed': True,
                          'observed_at': NOW.isoformat(), 'source': 'Synthetic native scheduler receipt'}

    def call(self, command, extra=None, now=NOW):
        doc = {'operation_id': self.b['operation_id'], 'evidence': copy.deepcopy(self.e)}
        doc.update(extra or {})
        return c.operate(command, self.store, doc, now)

    def prepare(self):
        return self.call('prepare', {'binding': copy.deepcopy(self.b)})

    def arm(self):
        self.prepare()
        return self.call('arm', {'selection': copy.deepcopy(self.s), 'scheduler': self.scheduler})

    def receiver(self):
        self.e.update(origin_turn_id=self.b['origin_turn_id'], origin_turn_status='completed',
                      current_turn_id='turn-receiver')

    def claim(self):
        self.arm(); self.receiver()
        return self.call('claim', {'selection': copy.deepcopy(self.s)})

    def retirement(self, **values):
        return {'retirement': {**self.scheduler, 'status': 'paused', **values},
                'selection': copy.deepcopy(self.s)}

    def ready(self):
        self.claim()
        return self.call('retire', self.retirement())

    def complete(self):
        return self.call('complete', {'outcome': {'status': 'completed', 'effects_reconciled': True,
                                                 'evidence': 'Synthetic bounded work verified'}})

    def test_prepare_and_arm_do_not_execute_or_disclose_lease(self):
        prepared = self.prepare()
        self.assertEqual(prepared['state'], 'prepared'); self.assertFalse(prepared['execute'])
        armed = self.call('arm', {'selection': self.s, 'scheduler': self.scheduler})
        self.assertEqual(armed['state'], 'armed'); self.assertFalse(armed['execute'])
        self.assertNotIn('private-token', json.dumps(armed))
        self.assertFalse(armed['execution_model_confirmed'])
        state = c.read_json(self.store / (c.PREFIX + '.json'))
        self.assertEqual(state['binding']['base_checkpoint'], self.b['base_checkpoint'])

    def test_claim_requires_retirement_and_ready_is_emitted_only_once(self):
        claimed = self.claim()
        self.assertEqual(claimed['state'], 'claimed'); self.assertFalse(claimed['execute'])
        self.assertTrue(c.work_receipt(self.store, self.b).is_file())
        with self.assertRaises(c.GuardError): self.complete()
        ready = self.call('retire', self.retirement())
        self.assertEqual(ready['state'], 'ready'); self.assertTrue(ready['execute'])
        self.assertFalse(c.operate('inspect', self.store, now=NOW)['execute'])
        with self.assertRaises(c.GuardError): self.call('retire', self.retirement())
        with self.assertRaises(c.GuardError): self.call('claim', {'selection': self.s})
        self.assertEqual(self.complete()['state'], 'completed')
        self.assertTrue(c.work_receipt(self.store, self.b).exists())

    def test_different_operation_id_cannot_replay_same_checkpoint_action(self):
        self.ready(); self.complete(); self.b['operation_id'] = 'fresh-id'
        with self.assertRaisesRegex(c.GuardError, 'already spent'): self.prepare()

    def test_new_checkpoint_action_can_follow_completed_work(self):
        self.ready(); self.complete()
        self.b['operation_id'] = 'switch-2'; self.b['next_action_sha256'] = 'e'*64
        self.e['next_action_sha256'] = 'e'*64
        self.assertEqual(self.prepare()['state'], 'prepared')
        self.assertTrue(c.receipt(self.store, 'switch-1', 'final').exists())

    def test_second_pending_intent_cannot_replace_the_first(self):
        self.prepare(); self.b['operation_id'] = 'other'
        with self.assertRaises(c.GuardError): self.prepare()
        self.assertEqual(c.operate('inspect', self.store, now=NOW)['operation_id'], 'switch-1')

    def test_current_or_unfinished_turn_is_not_a_receiver(self):
        self.arm(); self.receiver()
        for changes in [{'origin_turn_status': 'active'}, {'origin_turn_status': 'unknown'},
                        {'current_turn_id': 'turn-original'}, {'origin_turn_id': 'other'}]:
            e = {**self.e, **changes}
            with self.assertRaises(c.GuardError):
                self.call('claim', {'selection': self.s, 'evidence': e})
        self.assertFalse(c.work_receipt(self.store, self.b).exists())

    def test_wrong_task_chat_host_or_lease_blocks_without_reservation(self):
        self.arm(); self.receiver()
        for changes in [{'chat_id': 'other'}, {'task_id': 'other'}, {'host_id': 'remote'},
                        {'lease': {**self.e['lease'], 'token': 'other'}},
                        {'lease': {**self.e['lease'], 'verified': False}}]:
            with self.assertRaises(c.GuardError):
                self.call('claim', {'selection': self.s, 'evidence': {**self.e, **changes}})
        self.assertFalse(c.work_receipt(self.store, self.b).exists())

    def test_stale_future_or_naive_evidence_blocks(self):
        self.arm(); self.receiver()
        for stamp in [(NOW-dt.timedelta(seconds=121)).isoformat(),
                      (NOW+dt.timedelta(seconds=1)).isoformat(), NOW.replace(tzinfo=None).isoformat()]:
            with self.assertRaises(c.GuardError):
                self.call('claim', {'selection': self.s, 'evidence': {**self.e, 'observed_at': stamp}})
        self.assertFalse(c.work_receipt(self.store, self.b).exists())

    def test_low_unknown_resources_stop_and_revoked_authority_block(self):
        self.arm(); self.receiver()
        variants = [{'resources': {'adequate': False, 'reserve_ok': True}},
                    {'resources': {'adequate': True, 'reserve_ok': False}},
                    {'resources': {}}, {'stopped': True}, {'stopped': None},
                    {'authorization': {**self.e['authorization'], 'continuation_allowed': False}},
                    {'authorization': {**self.e['authorization'], 'scope_sha256': 'e'*64}}]
        for changes in variants:
            with self.assertRaises(c.GuardError):
                self.call('claim', {'selection': self.s, 'evidence': {**self.e, **changes}})
        self.assertFalse(c.work_receipt(self.store, self.b).exists())

    def test_changed_source_next_action_or_checkpoint_blocks(self):
        self.arm(); self.receiver()
        for changes in [{'source_fingerprint': 'e'*64}, {'next_action_sha256': 'e'*64},
                        {'base_checkpoint': {'id': 'base-2', 'manifest_sha256': 'a'*64}},
                        {'context_unchanged': False}]:
            with self.assertRaises(c.GuardError):
                self.call('claim', {'selection': self.s, 'evidence': {**self.e, **changes}})
        self.assertFalse(c.work_receipt(self.store, self.b).exists())

    def test_checkpoint_lineage_requires_explicit_unchanged_context(self):
        self.arm(); self.receiver()
        self.e['current_checkpoint'] = {'id': 'intent-checkpoint', 'manifest_sha256': 'f'*64}
        with self.assertRaises(c.GuardError): self.call('claim', {'selection': self.s})
        self.e['lineage_verified'] = True
        self.assertEqual(self.call('claim', {'selection': self.s})['state'], 'claimed')

    def test_other_active_or_uncertain_jobs_and_unknown_inventory_block(self):
        self.arm(); self.receiver()
        for status in ['running', 'unknown', 'pending']:
            self.e['jobs'] = [{'id': 'other-job', 'status': status}]
            with self.assertRaises(c.GuardError): self.call('claim', {'selection': self.s})
        self.e['jobs'] = []; self.e['jobs_verified'] = False
        with self.assertRaises(c.GuardError): self.call('claim', {'selection': self.s})
        self.e['jobs_verified'] = True
        self.e['jobs'] = [{'id': 'switch-1', 'status': 'pending'}, {'id': 'old', 'status': 'completed'}]
        self.assertFalse(self.call('claim', {'selection': self.s})['execute'])

    def test_selection_mismatch_or_staleness_cannot_arm_or_claim(self):
        self.prepare()
        for changed in [{'model': 'other'}, {'effort': 'low'}, {'chat_id': 'other'},
                        {'confirmed': False}, {'observed_at': (NOW-dt.timedelta(seconds=121)).isoformat()}]:
            with self.assertRaises(c.GuardError):
                self.call('arm', {'selection': {**self.s, **changed}, 'scheduler': self.scheduler})
        self.call('arm', {'selection': self.s, 'scheduler': self.scheduler}); self.receiver()
        with self.assertRaises(c.GuardError): self.call('claim', {'selection': {**self.s, 'model': 'other'}})

    def test_scheduler_creation_requires_confirmed_fresh_identity(self):
        self.prepare()
        for changes in [{'id': ''}, {'confirmed': False}, {'observed_at': (NOW-dt.timedelta(seconds=121)).isoformat()}]:
            with self.assertRaises(c.GuardError):
                self.call('arm', {'selection': self.s, 'scheduler': {**self.scheduler, **changes}})

    def test_expiry_does_not_reserve_or_extend_intent(self):
        self.arm(); self.receiver()
        later = NOW + dt.timedelta(minutes=11)
        self.e['observed_at'] = later.isoformat(); self.s['observed_at'] = later.isoformat()
        with self.assertRaisesRegex(c.GuardError, 'expired'):
            self.call('claim', {'selection': self.s}, later)
        self.assertFalse(c.work_receipt(self.store, self.b).exists())

    def test_cancel_before_claim_and_confirmed_retirement_never_execute(self):
        self.arm()
        result = self.call('cancel', {'reason': 'Human cancelled'})
        self.assertEqual(result['state'], 'cancelled'); self.assertFalse(result['execute'])
        with self.assertRaises(c.GuardError): self.call('claim', {'selection': self.s})
        result = self.call('retire', self.retirement())
        self.assertTrue(result['scheduler_retired']); self.assertFalse(result['execute'])
        self.assertFalse(c.work_receipt(self.store, self.b).exists())

    def test_uncertain_creation_cannot_be_cancelled_as_absent(self):
        self.prepare()
        with self.assertRaises(c.GuardError): self.call('cancel', {'reason': 'Unknown scheduler outcome'})
        result = self.call('cancel', {'reason': 'No scheduler created', 'scheduler_absent_confirmed': True})
        self.assertEqual(result['state'], 'cancelled'); self.assertTrue(result['scheduler_retired'])

    def test_uncertain_retirement_remains_spent_even_after_later_pause(self):
        self.claim()
        result = self.call('retire', self.retirement(confirmed=False))
        self.assertEqual(result['state'], 'unknown'); self.assertFalse(result['execute'])
        result = self.call('retire', self.retirement())
        self.assertEqual(result['state'], 'unknown'); self.assertFalse(result['execute'])
        with self.assertRaises(c.GuardError): self.complete()
        result = self.call('complete', {'outcome': {'status': 'failed', 'effects_reconciled': True,
                                                  'evidence': 'No task action occurred; scheduler retired'}})
        self.assertEqual(result['state'], 'completed')
        self.b['operation_id'] = 'retry-id'
        with self.assertRaises(c.GuardError): self.prepare()

    def test_wrong_scheduler_retirement_cannot_unlock_action(self):
        self.claim()
        result = self.call('retire', self.retirement(id='other-scheduler'))
        self.assertFalse(result['execute']); self.assertEqual(result['state'], 'unknown')

    def test_stop_between_claim_and_retirement_preserves_spent_unknown(self):
        self.claim(); self.e['stopped'] = True
        with self.assertRaises(c.GuardError): self.call('retire', self.retirement())
        report = c.operate('inspect', self.store, now=NOW)
        self.assertEqual(report['state'], 'unknown'); self.assertTrue(report['reservation_present'])
        self.assertFalse(report['execute'])

    def test_concurrent_claims_have_one_exclusive_reservation(self):
        self.arm(); self.receiver()
        barrier = threading.Barrier(2); results = []
        def run():
            barrier.wait()
            try: results.append(self.call('claim', {'selection': self.s}))
            except (c.GuardError, OSError): results.append(None)
        workers = [threading.Thread(target=run) for _ in range(2)]
        for worker in workers: worker.start()
        for worker in workers: worker.join(timeout=3); self.assertFalse(worker.is_alive())
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertTrue(c.work_receipt(self.store, self.b).exists())
        self.assertFalse(any(result and result['execute'] for result in results))

    def test_concurrent_retirement_emits_at_most_one_executable_result(self):
        self.claim()
        barrier = threading.Barrier(2); results = []
        def run():
            barrier.wait()
            try: results.append(self.call('retire', self.retirement()))
            except (c.GuardError, OSError): results.append(None)
        workers = [threading.Thread(target=run) for _ in range(2)]
        for worker in workers: worker.start()
        for worker in workers: worker.join(timeout=3); self.assertFalse(worker.is_alive())
        self.assertEqual(sum(bool(result and result['execute']) for result in results), 1)
        report = c.operate('inspect', self.store, now=NOW)
        self.assertEqual(report['state'], 'ready'); self.assertTrue(report['scheduler_retired'])
        self.assertFalse(report['execute']); self.assertTrue(report['reservation_present'])

    def test_cancel_and_retire_remain_available_when_stopped_revoked_and_low(self):
        self.arm()
        self.e['stopped'] = True
        self.e['authorization'].update(confirmed=False, continuation_allowed=False)
        self.e['resources'].update(adequate=False, reserve_ok=False)
        cancelled = self.call('cancel', {'reason': 'Human revoked work at resource stop'})
        self.assertEqual(cancelled['state'], 'cancelled'); self.assertFalse(cancelled['execute'])
        retired = self.call('retire', self.retirement())
        self.assertEqual(retired['state'], 'cancelled'); self.assertTrue(retired['scheduler_retired'])
        self.assertFalse(retired['execute'])
        self.assertFalse(c.work_receipt(self.store, self.b).exists())
        with self.assertRaises(c.GuardError): self.call('claim', {'selection': self.s})

    def test_crash_after_exclusive_claim_does_not_permit_retry(self):
        self.arm(); self.receiver()
        with mock.patch.object(c, 'save', side_effect=OSError('Synthetic interruption')):
            with self.assertRaises(OSError): self.call('claim', {'selection': self.s})
        report = c.operate('inspect', self.store, now=NOW)
        self.assertEqual(report['state'], 'unknown'); self.assertTrue(report['reservation_present'])
        with self.assertRaises(OSError): self.call('claim', {'selection': self.s})
        self.assertFalse(report['execute'])

    def test_lost_ready_response_cannot_be_reissued(self):
        self.ready()
        # Pretend the caller never observed the result. Reading or retrying does not authorize work.
        self.assertFalse(c.operate('inspect', self.store, now=NOW)['execute'])
        with self.assertRaises(c.GuardError): self.call('retire', self.retirement())

    def test_missing_state_with_immutable_intent_is_not_a_fresh_store(self):
        self.prepare(); (self.store / (c.PREFIX + '.json')).unlink()
        self.b['operation_id'] = 'replacement'
        with self.assertRaisesRegex(c.GuardError, 'Unresolved'): self.prepare()

    def test_existing_lock_is_never_stolen_or_removed(self):
        lock = self.store / ('.' + c.PREFIX + '.lock'); lock.write_bytes(b'uncertain')
        with self.assertRaises(OSError): self.prepare()
        self.assertEqual(lock.read_bytes(), b'uncertain')

    def test_symlink_state_and_nonregular_inputs_are_refused(self):
        target = self.store / 'target'; target.write_text('{}')
        state = self.store / (c.PREFIX + '.json'); state.symlink_to(target)
        with self.assertRaises(c.GuardError): self.prepare()
        self.assertEqual(target.read_text(), '{}')
        with self.assertRaises(c.GuardError): c.read_json(self.store)

    def test_cli_json_contract_and_unknown_retirement_exit(self):
        self.claim()
        document = {'operation_id': self.b['operation_id'], 'evidence': self.e,
                    **self.retirement(confirmed=False)}
        private = self.store / 'reviewed-input.json'; private.write_bytes(c.encoded(document))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), mock.patch.object(c.dt, 'datetime', wraps=dt.datetime) as clock:
            clock.now.return_value = NOW
            code = c.main(['retire', '--store', str(self.store), '--input', str(private)])
        self.assertEqual(code, 2)
        result = json.loads(out.getvalue())
        self.assertEqual(result['state'], 'unknown'); self.assertFalse(result['execute'])
        self.assertNotIn('private-token', out.getvalue())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = c.main(['inspect', '--store', str(self.store)])
        self.assertEqual(code, 0); self.assertFalse(json.loads(out.getvalue())['execute'])

    def test_binding_tamper_blocks_claim(self):
        self.arm(); self.receiver()
        path = self.store / (c.PREFIX + '.json'); value = c.read_json(path)
        value['binding']['next_action_sha256'] = 'e'*64
        path.write_bytes(c.encoded(value))
        with self.assertRaisesRegex(c.GuardError, 'binding changed'):
            self.call('claim', {'selection': self.s})
        self.assertFalse(c.work_receipt(self.store, self.b).exists())


if __name__ == '__main__':
    unittest.main()
