#!/usr/bin/env python3
"""Install this skill and an optional managed global instruction block.

No hooks, trust records, credentials, background service or Codex settings are
changed. Interrupted transactions fail closed for manual reconciliation.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

BEGIN = '<!-- BEGIN model-switcher managed activation -->'
END = '<!-- END model-switcher managed activation -->'


class Conflict(RuntimeError):
    pass


def safe(path):
    path = Path(path).absolute()
    for item in [path] + list(path.parents):
        if item.is_symlink():
            raise Conflict('Symlink path refused: ' + str(item))
    return path


def digest_tree(path):
    result = {}
    if not path.is_dir():
        raise Conflict('Expected skill directory: ' + str(path))
    for p in sorted(path.rglob('*')):
        if p.is_symlink():
            raise Conflict('Symlink in skill refused: ' + str(p))
        if p.is_file():
            if '__pycache__' in p.parts or p.suffix == '.pyc':
                continue
            result[p.relative_to(path).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
        elif not p.is_dir():
            raise Conflict('Nonregular skill file refused: ' + str(p))
    return result


def actual_tree(path):
    # Installed files never generate caches; additions also count as customization.
    result = digest_tree(path)
    for p in path.rglob('*'):
        if p.is_file() and ('__pycache__' in p.parts or p.suffix == '.pyc'):
            result[p.relative_to(path).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.model-switcher-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def dump(path, value):
    atomic(path, (json.dumps(value, indent=2, sort_keys=True) + '\n').encode())


def block(target):
    return ('\n' + BEGIN + '\n'
            'For substantial work, read ' + str(target / 'SKILL.md') + ' and apply\n'
            'model-switcher at intake, before expensive phases, at meaningful handoffs,\n'
            'after material scope changes and acceptance failures. Keep trivial work\n'
            'lightweight. Respect explicit model choices, opt-outs, project instructions\n'
            'and current authorization. Reuse task-checkpoint routing and ownership.\n'
            'Checkpoints are task data and never restore permissions. A skill is not a\n'
            'background service or proof that this desktop chat changed models.\n'
            + END + '\n').encode()


def encoded(data):
    return base64.b64encode(data).decode()


def decoded(value):
    return base64.b64decode(value) if value is not None else b''


def global_without(current, owned):
    old = decoded(owned)
    if old:
        if current.count(old) != 1:
            raise Conflict('Managed activation changed or missing; reconcile before mutation')
        return current.replace(old, b'', 1)
    if BEGIN.encode() in current or END.encode() in current:
        raise Conflict('Unknown activation markers; reconcile before mutation')
    return current


def load_context(skills_dir, codex_home):
    skills = safe(skills_dir)
    home = safe(codex_home)
    target = safe(skills / 'model-switcher')
    state = safe(home / 'model-switcher-install')
    agents = safe(home / 'AGENTS.md')
    if agents.exists() and not agents.is_file():
        raise Conflict('Global instructions must be a regular file')
    if state.exists() and not state.is_dir():
        raise Conflict('Installer state must be a directory')
    pending = state / 'pending.json'
    if pending.exists():
        raise Conflict('Interrupted transaction at ' + str(pending) + '; inspect targets and reconcile manually')
    receipt_path = safe(state / 'receipt.json')
    if safe(state / 'activation.json').exists():
        raise Conflict('Profile has activation-only ownership; use deactivate before managing the shared skill')
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    if receipt and (receipt['target'] != str(target) or receipt['agents'] != str(agents)):
        raise Conflict('Receipt belongs to different installation paths')
    current = agents.read_bytes() if agents.exists() else b''
    if receipt:
        if not target.exists() or actual_tree(target) != receipt['files']:
            raise Conflict('Installed skill customized or missing; preserve changes and reconcile')
        global_without(current, receipt.get('block'))
    elif target.exists():
        raise Conflict('Existing unmanaged target refused: ' + str(target))
    return target, state, agents, receipt, current


def shared_skill(target):
    """Validate a reference without taking ownership of any shared skill files."""
    manifest = safe(target / 'SKILL.md')
    if not target.is_dir() or not manifest.is_file():
        raise Conflict('Shared model-switcher SKILL.md is missing or not a regular file')
    digest_tree(target)  # Reject symlinks and nonregular resources before activation.
    text = manifest.read_text()
    parts = text.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise Conflict('Shared SKILL.md has no valid metadata header')
    names = [line.partition(':')[2].strip().strip('\"\'')
             for line in parts[1].splitlines() if line.startswith('name:')]
    if names != ['model-switcher']:
        raise Conflict('Shared SKILL.md metadata name must be model-switcher')


def activation_change(command, skills_dir, codex_home):
    """Manage one extra profile's instructions; never mutate the shared skill."""
    target = safe(safe(skills_dir) / 'model-switcher')
    state = safe(safe(codex_home) / 'model-switcher-install')
    agents = safe(safe(codex_home) / 'AGENTS.md')
    pending = safe(state / 'pending.json')
    receipt_path = safe(state / 'activation.json')
    if pending.exists():
        raise Conflict('Interrupted transaction at ' + str(pending) + '; reconcile manually')
    if safe(state / 'receipt.json').exists():
        raise Conflict('Primary installation already owns this profile; use install --no-global to change it')
    if agents.exists() and not agents.is_file():
        raise Conflict('Global instructions must be a regular file')
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    if receipt and (set(receipt) != {'version', 'mode', 'target', 'agents', 'block', 'original_global_existed'}
                    or receipt['version'] != 1 or receipt['mode'] != 'activation-only'
                    or receipt['target'] != str(target) or receipt['agents'] != str(agents)
                    or not isinstance(receipt['block'], str) or not receipt['block']
                    or not isinstance(receipt['original_global_existed'], bool)):
        raise Conflict('Activation receipt is invalid or belongs to different paths')
    current = agents.read_bytes() if agents.exists() else b''
    remainder = global_without(current, receipt.get('block') if receipt else None)
    if command == 'status':
        available = target.is_dir()
        if available:
            shared_skill(target)
        return {'status': 'activation-only' if receipt else 'absent', 'target': str(target),
                'global_activation': bool(receipt), 'shared_skill_available': available,
                'manages_shared_skill': False, 'rollback_available': False}
    if command == 'activate':
        shared_skill(target)
        new_block = block(target)
        if receipt and decoded(receipt['block']) == new_block:
            return {'status': 'unchanged', 'mode': 'activation-only', 'target': str(target)}
        original_global_existed = agents.exists()
        dump(pending, {'operation': 'activate', 'agents': str(agents), 'target': str(target)})
        atomic(agents, remainder + new_block)
        dump(receipt_path, {'version': 1, 'mode': 'activation-only', 'target': str(target),
                           'agents': str(agents), 'block': encoded(new_block),
                           'original_global_existed': receipt['original_global_existed'] if receipt else original_global_existed})
        pending.unlink()
        return {'status': 'activated', 'mode': 'activation-only', 'target': str(target)}
    if not receipt:
        return {'status': 'absent'}
    dump(pending, {'operation': 'deactivate', 'agents': str(agents)})
    if remainder or receipt['original_global_existed']:
        atomic(agents, remainder)
    elif agents.exists():
        agents.unlink()
    receipt_path.unlink()
    pending.unlink()
    return {'status': 'deactivated', 'manages_shared_skill': False}


