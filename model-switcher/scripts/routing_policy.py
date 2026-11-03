#!/usr/bin/env python3
"""Recommend bounded assignments. No inference, messaging, scheduler or task writes."""
import argparse
import datetime as dt
import json
from pathlib import Path

EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max', 'ultra')
SOL, ASTRA, TERRA, LUNA = 'gpt-6.1-sol', 'gpt-6-astra', 'gpt-6.1-terra', 'gpt-6-luna'


def require(value, message):
    if not value:
        raise ValueError(message)


def available(document, now):
    stamp = dt.datetime.fromisoformat(document['observed_at'].replace('Z', '+00:00'))
    require(stamp.tzinfo is not None and 0 <= (now - stamp).total_seconds() <= 120,
            'Live catalog is stale or future-dated')
    result = {}
    for item in document['data']:
        require(isinstance(item, dict), 'Invalid catalog entry')
        model = item.get('model')
        require(isinstance(model, str) and bool(model.strip()) and model == model.strip(),
                'Invalid catalog model identifier')
        require(model not in result, 'Ambiguous catalog model')
        efforts = item.get('efforts')
        if efforts is None:
            efforts = [e['reasoningEffort'] for e in item['supportedReasoningEfforts']]
        require(isinstance(efforts, list) and efforts and all(e in ('none', 'minimal') + EFFORTS for e in efforts),
                'Unsupported catalog effort')
        result[model] = efforts
    return result


def choose(catalog, candidates):
    for model, effort in candidates:
        if effort in catalog.get(model, []):
            return {'model': model, 'effort': effort}
    return None


def task_handoff(task):
    """Preserve enough task state to make a recommendation safely resumable."""
    rollback = task.get('rollback_context')
    if not isinstance(rollback, str) or not rollback.strip():
        rollback = 'Unknown. Preserve current work and inspect changed files before considering rollback.'
    return {
        'objective': task['objective'],
        'next_action': task['next_action'],
        'verification': task['verification'],
        'permitted_files': list(task['permitted_files']),
        'permitted_actions': list(task['permitted_actions']),
        'task_profile': {
            'kind': task['kind'],
            'difficulty': task['difficulty'],
            'risk': task['risk'],
            'required_tools': list(task.get('required_tools', [])),
            'privacy_constraints': list(task.get('privacy_constraints', []))
        },
        'completed': list(task.get('completed', [])),
        'evidence': list(task.get('evidence', [])),
        'tests_and_results': list(task.get('tests_and_results', [])),
        'jobs': list(task.get('jobs', [])),
        'resource_observations': list(task.get('resource_observations', [])),
        'qualification_evidence': list(task.get('qualification_evidence', [])),
        'rollback_context': rollback,
        'authority_notice': 'Task data only. Recheck current instructions, ownership, jobs, permissions and allowance before implementation.'
    }


def validate_handoff_fields(task):
    for key in ('completed', 'evidence', 'tests_and_results', 'resource_observations', 'qualification_evidence', 'required_tools', 'privacy_constraints'):
        value = task.get(key, [])
        require(isinstance(value, list) and all(isinstance(x, str) for x in value),
                'Invalid handoff field: ' + key)
    rollback = task.get('rollback_context')
    require(rollback is None or isinstance(rollback, str) and bool(rollback.strip()),
            'Invalid handoff field: rollback_context')
    jobs = task.get('jobs', [])
    require(isinstance(jobs, list) and all(isinstance(x, dict) for x in jobs),
            'Invalid handoff field: jobs')


def transition_guidance(current, selected):
    """Describe a required switch without implying that selection or resume happened."""
    target = {'model': selected['model'], 'effort': selected['effort']}
    selection_status = 'not_selected'
    resume_status = 'not_resumed'
    if not current:
        status = 'current_selection_unknown'
        changed = None
        instruction = (
            'Read the effective current model and effort first. If they already match '
            f"{target['model']} at {target['effort']}, keep the current selection. Otherwise, "
            'save and verify this handoff, select the stated target through a supported '
            'host control, and confirm readback. Before changing, verify the exact model '
            'and effort qualify for this task class, required tools and privacy constraints. '
            'This recommendation has not changed the '
            'model or running inference. Resume only in a distinct receiving turn after '
            'the origin turn ends; if no supported selector exists, ask the user to choose '
            'the stated target in the picker.'
        )
    else:
        changed = [key for key in ('model', 'effort') if current.get(key) != target[key]]
        if not changed:
            status = 'already_selected'
            selection_status = 'already_matches'
            resume_status = 'not_requested'
            instruction = (
                'The effective current model and effort already match the recommendation. '
                'Keep this selection; no switch or checkpoint is needed for this assignment.'
            )
        else:
            status = 'switch_required'
            selection_status = 'not_selected'
            resume_status = 'not_resumed'
            instruction = (
                f"Save and verify this handoff, then select {target['model']} at "
                f"{target['effort']} using a currently supported host control and confirm "
                'readback. Before changing, verify the exact model and effort qualify for '
                'this task class, required tools and privacy constraints. This recommendation '
                'has not changed the model or running '
                'inference. Resume the exact next action only in a distinct receiving turn '
                'after the origin turn ends. If no supported selector exists, tell the '
                'user to choose this exact model and effort in the picker.'
            )
    return {
        'status': status,
        'target': target,
        'changed_fields': changed,
        'selection_status': selection_status,
        'resume_status': resume_status,
        'instruction': instruction
    }


