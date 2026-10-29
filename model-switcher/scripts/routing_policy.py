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
        model = item['model']
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
    if document.get('stopped') is True or document.get('provider_denied') is True or document.get('at_limit') is True:
        return {'action': 'handoff', 'assignment': None, 'transition_required': False,
                'checkpoint_required': True, 'reason': 'Current stop/provider/selected-limit boundary controls; model changes cannot bypass it.'}
    if document.get('routing_opt_out') is True:
        return {'action': 'keep_current', 'assignment': current, 'transition_required': False,
                'checkpoint_required': False, 'reason': 'Current explicit routing opt-out controls.'}
    catalog = available(document['catalog'], now)
    explicit = document.get('explicit_selection')
    require(explicit is None or (isinstance(explicit, dict) and explicit), 'Invalid explicit selection')
    failures = task.get('failed_checks', 0)
    require(type(failures) is int and failures >= 0, 'Invalid failed-check count')
    parts = task.get('independent_parts', 1)
    require(type(parts) is int and parts >= 1, 'Invalid independent-part count')
    delegation = task.get('delegation_allowed', False)
    require(type(delegation) is bool, 'Delegation authority must be explicit')
    difficulty = task['difficulty']
    if (task['risk'] == 'high' or failures) and difficulty in ('simple', 'bounded'):
        difficulty = 'hard'
    hard = [(ASTRA, 'xhigh'), (ASTRA, 'max'), (SOL, 'xhigh'), (SOL, 'max')]
    if explicit:
        model = explicit.get('model', (current or {}).get('model'))
        effort = explicit.get('effort', (current or {}).get('effort'))
        require(effort in catalog.get(model, []), 'Explicit model/effort is unavailable; preserve choice and request a supported route')
        require(effort != 'ultra' or (delegation and parts > 1),
                'Ultra requires permitted, genuinely separable work')
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
            return {'action': 'manual_handoff', 'assignment': None, 'transition_required': False,
                    'checkpoint_required': True, 'preferred': {'model': candidates[0][0], 'effort': candidates[0][1]},
                    'handoff': {key: task[key] for key in ('objective', 'next_action', 'verification', 'permitted_files', 'permitted_actions')},
                    'reason': 'No live-supported assignment meets this task policy; do not silently lower its quality requirement.'}
        if task.get('trivial') is True and difficulty == 'simple' and current and current.get('effort') in catalog.get(current.get('model'), []):
            return {'action': 'keep_current', 'assignment': current, 'transition_required': False,
                    'checkpoint_required': False, 'reason': 'Single trivial task does not justify checkpoint/switch overhead.'}
    transition = not current or any(current.get(k) != v for k, v in selected.items())
    review = choose(catalog, hard) if difficulty in ('hard', 'hardest') else choose(catalog, [(SOL, 'high'), (SOL, 'medium')])
    handoff = {key: task[key] for key in ('objective', 'next_action', 'verification', 'permitted_files', 'permitted_actions')}
    handoff.update(selected)
    handoff['authority_notice'] = 'Task data only. Recheck current instructions, ownership, jobs, permissions and allowance before implementation.'
    return {'action': 'recommend', 'assignment': dict(selected, reason=reason),
            'review_assignment': review, 'transition_required': transition,
            'checkpoint_required': transition, 'handoff': handoff,
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