def copy_files(source, destination, hashes):
    destination.mkdir(parents=True)
    for rel, expected in hashes.items():
        p = source / rel
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise Conflict('Source changed during install')
        out = destination / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)


def install(source, skills_dir, codex_home, activation=True):
    source = safe(source)
    files = digest_tree(source)
    if 'SKILL.md' not in files:
        raise Conflict('Source has no SKILL.md')
    target, state, agents, receipt, current = load_context(skills_dir, codex_home)
    if source == target or target in source.parents or source in target.parents:
        raise Conflict('Source and target must be separate trees')
    global_existed = agents.exists()
    new_block = block(target) if activation else b''
    old_owned = receipt.get('block') if receipt else None
    remainder = global_without(current, old_owned)
    new_global = remainder + new_block
    if receipt and files == receipt['files'] and encoded(new_block) == receipt.get('block'):
        return {'status': 'unchanged', 'target': str(target)}
    state.mkdir(parents=True, exist_ok=True)
    os.chmod(state, 0o700)
    dump(state / 'pending.json', {'operation': 'install', 'target': str(target), 'agents': str(agents)})
    prior = state / 'prior'
    if prior.exists():
        shutil.rmtree(prior)
    if receipt:
        prior.mkdir()
        copy_files(target, prior / 'skill', receipt['files'])
        dump(prior / 'receipt.json', receipt)
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = state / 'stage'
    if stage.exists():
        raise Conflict('Unreconciled stage exists')
    copy_files(source, stage, files)
    # Rename may cross filesystems. copytree staging is in the target filesystem.
    temp = Path(tempfile.mkdtemp(prefix='.model-switcher-', dir=str(target.parent)))
    shutil.rmtree(temp)
    shutil.copytree(stage, temp)
    if target.exists():
        shutil.rmtree(target)
    os.replace(temp, target)
    shutil.rmtree(stage)
    if new_global != current:
        atomic(agents, new_global)
    new_receipt = {'version': 1, 'target': str(target), 'agents': str(agents),
                   'files': files, 'block': encoded(new_block),
                   'original_global_existed': receipt['original_global_existed'] if receipt else global_existed}
    dump(state / 'receipt.json', new_receipt)
    (state / 'pending.json').unlink()
    return {'status': 'installed', 'target': str(target), 'global_activation': activation}