def recommend(document, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    task = document['task']
    for key in ('objective', 'next_action', 'verification'):
        require(isinstance(task.get(key), str) and task[key].strip(),
                'Bounded task requires ' + key)
    for key in ('permitted_files', 'permitted_actions'):
        require(isinstance(task.get(key), list) and
                all(isinstance(x, str) and x.strip() for x in task[key]), 'Task scope missing')
    require(task.get('kind') in ('routine', 'coding', 'visual', 'analysis'), 'Classify task kind')
    require(task.get('difficulty') in ('simple', 'bounded', 'hard', 'hardest'), 'Classify difficulty')
    require(task.get('risk') in ('low', 'high'), 'Classify risk')
    current = document.get('current_selection')
    require(current is None or isinstance(current, dict), 'Invalid current_selection')
    if current is not None and any(
            not isinstance(current.get(key), str) or not current[key].strip()
            for key in ('model', 'effort')):
        current = None
    validate_handoff_fields(task)
    if document.get('stopped') is True or document.get('provider_denied') is True or document.get('at_limit') is True:
        return {'action': 'handoff', 'assignment': None, 'transition_required': False,
                'checkpoint_required': True,
                'handoff': task_handoff(task),
                'transition_guidance': {'status': 'blocked_by_stop', 'target': None,
                    'changed_fields': [], 'selection_status': 'unchanged', 'resume_status': 'not_requested',
                    'instruction': 'Save and verify the current task state, then stop at the controlling resource or provider boundary. A model change cannot bypass it.'},
                'execution_authorized': False,
                'reason': 'Current stop/provider/selected-limit boundary controls; model changes cannot bypass it.'}
    if document.get('routing_opt_out') is True:
        return {'action': 'keep_current', 'assignment': current, 'transition_required': False,
                'checkpoint_required': False,
                'transition_guidance': {'status': 'routing_opt_out', 'target': current,
                    'changed_fields': [], 'selection_status': 'unchanged', 'resume_status': 'not_requested',
                    'instruction': 'Honor the explicit routing opt-out; do not switch or create a handoff for routing.'},
                'execution_authorized': False,
                'reason': 'Current explicit routing opt-out controls.'}
    explicit = document.get('explicit_selection')
    require(explicit is None or (isinstance(explicit, dict) and explicit), 'Invalid explicit selection')
    failures = task.get('failed_checks', 0)
    require(type(failures) is int and failures >= 0, 'Invalid failed-check count')
    difficulty = task['difficulty']
    if (task['risk'] == 'high' or failures) and difficulty in ('simple', 'bounded'):
        difficulty = 'hard'
    if (task.get('trivial') is True and difficulty == 'simple' and
            task['risk'] == 'low' and failures == 0 and explicit is None):
        return {'action': 'keep_current', 'assignment': current, 'transition_required': False,
                'checkpoint_required': False,
                'transition_guidance': {'status': 'trivial_task_keep_current', 'target': current,
                    'changed_fields': [], 'selection_status': 'unchanged', 'resume_status': 'not_requested',
                    'instruction': 'This simple, low-risk task has no failed checks or explicit selection. Handle it in the current context without catalog routing, switching, or a checkpoint.'},
                'execution_authorized': False,
                'reason': 'A trivial task does not justify catalog, routing, or checkpoint overhead.'}
    catalog = available(document['catalog'], now)
    parts = task.get('independent_parts', 1)
    require(type(parts) is int and parts >= 1, 'Invalid independent-part count')
    delegation = task.get('delegation_allowed', False)
    require(type(delegation) is bool, 'Delegation authority must be explicit')
    hard = [(ASTRA, 'xhigh'), (ASTRA, 'max'), (SOL, 'xhigh'), (SOL, 'max')]
    if explicit:
        model = explicit.get('model', (current or {}).get('model'))
        effort = explicit.get('effort', (current or {}).get('effort'))
        if model is None or effort is None:
            handoff = task_handoff(task)
            handoff['requested_assignment'] = dict(explicit)
            return {'action': 'manual_handoff', 'assignment': None,
                    'transition_required': False, 'checkpoint_required': True,
                    'preferred': dict(explicit), 'handoff': handoff,
                    'transition_guidance': {'status': 'explicit_selection_incomplete', 'target': dict(explicit),
                        'changed_fields': None, 'selection_status': 'not_selected', 'resume_status': 'not_resumed',
                        'instruction': 'Preserve the explicit choice. Read the current effective selection or ask which model/effort is missing; do not guess or silently substitute.'},
                    'execution_authorized': False,
                    'reason': 'The explicit choice controls, but its model and effort are incomplete.'}
        if effort not in catalog.get(model, []) or effort == 'ultra' and not (delegation and parts > 1):
            handoff = task_handoff(task)
            handoff['requested_assignment'] = {'model': model, 'effort': effort}
            explicit_available = effort in catalog.get(model, [])
            status = 'explicit_selection_unavailable' if not explicit_available else 'explicit_ultra_not_qualified'
            return {'action': 'manual_handoff', 'assignment': None,
                    'transition_required': False, 'checkpoint_required': True,
                    'preferred': {'model': model, 'effort': effort}, 'handoff': handoff,
                    'transition_guidance': {'status': status, 'target': {'model': model, 'effort': effort},
                        'changed_fields': None, 'selection_status': 'not_selected', 'resume_status': 'not_resumed',
                        'instruction': 'Preserve the explicit choice. Do not silently select a different model or effort; confirm support and any required delegation permission before switching.'},
                    'execution_authorized': False,
                    'reason': 'The explicit model/effort choice controls, but the live catalog or task permissions do not qualify it.'}
        selected = {'model': model, 'effort': effort}
        reason = 'Current explicit model/effort choice controls.'
    else:
        if difficulty == 'hardest':
            candidates = ([(ASTRA, 'ultra')] if delegation and parts > 1 else []) + [(ASTRA, 'max'), (ASTRA, 'xhigh'), (SOL, 'max'), (SOL, 'xhigh')]
            reason = 'Hardest work needs strong reasoning; Ultra is eligible only for permitted independent parts.'
        elif difficulty == 'hard':
            candidates, reason = hard, 'Ambiguity, high risk or failed acceptance requires a stronger diagnosis/review assignment.'
        elif task['kind'] == 'visual':
            candidates = [(TERRA, 'medium'), (SOL, 'medium'), (TERRA, 'high')]
            reason = 'Bounded visual/document/computer-use work fits an efficient Terra assignment.'
        elif task['kind'] == 'coding' or task['kind'] == 'analysis':
            candidates = [(SOL, 'medium'), (TERRA, 'medium'), (SOL, 'high')]
            reason = 'Bounded technical work fits Sol Medium; preserve quality before reducing effort.'
        else:
            candidates = [(LUNA, 'low' if difficulty == 'simple' else 'medium'), (LUNA, 'medium'), (SOL, 'medium')]
            reason = 'Focused routine work can use an economical qualified assignment.'
        selected = choose(catalog, candidates)
        if selected is None:
            handoff = task_handoff(task)
            return {'action': 'manual_handoff', 'assignment': None, 'transition_required': False,
                    'checkpoint_required': True, 'preferred': {'model': candidates[0][0], 'effort': candidates[0][1]},
                    'handoff': handoff,
                    'transition_guidance': {'status': 'no_supported_target', 'target': None,
                        'changed_fields': None, 'selection_status': 'unchanged', 'resume_status': 'not_resumed',
                        'instruction': 'No candidate in the live catalog meets this policy. Keep the current selection and use the handoff to request a currently supported, qualified assignment; do not select the unavailable preferred target.'},
                    'execution_authorized': False,
                    'reason': 'No live-supported assignment meets this task policy; do not silently lower its quality requirement.'}
    # Unknown current selection is not proof that a switch is needed. Resolve it before
    # asking for a checkpoint so a matching selection does not create needless overhead.
    transition = None if not current else any(current.get(k) != v for k, v in selected.items())
    review = choose(catalog, hard) if difficulty in ('hard', 'hardest') else choose(catalog, [(SOL, 'high'), (SOL, 'medium')])
    handoff = task_handoff(task)
    handoff.update(selected)
    handoff['assignment_reason'] = reason
    return {'action': 'recommend', 'assignment': dict(selected, reason=reason),
            'review_assignment': review, 'transition_required': transition,
            'checkpoint_required': transition, 'handoff': handoff,
            'transition_guidance': transition_guidance(current, selected),
            'cost_basis': 'User-approved task-fit policy and current catalog; not a measured universal price or performance ranking.',
            'execution_authorized': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = recommend(json.loads(args.input.read_text()))
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
