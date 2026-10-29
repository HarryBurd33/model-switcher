#!/usr/bin/env python3
"""Cooperative one-use continuation ledger in an EXISTING checkpoint store.

No scheduler, messaging, inference, ownership acquisition or task execution occurs.
All host/authority/resource/lineage fields are operator attestations, not security
proofs. This guard never attests the executing model. Missing/uncertain receipts
must be reconciled; never remove a lock or spent marker to retry an operation.
"""
import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid

PREFIX = 'model-switcher-continuation'
LIMIT = 1024 * 1024
TERMINAL = {'completed', 'cancelled'}


class GuardError(ValueError):
    pass


def require(value, message):
    if not value:
        raise GuardError(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def token(value, label):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', value),
            'Invalid ' + label)
    return value


def sha(value):
    require(isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value), 'Invalid digest')
    return value


def obj(value, label):
    require(isinstance(value, dict), 'Missing or invalid ' + label)
    return value


def timestamp(value):
    require(isinstance(value, str), 'Missing timestamp')
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise GuardError('Invalid timestamp')
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None, 'Naive timestamp')
    return parsed


def fresh(value, now):
    require(0 <= (now - timestamp(value)).total_seconds() <= 120,
            'Evidence is stale or future-dated')


def checkpoint(value):
    obj(value, 'checkpoint')
    require(set(value) == {'id', 'manifest_sha256'}, 'Invalid checkpoint binding')
    token(value['id'], 'checkpoint id'); sha(value['manifest_sha256'])


def binding(value, now):
    obj(value, 'binding')
    keys = {'operation_id', 'chat_id', 'task_id', 'host_id', 'base_checkpoint',
            'source_fingerprint', 'next_action_sha256', 'origin_turn_id', 'target',
            'lease', 'authorization_scope_sha256', 'expires_at'}
    require(set(value) == keys, 'Unexpected or missing binding fields')
    for key in ('operation_id', 'chat_id', 'task_id', 'origin_turn_id'):
        token(value[key], key)
    require(value['host_id'] == 'local', 'Only the reviewed local host is supported')
    checkpoint(value['base_checkpoint'])
    for key in ('source_fingerprint', 'next_action_sha256', 'authorization_scope_sha256'):
        sha(value[key])
    target = obj(value['target'], 'target')
    require(set(target) == {'model', 'effort'}, 'Invalid target selection')
    token(target['model'], 'model'); token(target['effort'], 'effort')
    require(target['effort'] in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'),
            'Invalid target effort')
    lease = obj(value['lease'], 'lease')
    require(set(lease) == {'owner', 'token'}, 'Invalid lease binding')
    token(lease['owner'], 'lease owner'); token(lease['token'], 'lease token')
    require(0 < (timestamp(value['expires_at']) - now).total_seconds() <= 3600,
            'Intent lifetime must be positive and at most one hour')
    return json.loads(encoded(value))


def control(b, evidence, now):
    e = obj(evidence, 'evidence'); fresh(e.get('observed_at'), now)
    require(isinstance(e.get('source'), str) and bool(e['source'].strip()),
            'Current evidence source is required')
    require(e.get('chat_id') == b['chat_id'] and e.get('task_id') == b['task_id']
            and e.get('host_id') == b['host_id'], 'Wrong chat, task or host')
    lease = obj(e.get('lease'), 'current lease')
    require(lease.get('verified') is True and all(lease.get(k) == v for k, v in b['lease'].items()),
            'Current retained task lease does not match')
    return e


def context(b, evidence, now, receiver=False):
    """Pure gate. Checkpoint lineage and host observations are cooperative evidence."""
    e = control(b, evidence, now)
    require(now < timestamp(b['expires_at']), 'Continuation intent expired')
    require(e.get('base_checkpoint') == b['base_checkpoint'], 'Base checkpoint changed')
    checkpoint(e.get('current_checkpoint'))
    require(e['current_checkpoint'] == b['base_checkpoint'] or
            (e.get('lineage_verified') is True and e.get('context_unchanged') is True),
            'Latest checkpoint lineage is unverified')
    require(e.get('context_unchanged') is True and
            all(e.get(k) == b[k] for k in ('source_fingerprint', 'next_action_sha256')),
            'Source or next action changed')
    auth = obj(e.get('authorization'), 'current authorization')
    require(auth.get('confirmed') is True and auth.get('continuation_allowed') is True
            and auth.get('scope_sha256') == b['authorization_scope_sha256']
            and isinstance(auth.get('source'), str) and bool(auth['source'].strip()),
            'Current continuation authority is absent or changed')
    resources = obj(e.get('resources'), 'current resources')
    require(resources.get('adequate') is True and resources.get('reserve_ok') is True,
            'Resources are low or unknown')
    require(e.get('stopped') is False, 'Stop state is active or unknown')
    jobs = e.get('jobs')
    require(e.get('jobs_verified') is True and isinstance(jobs, list), 'Job inventory is unknown')
    ids = set()
    for job in jobs:
        obj(job, 'job'); ident = token(job.get('id'), 'job id')
        require(ident not in ids, 'Duplicate job identity'); ids.add(ident)
        require(ident == b['operation_id'] or job.get('status') in ('completed', 'failed', 'cancelled'),
                'Another job is active or uncertain')
    if receiver:
        require(e.get('origin_turn_id') == b['origin_turn_id']
                and e.get('origin_turn_status') == 'completed', 'Origin turn is not confirmed complete')
        current = token(e.get('current_turn_id'), 'current turn')
        require(current != b['origin_turn_id'], 'Steering is not a subsequent turn')
    return e


