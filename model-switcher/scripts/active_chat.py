#!/usr/bin/env python3
"""Guard native same-chat selection requests and inspect selection metadata.

This helper never sends chat messages or starts/resumes a model turn. Authorization,
catalog and resource fields are fresh operator attestations, not recovered permissions.
The caller owns checkpointing, the task lease and durable intent/outcome recording.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import queue
import re
import stat
import subprocess
import sys
import threading
import time


class GuardError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GuardError(message)


def token(value, label, maximum=128):
    require(isinstance(value, str) and 0 < len(value) <= maximum
            and re.fullmatch(r'[A-Za-z0-9_.:-]+', value), 'Invalid ' + label)
    return value


def timestamp(value):
    require(isinstance(value, str), 'Timestamp is unknown')
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise GuardError('Invalid timestamp')
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None,
            'Timezone-aware timestamp required')
    return parsed


def fresh(value, now):
    age = (now - timestamp(value)).total_seconds()
    require(0 <= age <= 120, 'Observation is stale or future-dated')


def object_field(context, field):
    value = context.get(field)
    require(isinstance(value, dict), field + ' is unknown or invalid')
    return value


def plan(context, now=None):
    """Return native tool arguments only after all declared guards pass."""
    require(isinstance(context, dict), 'Context must be an object')
    now = now or dt.datetime.now(dt.timezone.utc)
    chat = token(context.get('chat_id'), 'chat id')
    require(chat == context.get('current_chat_id'), 'Target is not the current chat')
    require(context.get('host_id') == 'local', 'Only the verified local host is supported')
    operation = token(context.get('operation_id'), 'operation id', 80)
    model = token(context.get('target_model'), 'model')
    effort = token(context.get('target_effort'), 'effort', 20)
    require(effort in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'),
            'Effort is not supported by the native tool')
    auth = object_field(context, 'authorization')
    require(auth.get('confirmed') is True and isinstance(auth.get('source'), str)
            and bool(auth['source'].strip()), 'Current human authorization is required')
    resources = object_field(context, 'resources')
    fresh(resources.get('observed_at'), now)
    require(resources.get('ordinary_usage_allowed') is True and resources.get('reserve_ok') is True,
            'Resource stop or unknown resource sufficiency')
    pending = context.get('pending_operations')
    require(isinstance(pending, list), 'Pending-operation state is unknown')
    require(not pending, 'An active or uncertain selection operation blocks another request')
    catalog = object_field(context, 'catalog')
    fresh(catalog.get('observed_at'), now)
    models = catalog.get('data')
    require(isinstance(models, list), 'Model catalog is unknown')
    matches = [item for item in models if isinstance(item, dict) and item.get('model') == model]
    require(len(matches) == 1, 'Target model is unavailable or ambiguous')
    efforts = matches[0].get('efforts')
    require(isinstance(efforts, list) and effort in efforts, 'Target effort is unavailable')
    expected = {'chat_id': chat, 'model': model, 'effort': effort}
    result = {'action': 'native_request', 'operation_id': operation, 'expected': expected,
              'claim_scope': 'configured_for_subsequent_turns', 'execution_confirmed': False}
    current = context.get('current_selection')
    if isinstance(current, dict) and current.get('model') == model and current.get('effort') == effort:
        return dict(result, action='no_op')
    prompt = ('Model Switcher configuration cue, operation ' + operation + '. '
              'Select ' + model + ' with ' + effort + ' reasoning for subsequent turns '
              'of this same chat. Keep the current task and authority intact. Do not '
              'restart or duplicate work, repost this cue, create a worker, or claim '
              'that in-flight inference changed. The coordinator must verify host readback.')
    result['tool'] = 'mcp__codex_app__send_message_to_thread'
    result['arguments'] = {'threadId': chat, 'hostId': 'local', 'model': model,
                           'thinking': effort, 'prompt': prompt}
    return result


def verify(request, readback, now=None):
    """Confirm only configured/persisted selection, never per-turn execution."""
    require(isinstance(request, dict) and request.get('action') in ('native_request', 'no_op'),
            'Invalid prepared request')
    expected = object_field(request, 'expected')
    require(set(expected) == {'chat_id', 'model', 'effort'}, 'Invalid expected selection')
    for label, value in expected.items():
        token(value, label)
    require(isinstance(readback, dict)
            and readback.get('source') == 'codex-app-server-thread-read',
            'Trusted host readback source is required')
    fresh(readback.get('observed_at'), now or dt.datetime.now(dt.timezone.utc))
    thread = object_field(readback, 'thread')
    require(thread.get('id') == expected['chat_id'], 'Readback belongs to another chat')
    require(thread.get('model') == expected['model']
            and thread.get('reasoningEffort') == expected['effort'], 'Selection readback mismatch')
    status = thread.get('status')
    require(isinstance(status, dict), 'Thread loading state is unknown')
    kind = status.get('type')
    require(kind in ('notLoaded', 'active', 'idle', 'loaded', 'systemError'),
            'Thread loading state is unknown')
    return {'selection_confirmed': True, 'execution_confirmed': False,
            'claim_scope': 'configured_for_subsequent_turns',
            'metadata_scope': 'latest_persisted' if kind == 'notLoaded' else 'current_configured',
            'expected': expected}


def inspect_selection(chat_id, executable='codex', timeout=20):
    """Use only initialize + thread/read on a separate read-only app-server connection."""
    token(chat_id, 'chat id')
    require(isinstance(timeout, (int, float)) and not isinstance(timeout, bool)
            and 1 <= timeout <= 60, 'Probe timeout must be 1–60 seconds')
    process = subprocess.Popen([executable, 'app-server', '--stdio'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    messages = queue.Queue()
    def receive():
        try:
            for line in process.stdout:
                try:
                    messages.put(json.loads(line))
                except ValueError:
                    continue
        except (OSError, ValueError):
            pass
        finally:
            messages.put(None)
    threading.Thread(target=receive, daemon=True).start()
    deadline = time.monotonic() + timeout
    def send(message):
        process.stdin.write(json.dumps(message) + '\n')
        process.stdin.flush()
    def request(ident, method, params):
        send({'id': ident, 'method': method, 'params': params})
        while time.monotonic() < deadline:
            try:
                value = messages.get(timeout=max(.01, deadline - time.monotonic()))
            except queue.Empty:
                break
            require(value is not None, 'Read-only metadata probe exited before reply')
            if value.get('id') == ident:
                require('error' not in value and isinstance(value.get('result'), dict),
                        'Read-only metadata method unavailable')
                return value['result']
        raise GuardError('Read-only metadata probe timed out')
    try:
        request(1, 'initialize', {'clientInfo': {'name': 'model_switcher_selection_probe',
                                               'version': '0.2.0'}})
        send({'method': 'initialized', 'params': {}})
        data = request(2, 'thread/read', {'threadId': chat_id, 'includeTurns': False})
        thread = object_field(data, 'thread')
        require(thread.get('id') == chat_id, 'Probe returned another chat')
        return {'source': 'codex-app-server-thread-read',
                'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'thread': {key: thread.get(key) for key in
                           ('id', 'model', 'reasoningEffort', 'modelProvider', 'status')}}
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
        process.stdin.close()
        process.stdout.close()


def read_json(path):
    path = Path(path)
    require(not path.is_symlink() and stat.S_ISREG(path.stat().st_mode),
            'JSON input must be a regular file')
    require(path.stat().st_size <= 1024 * 1024, 'JSON input exceeds 1 MiB')
    return json.loads(path.read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('plan'); prepare.add_argument('--input', type=Path, required=True)
    check = commands.add_parser('verify')
    check.add_argument('--request', type=Path, required=True)
    check.add_argument('--readback', type=Path, required=True)
    probe = commands.add_parser('inspect'); probe.add_argument('--chat-id', required=True)
    probe.add_argument('--timeout', type=float, default=20); probe.add_argument('--codex', default='codex')
    args = parser.parse_args(argv)
    try:
        if args.command == 'plan':
            result = plan(read_json(args.input))
        elif args.command == 'verify':
            result = verify(read_json(args.request), read_json(args.readback))
        else:
            result = inspect_selection(args.chat_id, args.codex, args.timeout)
        print(json.dumps(result, indent=2))
        return 0
    except (GuardError, OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'status': 'blocked', 'reason': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
