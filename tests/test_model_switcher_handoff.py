import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'model-switcher' / 'scripts'))
import routing_policy

NOW = dt.datetime.fromisoformat('2026-11-02T20:00:00+00:00')
SOL = 'gpt-6.1-sol'
ASTRA = 'gpt-6-astra'
LUNA = 'gpt-6-luna'


def fixture(task=None, current=None, catalog=None, **extra):
    base_task = {
        'kind': 'routine',
        'difficulty': 'simple',
        'risk': 'low',
        'objective': 'Complete the bounded work package.',
        'next_action': 'Edit the named file and inspect the result.',
        'verification': 'Run the focused acceptance check.',
        'permitted_files': ['src/example.py'],
        'permitted_actions': ['edit src/example.py', 'run focused check'],
        'required_tools': ['filesystem', 'shell'],
        'privacy_constraints': ['local-only'],
        'completed': ['Inspection complete.'],
        'evidence': ['Current diff has no edits.'],
        'tests_and_results': ['Not run yet.'],
        'jobs': [{'id': 'focused-check-1', 'kind': 'test', 'status': 'completed'}],
        'resource_observations': ['Weekly included allowance is recorded separately.'],
        'qualification_evidence': ['Fresh catalog supports target effort; caller checks task/tools/privacy fit.'],
        'rollback_context': 'No source edits yet; preserve current worktree.'
    }
    base_task.update(task or {})
    default_catalog = [
        {'model': LUNA, 'efforts': ['low', 'medium']},
        {'model': SOL, 'efforts': ['low', 'medium', 'high', 'xhigh', 'max']},
        {'model': ASTRA, 'efforts': ['medium', 'high', 'xhigh', 'max']}
    ]
    return {
        'catalog': {'observed_at': NOW.isoformat(), 'data': catalog or default_catalog},
        'task': base_task,
        'current_selection': current,
        **extra
    }