def selection(b, value, now):
    s = obj(value, 'selection readback'); fresh(s.get('observed_at'), now)
    require(s.get('confirmed') is True and s.get('chat_id') == b['chat_id']
            and all(s.get(k) == v for k, v in b['target'].items())
            and isinstance(s.get('source'), str) and bool(s['source'].strip()),
            'Fresh exact selection is not confirmed')


def scheduler(value, now):
    s = obj(value, 'scheduler receipt'); fresh(s.get('observed_at'), now)
    require(s.get('confirmed') is True and isinstance(s.get('source'), str)
            and bool(s['source'].strip()), 'Scheduler receipt is uncertain')
    return token(s.get('id'), 'scheduler id')


def read_json(path):
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(str(path), flags)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= LIMIT,
                'Input must be a bounded, unlinked regular file')
        require(not Path(path).is_symlink(), 'Linked input is unsupported')
        data = bytearray()
        while len(data) <= LIMIT:
            part = os.read(fd, min(65536, LIMIT + 1 - len(data)))
            if not part: break
            data.extend(part)
        require(len(data) <= LIMIT, 'Input exceeds bound')
        return json.loads(data)
    finally:
        os.close(fd)


def sync_dir(path):
    if os.name != 'nt':
        fd = os.open(str(path), os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)


def write_new(path, value):
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        view = memoryview(encoded(value))
        while view:
            n = os.write(fd, view); require(n > 0, 'Receipt write made no progress'); view = view[n:]
        os.fsync(fd)
    finally:
        os.close(fd)
    sync_dir(path.parent)


def save(path, value):
    # Failed pending files remain as evidence. Never remove a claim to recover.
    pending = path.parent / ('.' + PREFIX + '.pending-' + uuid.uuid4().hex)
    write_new(pending, value)
    os.replace(pending, path)
    sync_dir(path.parent)


@contextlib.contextmanager
def locked(store):
    store = Path(store)
    require(store.is_dir() and not store.is_symlink(), 'Existing checkpoint store required')
    info = store.stat()
    if hasattr(os, 'getuid'):
        require(info.st_uid == os.getuid() and not info.st_mode & 0o077,
                'Checkpoint store must be private and owned')
    lock = store / ('.' + PREFIX + '.lock')
    write_new(lock, {'pid': os.getpid(), 'cooperating_lock': True})
    try:
        yield store
    finally:
        lock.unlink(); sync_dir(store)


def receipt(store, operation, kind):
    token(operation, 'operation id')
    return store / (PREFIX + '.' + operation + '.' + kind + '.json')


def work_receipt(store, b):
    # Fence the work itself, not just an operation ID that a caller could change.
    work = {k: b[k] for k in ('task_id', 'chat_id', 'base_checkpoint',
                              'source_fingerprint', 'next_action_sha256')}
    return store / (PREFIX + '.work-' + digest(work) + '.claim.json')


def output(record, execute=False):
    b = record['binding']
    return {'operation_id': b['operation_id'], 'state': record['state'],
            'execute': execute, 'execution_model_confirmed': False,
            'selection_scope': 'configured_for_subsequent_turns',
            'next_action_sha256': b['next_action_sha256'],
            'scheduler_id': record.get('scheduler_id'),
            'scheduler_retired': record.get('scheduler_retired', False)}


