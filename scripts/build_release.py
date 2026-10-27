#!/usr/bin/env python3
"""Validate and export the explicit public package without inference or private state."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

SKILL_FILES = [
    'SKILL.md', 'README.md', 'LICENSE', 'agents/openai.yaml',
    'references/capabilities.md', 'references/examples.md', 'references/host.md',
    'references/runtime.md', 'scripts/install.py', 'templates/handoff.md',
]
PUBLIC_FILES = [
    'README.md', 'LICENSE', '.gitignore', '.github/workflows/ci.yml',
    'scripts/build_release.py', 'tests/test_install.py', 'tests/test_release.py',
    'validation/REPORT.md', 'validation/cases.json', 'validation/evaluator.json',
    'validation/model-grades.md', 'validation/model-grades-v2.md',
    'validation/live-observations.json', 'validation/dependency-hashes.json',
    'validation/final-skill-hashes.json', 'validation/baseline-package-check.json',
    'validation/baseline-suite.json', 'validation/candidate-suite.json',
    'validation/candidate-v2-suite.json', 'validation/native-checks.json',
    'validation/manual-real-check.json', 'validation/manual-real-review.md',
]


def files(root):
    return [Path(x) for x in sorted(PUBLIC_FILES + ['model-switcher/' + x for x in SKILL_FILES])]


def validate(root):
    paths = files(root)
    for rel in paths:
        p = root / rel
        if not p.is_file() or any(q.is_symlink() for q in [p] + list(p.parents)):
            raise ValueError('Missing or symlinked export path: ' + str(rel))
        data = p.read_bytes()
        if re.search(rb'/(?:Users|home)/[A-Za-z0-9_]', data):
            raise ValueError('Personal absolute path in public file: ' + str(rel))
        if re.search(rb'\bsk-[A-Za-z0-9]{24,}', data):
            raise ValueError('Credential-like content in public file: ' + str(rel))
    skill = root / 'model-switcher'
    text = (skill / 'SKILL.md').read_text()
    front = text.split('---', 2)[1]
    if not re.search(r'^name: model-switcher$', front, re.M):
        raise ValueError('Skill name mismatch')
    description = re.search(r'^description: (.+)$', front, re.M)
    if not description or not 1 <= len(description[1]) <= 1024:
        raise ValueError('Invalid discovery description')
    if 'allow_implicit_invocation: true' not in (skill / 'agents/openai.yaml').read_text():
        raise ValueError('Implicit invocation metadata missing')
    license_text = (root / 'LICENSE').read_bytes()
    if not license_text.startswith(b'MIT License\n') or license_text != (skill / 'LICENSE').read_bytes():
        raise ValueError('MIT notices missing or inconsistent')
    allowed = {str(p) for p in paths}
    for rel in paths:
        if rel.suffix != '.md':
            continue
        for target in re.findall(r'\]\(([^)]+)\)', (root / rel).read_text()):
            target = target.strip('<>').split('#', 1)[0]
            if not target or '://' in target:
                continue
            resolved = (root / rel.parent / target).resolve()
            try:
                exported = str(resolved.relative_to(root.resolve()))
            except ValueError:
                raise ValueError('Link escapes export: ' + str(rel))
            if exported not in allowed:
                raise ValueError('Link target not exported: ' + str(rel) + ': ' + target)
    return paths


def build(root, output):
    paths = validate(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for rel in paths:
            info = zipfile.ZipInfo(rel.as_posix(), date_time=(2026, 10, 26, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (root / rel).read_bytes())
    return {'artifact': output.name, 'files': len(paths), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


def export(root, destination):
    paths = validate(root)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Public export destination must be empty')
    for rel in paths:
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / rel).read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('dist/model-switcher-0.1.1.zip'))
    parser.add_argument('--export-dir', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.export_dir:
        export(root, args.export_dir.resolve())
    print(json.dumps(build(root, args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