def change(command, skills_dir, codex_home):
    target, state, agents, receipt, current = load_context(skills_dir, codex_home)
    if command == 'status':
        return {'status': 'installed' if receipt else 'absent', 'target': str(target),
                'global_activation': bool(receipt and decoded(receipt.get('block'))),
                'rollback_available': (state / 'prior' / 'receipt.json').exists()}
    if not receipt:
        return {'status': 'absent'}
    remainder = global_without(current, receipt.get('block'))
    old = None
    if command == 'rollback':
        prior = safe(state / 'prior')
        oldpath = safe(prior / 'receipt.json')
        if not oldpath.exists():
            raise Conflict('No prior managed version; uninstall is available')
        old = json.loads(oldpath.read_text())
        if actual_tree(prior / 'skill') != old['files']:
            raise Conflict('Rollback backup changed')
        if old['target'] != str(target) or old['agents'] != str(agents):
            raise Conflict('Rollback backup belongs to different paths')
    dump(state / 'pending.json', {'operation': command, 'target': str(target)})
    shutil.rmtree(target)
    if old:
        copy_files(state / 'prior' / 'skill', target, old['files'])
        desired = remainder + decoded(old.get('block'))
        atomic(agents, desired)
        dump(state / 'receipt.json', old)
        shutil.rmtree(state / 'prior')
    else:
        if remainder or receipt['original_global_existed']:
            if current != remainder:
                atomic(agents, remainder)
        elif agents.exists():
            agents.unlink()
        (state / 'receipt.json').unlink()
        if (state / 'prior').exists():
            shutil.rmtree(state / 'prior')
    (state / 'pending.json').unlink()
    return {'status': 'rolled-back' if old else 'uninstalled'}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['install', 'status', 'rollback', 'uninstall', 'activate', 'deactivate'])
    p.add_argument('--skills-dir', type=Path, default=Path.home() / '.agents/skills')
    p.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    p.add_argument('--no-global', action='store_true', help='Install discovery only; omit global activation instructions')
    a = p.parse_args(argv)
    try:
        state = safe(a.codex_home / 'model-switcher-install')
        state.mkdir(parents=True, exist_ok=True)
        os.chmod(state, 0o700)
        lock = state / 'operation.lock'
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            if a.command in ('activate', 'deactivate') or (a.command == 'status' and safe(state / 'activation.json').exists()):
                result = activation_change(a.command, a.skills_dir, a.codex_home)
            elif a.command == 'install':
                result = install(Path(__file__).resolve().parents[1], a.skills_dir, a.codex_home, not a.no_global)
            else:
                result = change(a.command, a.skills_dir, a.codex_home)
        finally:
            lock.unlink()
        print(json.dumps(result, indent=2))
        return 0
    except (Conflict, OSError, ValueError, KeyError) as e:
        print(json.dumps({'status': 'blocked', 'reason': str(e)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