def operate(command, store, document=None, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    document = {} if document is None else obj(document, 'document')
    with locked(store) as store:
        path = store / (PREFIX + '.json')
        require(not path.is_symlink(), 'Linked continuation state is unsupported')
        record = read_json(path) if path.exists() else None
        if command == 'prepare':
            b = binding(document.get('binding'), now)
            context(b, document.get('evidence'), now)
            require(not work_receipt(store, b).exists(), 'This checkpoint action is already spent or uncertain')
            if record:
                require(record['state'] in TERMINAL and record.get('scheduler_retired') is True,
                        'Earlier continuation is active, uncertain or not retired')
                final = receipt(store, record['binding']['operation_id'], 'final')
                if not final.exists(): write_new(final, record)
                else: require(read_json(final) == record, 'Final receipt changed')
            for old in store.glob(PREFIX + '.*.intent.json'):
                ident = old.name[len(PREFIX)+1:-len('.intent.json')]
                require(receipt(store, ident, 'final').exists(), 'Unresolved earlier intent receipt')
            record = {'version': 1, 'state': 'prepared', 'binding': b,
                      'binding_sha256': digest(b), 'created_at': now.isoformat(),
                      'scheduler_id': None, 'scheduler_retired': False}
            write_new(receipt(store, b['operation_id'], 'intent'), record)
            save(path, record)
            return output(record)
        require(record is not None, 'Continuation intent is missing; do not reconstruct it')
        b = record['binding']
        require(record.get('binding_sha256') == digest(b), 'Intent binding changed')
        original = read_json(receipt(store, b['operation_id'], 'intent'))
        require(original['binding'] == b and original['binding_sha256'] == digest(b),
                'Immutable intent does not match')
        if command == 'inspect':
            result = output(record)  # Observation NEVER returns an executable grant.
            result['reservation_present'] = work_receipt(store, b).exists()
            if record['state'] == 'armed' and result['reservation_present']:
                result['state'] = 'unknown'
            return result
        require(document.get('operation_id') == b['operation_id'], 'Wrong operation identity')
        evidence = document.get('evidence')
        if command == 'arm':
            require(record['state'] == 'prepared', 'Intent is not prepared')
            context(b, evidence, now); selection(b, document.get('selection'), now)
            record.update(state='armed', scheduler_id=scheduler(document.get('scheduler'), now),
                          armed_at=now.isoformat())
        elif command == 'claim':
            require(record['state'] == 'armed', 'Intent is not armed or already spent')
            context(b, evidence, now, receiver=True); selection(b, document.get('selection'), now)
            spent = work_receipt(store, b)
            claim = {'operation_id': b['operation_id'], 'binding_sha256': digest(b), 'turn_id': evidence['current_turn_id'],
                     'claimed_at': now.isoformat(), 'execute': False}
            write_new(spent, claim)  # Exclusive durable reservation BEFORE task action.
            record.update(state='claimed', claim=claim)
        elif command == 'retire':
            require(record['state'] in ('claimed', 'unknown', 'cancelled'), 'No pending retirement')
            control(b, evidence, now)
            r = obj(document.get('retirement'), 'retirement')
            fresh(r.get('observed_at'), now)
            confirmed = (r.get('confirmed') is True and r.get('id') == record['scheduler_id']
                         and r.get('status') in ('paused', 'deleted')
                         and isinstance(r.get('source'), str) and bool(r['source'].strip()))
            if not confirmed:
                if record['state'] != 'cancelled': record['state'] = 'unknown'
                record['retirement_uncertain'] = True
                save(path, record)
                return output(record)
            record['scheduler_retired'] = True
            record['retirement'] = r
            if record['state'] == 'claimed':
                try:
                    context(b, evidence, now, receiver=True)
                    selection(b, document.get('selection'), now)
                    require(evidence['current_turn_id'] == record['claim']['turn_id'],
                            'Claim belongs to another receiver turn')
                    require(read_json(work_receipt(store, b)) == record['claim'],
                            'Claim receipt changed')
                except (GuardError, OSError, ValueError, KeyError, TypeError):
                    record['state'] = 'unknown'; save(path, record); raise
                record['state'] = 'ready'
                record['ready_at'] = now.isoformat()
                save(path, record)
                return output(record, execute=True)  # Exactly one emission; inspect cannot replay it.
        elif command == 'complete':
            require(record['state'] in ('ready', 'unknown'), 'No claimed outcome to complete')
            control(b, evidence, now)
            require(record.get('scheduler_retired') is True, 'Scheduler retirement is unconfirmed')
            outcome = obj(document.get('outcome'), 'outcome')
            require(outcome.get('status') in ('completed', 'failed')
                    and outcome.get('effects_reconciled') is True
                    and isinstance(outcome.get('evidence'), str) and bool(outcome['evidence'].strip()),
                    'Actual task outcome and effect reconciliation are required')
            require(record['state'] == 'ready' or outcome['status'] == 'failed',
                    'Uncertain claim cannot be certified as executed')
            record.update(state='completed', outcome=outcome, completed_at=now.isoformat())
        elif command == 'cancel':
            require(record['state'] in ('prepared', 'armed'), 'Claimed work requires outcome reconciliation')
            control(b, evidence, now)
            require(isinstance(document.get('reason'), str) and bool(document['reason'].strip()),
                    'Cancellation reason required')
            if record['scheduler_id'] is None:
                require(document.get('scheduler_absent_confirmed') is True,
                        'Uncertain scheduler creation prevents cancellation certification')
                record['scheduler_retired'] = True
            record.update(state='cancelled', reason=document['reason'])
        else:
            raise GuardError('Unknown operation')
        save(path, record)
        return output(record)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['prepare', 'arm', 'claim', 'retire', 'complete', 'cancel', 'inspect'])
    p.add_argument('--store', required=True, type=Path)
    p.add_argument('--input', type=Path)
    args = p.parse_args(argv)
    try:
        require(args.command == 'inspect' or args.input is not None, 'Private input JSON required')
        result = operate(args.command, args.store, read_json(args.input) if args.input else None)
        print(json.dumps(result, sort_keys=True))
        return 2 if result['state'] == 'unknown' and args.command != 'inspect' else 0
    except (GuardError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'state': 'blocked-or-uncertain', 'execute': False,
                          'reason': str(error) if isinstance(error, GuardError) else 'Receipt or input failure'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
