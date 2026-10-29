import copy
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('routing_policy', ROOT / 'model-switcher/scripts/routing_policy.py')
policy = importlib.util.module_from_spec(spec); spec.loader.exec_module(policy)
NOW = dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc)


def request(kind='routine', difficulty='bounded', **task_changes):
    task = {'kind': kind, 'difficulty': difficulty, 'risk': 'low',
            'objective': 'Repair the bounded output', 'next_action': 'Edit only the selected file',
            'verification': 'Run the frozen acceptance command and inspect exact output',
            'permitted_files': ['selected.py'], 'permitted_actions': ['edit', 'test']}
    task.update(task_changes)
    return {'task': task, 'current_selection': {'model': policy.SOL, 'effort': 'xhigh'},
            'catalog': {'observed_at': NOW.isoformat(), 'data': [
                {'model': m, 'efforts': list(policy.EFFORTS if m != policy.LUNA else policy.EFFORTS[:-1])}
                for m in (policy.SOL, policy.ASTRA, policy.TERRA, policy.LUNA)]}}


class RoutingPolicy(unittest.TestCase):
    def run_policy(self, value):
        return policy.recommend(value, NOW)

    def test_easy_and_bounded_routine_use_economical_models(self):
        self.assertEqual(self.run_policy(request(difficulty='simple'))['assignment']['model'], policy.LUNA)
        self.assertEqual(self.run_policy(request())['assignment']['effort'], 'medium')

    def test_bounded_code_uses_sol_medium(self):
        result = self.run_policy(request('coding'))
        self.assertEqual((result['assignment']['model'], result['assignment']['effort']), (policy.SOL, 'medium'))
        self.assertTrue(result['transition_required'])
        self.assertTrue(result['checkpoint_required'])

    def test_bounded_visual_work_uses_terra(self):
        self.assertEqual(self.run_policy(request('visual'))['assignment']['model'], policy.TERRA)

    def test_hard_and_high_risk_work_use_stronger_assignment(self):
        for value in [request('analysis', 'hard'), request('coding', risk='high'), request('coding', failed_checks=1)]:
            result = self.run_policy(value)
            self.assertEqual((result['assignment']['model'], result['assignment']['effort']), (policy.ASTRA, 'xhigh'))
            self.assertEqual(result['review_assignment']['model'], policy.ASTRA)

    def test_hardest_serial_does_not_delegate(self):
        result = self.run_policy(request('analysis', 'hardest', delegation_allowed=False, independent_parts=3))
        self.assertEqual(result['assignment']['effort'], 'max')

    def test_ultra_needs_both_permission_and_separable_work(self):
        self.assertEqual(self.run_policy(request('analysis', 'hardest', delegation_allowed=True, independent_parts=3))['assignment']['effort'], 'ultra')
        self.assertNotEqual(self.run_policy(request('analysis', 'hardest', delegation_allowed=True, independent_parts=1))['assignment']['effort'], 'ultra')
        value = request(); value['explicit_selection'] = {'model': policy.ASTRA, 'effort': 'ultra'}
        with self.assertRaisesRegex(ValueError, 'Ultra'): self.run_policy(value)

    def test_explicit_choice_and_effort_only_choice_are_preserved(self):
        value = request('analysis', 'hardest')
        value['explicit_selection'] = {'model': policy.SOL, 'effort': 'medium'}
        self.assertEqual(self.run_policy(value)['assignment']['effort'], 'medium')
        value['explicit_selection'] = {'effort': 'high'}
        self.assertEqual(self.run_policy(value)['assignment']['model'], policy.SOL)

    def test_explicit_unsupported_choice_does_not_silently_fallback(self):
        value = request(); value['explicit_selection'] = {'model': policy.LUNA, 'effort': 'ultra'}
        with self.assertRaisesRegex(ValueError, 'unavailable'): self.run_policy(value)

    def test_opt_out_and_actual_stop_are_independent(self):
        value = request(); value['routing_opt_out'] = True
        self.assertEqual(self.run_policy(value)['assignment'], value['current_selection'])
        for key in ('stopped', 'provider_denied', 'at_limit'):
            stopped = copy.deepcopy(value); stopped[key] = True
            self.assertEqual(self.run_policy(stopped)['action'], 'handoff')

    def test_catalog_absence_never_forces_a_weaker_hard_assignment(self):
        value = request('analysis', 'hard')
        value['catalog']['data'] = [value['catalog']['data'][-1]]
        result = self.run_policy(value)
        self.assertEqual(result['action'], 'manual_handoff')
        self.assertEqual(result['handoff']['verification'], value['task']['verification'])

    def test_live_catalog_limits_efforts_and_specialist_fallback(self):
        value = request('visual'); value['catalog']['data'] = [value['catalog']['data'][0]]
        self.assertEqual(self.run_policy(value)['assignment']['model'], policy.SOL)
        value['catalog']['data'][0]['efforts'] = ['low']
        self.assertEqual(self.run_policy(value)['action'], 'manual_handoff')

    def test_stale_future_and_ambiguous_catalogs_rejected(self):
        for stamp in ('2000-01-01T00:00:00+00:00', '2100-01-01T00:00:00+00:00'):
            value = request(); value['catalog']['observed_at'] = stamp
            with self.assertRaises(ValueError): self.run_policy(value)
        value = request(); value['catalog']['data'].append(value['catalog']['data'][0])
        with self.assertRaisesRegex(ValueError, 'Ambiguous'): self.run_policy(value)

    def test_noop_and_trivial_overhead_do_not_create_a_transition(self):
        value = request('coding'); value['current_selection']['effort'] = 'medium'
        self.assertFalse(self.run_policy(value)['transition_required'])
        value = request(difficulty='simple', trivial=True)
        self.assertEqual(self.run_policy(value)['action'], 'keep_current')
        self.assertFalse(self.run_policy(value)['checkpoint_required'])

    def test_handoff_preserves_exact_scope_action_and_acceptance(self):
        value = request('coding'); result = self.run_policy(value)
        for key in ('objective', 'next_action', 'verification', 'permitted_files', 'permitted_actions'):
            self.assertEqual(result['handoff'][key], value['task'][key])
        self.assertEqual(result['handoff']['model'], result['assignment']['model'])
        self.assertEqual(result['handoff']['effort'], result['assignment']['effort'])
        self.assertFalse(result['execution_authorized'])

    def test_missing_bounded_contract_and_boolean_counts_rejected(self):
        for key in ('objective', 'next_action', 'verification', 'permitted_files', 'permitted_actions'):
            value = request(); del value['task'][key]
            with self.assertRaises(ValueError): self.run_policy(value)
        for key in ('failed_checks', 'independent_parts'):
            value = request(); value['task'][key] = True
            with self.assertRaises(ValueError): self.run_policy(value)


if __name__ == '__main__':
    unittest.main()