class RoutingPolicyTests(unittest.TestCase):
    def test_simple_routine_recommends_economical_route_with_ready_switch_handoff(self):
        result = routing_policy.recommend(fixture(current={'model': SOL, 'effort': 'medium'}), NOW)
        self.assertEqual(result['assignment']['model'], LUNA)
        self.assertEqual(result['assignment']['effort'], 'low')
        self.assertTrue(result['checkpoint_required'])
        self.assertEqual(result['transition_guidance']['status'], 'switch_required')
        self.assertEqual(result['transition_guidance']['target'], {'model': LUNA, 'effort': 'low'})
        self.assertEqual(result['transition_guidance']['selection_status'], 'not_selected')
        self.assertEqual(result['transition_guidance']['resume_status'], 'not_resumed')
        self.assertIn(LUNA, result['transition_guidance']['instruction'])
        self.assertIn('low', result['transition_guidance']['instruction'])
        self.assertEqual(result['handoff']['completed'], ['Inspection complete.'])
        self.assertEqual(result['handoff']['evidence'], ['Current diff has no edits.'])
        self.assertEqual(result['handoff']['tests_and_results'], ['Not run yet.'])
        self.assertEqual(result['handoff']['jobs'], [{'id': 'focused-check-1', 'kind': 'test', 'status': 'completed'}])
        self.assertEqual(result['handoff']['qualification_evidence'], ['Fresh catalog supports target effort; caller checks task/tools/privacy fit.'])
        self.assertEqual(result['handoff']['rollback_context'], 'No source edits yet; preserve current worktree.')
        self.assertEqual(result['handoff']['permitted_files'], ['src/example.py'])
        self.assertEqual(result['handoff']['task_profile']['kind'], 'routine')
        self.assertEqual(result['handoff']['task_profile']['required_tools'], ['filesystem', 'shell'])
        self.assertEqual(result['handoff']['task_profile']['privacy_constraints'], ['local-only'])
        self.assertFalse(result['execution_authorized'])

    def test_same_assignment_avoids_unneeded_switch_and_checkpoint(self):
        result = routing_policy.recommend(fixture(
            task={'kind': 'coding', 'difficulty': 'bounded'},
            current={'model': SOL, 'effort': 'medium'}), NOW)
        self.assertEqual(result['assignment']['model'], SOL)
        self.assertFalse(result['transition_required'])
        self.assertFalse(result['checkpoint_required'])
        self.assertEqual(result['transition_guidance']['status'], 'already_selected')
        self.assertEqual(result['transition_guidance']['selection_status'], 'already_matches')
        self.assertIn('no switch', result['transition_guidance']['instruction'])

    def test_failed_acceptance_escalates_and_preserves_evidence_and_rollback(self):
        task = {
            'kind': 'coding', 'difficulty': 'bounded', 'failed_checks': 1,
            'evidence': ['Duplicate-event acceptance failed once.'],
            'tests_and_results': ['duplicate_event: failed'],
            'rollback_context': 'Keep parser diff; revert only the idempotency branch if reviewed.'
        }
        result = routing_policy.recommend(fixture(task=task, current={'model': SOL, 'effort': 'medium'}), NOW)
        self.assertEqual(result['assignment']['model'], ASTRA)
        self.assertEqual(result['assignment']['effort'], 'xhigh')
        self.assertEqual(result['transition_guidance']['status'], 'switch_required')
        self.assertEqual(result['handoff']['evidence'], task['evidence'])
        self.assertEqual(result['handoff']['tests_and_results'], task['tests_and_results'])
        self.assertEqual(result['handoff']['rollback_context'], task['rollback_context'])

    def test_unavailable_explicit_choice_is_preserved_without_claiming_switch(self):
        result = routing_policy.recommend(fixture(
            current={'model': SOL, 'effort': 'medium'},
            explicit_selection={'model': 'gpt-unknown', 'effort': 'high'}), NOW)
        self.assertEqual(result['action'], 'manual_handoff')
        self.assertIsNone(result['assignment'])
        self.assertEqual(result['preferred'], {'model': 'gpt-unknown', 'effort': 'high'})
        self.assertEqual(result['transition_guidance']['status'], 'explicit_selection_unavailable')
        self.assertEqual(result['transition_guidance']['selection_status'], 'not_selected')
        self.assertFalse(result['execution_authorized'])

    def test_stop_boundary_blocks_switch_recommendation(self):
        result = routing_policy.recommend(fixture(current={'model': SOL, 'effort': 'medium'}, at_limit=True), NOW)
        self.assertEqual(result['action'], 'handoff')
        self.assertIsNone(result['assignment'])
        self.assertEqual(result['transition_guidance']['status'], 'blocked_by_stop')
        self.assertEqual(result['transition_guidance']['selection_status'], 'unchanged')
        self.assertEqual(result['transition_guidance']['resume_status'], 'not_requested')
        self.assertIn('rollback_context', result['handoff'])
        self.assertFalse(result['execution_authorized'])

    def test_unknown_current_selection_requires_readback_before_switching(self):
        result = routing_policy.recommend(fixture(current=None), NOW)
        self.assertIsNone(result['transition_required'])
        self.assertIsNone(result['checkpoint_required'])
        self.assertEqual(result['transition_guidance']['status'], 'current_selection_unknown')
        self.assertIn('Read the effective current model and effort first', result['transition_guidance']['instruction'])
        self.assertEqual(result['transition_guidance']['selection_status'], 'not_selected')

    def test_missing_rollback_context_is_explicitly_unknown(self):
        result = routing_policy.recommend(fixture(
            task={'rollback_context': None}, current={'model': SOL, 'effort': 'medium'}), NOW)
        self.assertEqual(result['handoff']['rollback_context'],
                         'Unknown. Preserve current work and inspect changed files before considering rollback.')

    def test_unavailable_target_is_never_suggested_as_a_switch(self):
        result = routing_policy.recommend(fixture(
            task={'difficulty': 'hard'},
            current={'model': SOL, 'effort': 'medium'},
            catalog=[{'model': SOL, 'efforts': ['medium']}]), NOW)
        self.assertEqual(result['action'], 'manual_handoff')
        self.assertIsNone(result['assignment'])
        self.assertEqual(result['preferred'], {'model': ASTRA, 'effort': 'xhigh'})
        self.assertEqual(result['transition_guidance']['status'], 'no_supported_target')
        self.assertIsNone(result['transition_guidance']['target'])
        self.assertFalse(result['execution_authorized'])


if __name__ == '__main__':
    unittest.main()
