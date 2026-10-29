import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


INSTALLER = Path(__file__).resolve().parents[1] / 'model-switcher/scripts/install.py'


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'source/model-switcher'
        (self.source / 'scripts').mkdir(parents=True)
        shutil.copyfile(INSTALLER, self.source / 'scripts/install.py')
        (self.source / 'SKILL.md').write_text('---\nname: model-switcher\ndescription: Route work\n---\nFirst version\n')
        self.skills = self.root / 'skills'
        self.home = self.root / 'codex'
        self.home.mkdir()
        self.global_file = self.home / 'AGENTS.md'
        self.target = self.skills / 'model-switcher'

    def run_install(self, command='install', *extra, expected=0):
        p = subprocess.run([sys.executable, str(self.source / 'scripts/install.py'), command,
                            '--skills-dir', str(self.skills), '--codex-home', str(self.home), *extra],
                           text=True, capture_output=True)
        self.assertEqual(p.returncode, expected, p.stdout + p.stderr)
        return json.loads(p.stdout if p.returncode == 0 else p.stderr)

    def test_install_repeat_uninstall_preserves_outside_edits(self):
        self.global_file.write_text('Existing custom instructions\n')
        self.run_install()
        installed = self.global_file.read_text()
        self.assertIn('Existing custom instructions\n', installed)
        self.assertIn('meaningful handoffs', installed)
        self.assertEqual(self.run_install()['status'], 'unchanged')
        self.global_file.write_text('New prefix\n' + installed + 'New suffix\n')
        self.run_install('uninstall')
        self.assertEqual(self.global_file.read_text(), 'New prefix\nExisting custom instructions\nNew suffix\n')
        self.assertFalse(self.target.exists())

    def test_update_and_rollback_restore_prior_skill_and_activation(self):
        self.global_file.write_text('Personal instructions')
        original_global = self.global_file.read_bytes()
        self.run_install('install', '--no-global')
        old = (self.target / 'SKILL.md').read_bytes()
        (self.source / 'SKILL.md').write_text('---\nname: model-switcher\ndescription: Route work\n---\nSecond version\n')
        self.run_install()
        self.assertNotEqual((self.target / 'SKILL.md').read_bytes(), old)
        self.assertIn('BEGIN model-switcher', self.global_file.read_text())
        self.run_install('rollback')
        self.assertEqual((self.target / 'SKILL.md').read_bytes(), old)
        self.assertEqual(self.global_file.read_bytes(), original_global)
        self.run_install('uninstall')
        self.assertEqual(self.global_file.read_bytes(), original_global)

    def test_upgrade_preserves_installed_owner_and_modes(self):
        import stat
        self.run_install()
        paths=[self.target,self.target/'scripts',self.target/'SKILL.md']
        for path in paths:path.chmod(0o700 if path.is_dir() else 0o600)
        expected={str(p.relative_to(self.target)):(p.stat().st_uid,p.stat().st_gid,stat.S_IMODE(p.stat().st_mode)) for p in paths}
        (self.source/'SKILL.md').write_text((self.source/'SKILL.md').read_text()+'Verified update\n')
        self.run_install()
        actual={str(p.relative_to(self.target)):(p.stat().st_uid,p.stat().st_gid,stat.S_IMODE(p.stat().st_mode)) for p in paths}
        self.assertEqual(actual,expected)

    def test_customized_skill_blocks_update_and_removal(self):
        self.run_install()
        p = self.target / 'SKILL.md'
        p.write_text('User customization')
        before = self.global_file.read_bytes()
        self.assertIn('customized', self.run_install('uninstall', expected=2)['reason'])
        self.assertEqual(p.read_text(), 'User customization')
        self.assertEqual(self.global_file.read_bytes(), before)
        self.run_install(expected=2)

    def test_customized_block_blocks_removal(self):
        self.run_install()
        self.global_file.write_text(self.global_file.read_text().replace('meaningful handoffs', 'custom handoffs'))
        self.run_install('uninstall', expected=2)
        self.assertTrue(self.target.exists())

    def test_unknown_target_and_symlink_are_refused(self):
        self.target.mkdir(parents=True)
        (self.target / 'SKILL.md').write_text('Unknown')
        self.run_install(expected=2)
        shutil.rmtree(self.target)
        self.target.symlink_to(self.source, target_is_directory=True)
        self.run_install(expected=2)
        self.assertTrue(self.target.is_symlink())

    def test_symlink_global_and_source_refused(self):
        other = self.root / 'other'; other.write_text('Private')
        self.global_file.symlink_to(other)
        self.run_install(expected=2)
        self.assertEqual(other.read_text(), 'Private')
        self.global_file.unlink()
        (self.source / 'linked').symlink_to(other)
        self.run_install(expected=2)
        self.assertFalse(self.target.exists())

    def test_missing_global_file_removed_empty_existing_file_retained(self):
        self.run_install(); self.run_install('uninstall')
        self.assertFalse(self.global_file.exists())
        self.global_file.write_bytes(b'')
        self.run_install(); self.run_install('uninstall')
        self.assertTrue(self.global_file.exists())
        self.assertEqual(self.global_file.read_bytes(), b'')

    def test_interrupted_and_concurrent_transactions_block(self):
        self.run_install()
        state = self.home / 'model-switcher-install'
        pending = state / 'pending.json'; pending.write_text('{}')
        self.run_install('status', expected=2)
        pending.unlink()
        lock = state / 'operation.lock'; lock.write_text('Evidence')
        self.run_install(expected=2)
        self.assertEqual(lock.read_text(), 'Evidence')

    def test_added_installed_file_blocks_removal(self):
        self.run_install()
        (self.target / 'private.txt').write_text('Keep me')
        self.run_install('uninstall', expected=2)
        self.assertTrue((self.target / 'private.txt').exists())

    def secondary(self, command, *extra, expected=0):
        return self.run_install(command, '--codex-home', str(self.root / 'second'), *extra, expected=expected)

    def test_shared_profile_activation_status_and_text_preservation(self):
        self.run_install()
        shared = {p.relative_to(self.target): p.read_bytes()
                  for p in self.target.rglob('*') if p.is_file()}
        second = self.root / 'second'; second.mkdir()
        agents = second / 'AGENTS.md'; agents.write_text('Second profile rules\n')
        self.assertEqual(self.secondary('activate')['status'], 'activated')
        active = agents.read_text()
        self.assertIn('Second profile rules\n', active)
        self.assertEqual(active.count('BEGIN model-switcher'), 1)
        self.assertEqual(self.secondary('activate')['status'], 'unchanged')
        status = self.secondary('status')
        self.assertEqual(status['status'], 'activation-only')
        self.assertFalse(status['manages_shared_skill'])
        self.assertTrue(status['shared_skill_available'])
        agents.write_text('New prefix\n' + active + 'New suffix\n')
        self.secondary('deactivate')
        self.assertEqual(agents.read_text(), 'New prefix\nSecond profile rules\nNew suffix\n')
        self.assertEqual({p.relative_to(self.target): p.read_bytes()
                          for p in self.target.rglob('*') if p.is_file()}, shared)
        self.assertEqual(self.run_install('status')['status'], 'installed')

    def test_secondary_activation_does_not_claim_primary_ownership(self):
        self.run_install(); self.secondary('activate')
        self.secondary('install', expected=2)
        self.secondary('uninstall', expected=2)
        self.secondary('rollback', expected=2)
        self.run_install('activate', expected=2)
        self.run_install('deactivate', expected=2)
        self.assertTrue(self.target.exists())

    def test_secondary_deactivation_after_shared_target_removed(self):
        self.run_install(); self.secondary('activate'); self.run_install('uninstall')
        self.assertFalse(self.secondary('status')['shared_skill_available'])
        self.secondary('deactivate')
        self.assertFalse((self.root / 'second/AGENTS.md').exists())
        self.assertFalse(self.target.exists())

    def test_secondary_existing_empty_global_retained(self):
        self.run_install()
        second = self.root / 'second'; second.mkdir()
        agents = second / 'AGENTS.md'; agents.write_bytes(b'')
        self.secondary('activate'); self.secondary('deactivate')
        self.assertEqual(agents.read_bytes(), b'')

    def test_secondary_activation_refuses_modified_and_unknown_blocks(self):
        self.run_install(); self.secondary('activate')
        agents = self.root / 'second/AGENTS.md'
        agents.write_text(agents.read_text().replace('meaningful handoffs', 'edited handoffs'))
        before = agents.read_bytes()
        self.secondary('activate', expected=2); self.secondary('deactivate', expected=2)
        self.assertEqual(agents.read_bytes(), before)
        state = self.root / 'second/model-switcher-install'
        (state / 'activation.json').unlink()
        self.secondary('activate', expected=2)

    def test_secondary_reference_metadata_and_symlinks_refused(self):
        self.secondary('activate', expected=2)
        self.run_install()
        manifest = self.target / 'SKILL.md'; old = manifest.read_bytes()
        manifest.write_text('---\nname: other-skill\n---\n')
        self.secondary('activate', expected=2)
        manifest.unlink(); manifest.symlink_to(self.source / 'SKILL.md')
        self.secondary('activate', expected=2)
        manifest.unlink(); manifest.write_bytes(old)
        second = self.root / 'second'; second.mkdir(exist_ok=True)
        (second / 'AGENTS.md').symlink_to(self.global_file)
        self.secondary('activate', expected=2)
        self.assertEqual(self.run_install('status')['status'], 'installed')

    def test_secondary_ambiguous_receipt_and_pending_refused(self):
        self.run_install(); self.secondary('activate')
        state = self.root / 'second/model-switcher-install'
        (state / 'receipt.json').write_text('{}')
        self.secondary('status', expected=2); self.secondary('deactivate', expected=2)
        (state / 'receipt.json').unlink()
        (state / 'pending.json').write_text('{}')
        self.secondary('activate', expected=2); self.secondary('deactivate', expected=2)


    def test_fresh_default_is_policy_without_standing_automatic_authority(self):
        result = self.run_install()
        self.assertEqual(result['automation_mode'], 'policy')
        self.assertEqual(self.run_install('status')['automation_mode'], 'policy')
        self.assertNotIn('standing preference', self.global_file.read_text())
        self.assertNotIn('one-use continuation', self.global_file.read_text())
        self.run_install('install', '--no-global')
        self.assertEqual(self.run_install('status')['automation_mode'], 'disabled')

    def test_automatic_preference_contains_transition_contract_and_preserves_on_upgrade(self):
        self.global_file.write_text('User rules\n')
        self.assertEqual(self.run_install('install', '--automatic')['automation_mode'], 'automatic')
        block = self.global_file.read_text()
        for phrase in ('models AND reasoning effort', 'checkpoint or handoff first',
                       'verify readback', 'one-use continuation', 'concrete reason',
                       'Explicit model choices', 'paid API spending', 'mid-turn'):
            self.assertIn(phrase, block)
        self.assertEqual(self.run_install()['status'], 'unchanged')
        (self.source / 'SKILL.md').write_text('---\nname: model-switcher\n---\nUpdated content\n')
        self.assertEqual(self.run_install()['automation_mode'], 'automatic')
        self.assertEqual(self.global_file.read_text(), block)
        self.assertEqual(self.run_install('status')['automation_mode'], 'automatic')
        self.assertEqual(set(p.name for p in self.home.iterdir()), {'AGENTS.md', 'model-switcher-install'})
        self.assertFalse(any(p.name == 'automations' for p in self.home.rglob('*')))

    def test_manual_downgrade_persists_and_rollback_restores_automatic(self):
        self.run_install('install', '--automatic')
        original = self.global_file.read_bytes()
        self.assertEqual(self.run_install('install', '--manual')['automation_mode'], 'manual')
        self.assertIn('Keep automatic switching and automatic continuation disabled', self.global_file.read_text())
        self.assertNotIn('standing preference', self.global_file.read_text())
        self.assertEqual(self.run_install()['status'], 'unchanged')
        self.assertEqual(self.run_install('status')['automation_mode'], 'manual')
        self.assertEqual(self.run_install('rollback')['automation_mode'], 'automatic')
        self.assertEqual(self.global_file.read_bytes(), original)

    def test_legacy_primary_receipt_upgrades_without_new_authority_and_rolls_back(self):
        self.run_install()
        receipt = json.loads((self.home / 'model-switcher-install/receipt.json').read_text())
        self.assertEqual(set(receipt), {'version', 'target', 'agents', 'files', 'block', 'original_global_existed'})
        original = self.global_file.read_bytes()
        self.run_install('install', '--automatic')
        self.assertEqual(self.run_install('rollback')['automation_mode'], 'policy')
        self.assertEqual(self.global_file.read_bytes(), original)

    def test_secondary_automatic_preference_is_explicit_and_independent(self):
        self.run_install('install', '--automatic')
        primary = self.global_file.read_bytes()
        shared = {p.relative_to(self.target): p.read_bytes() for p in self.target.rglob('*') if p.is_file()}
        self.assertEqual(self.secondary('activate')['automation_mode'], 'policy')
        self.assertEqual(self.secondary('activate', '--automatic')['automation_mode'], 'automatic')
        agents = self.root / 'second/AGENTS.md'
        automatic = agents.read_bytes()
        self.assertEqual(self.secondary('activate')['status'], 'unchanged')
        self.assertEqual(agents.read_bytes(), automatic)
        self.assertEqual(self.secondary('status')['automation_mode'], 'automatic')
        self.assertEqual(self.secondary('activate', '--manual')['automation_mode'], 'manual')
        self.assertEqual(self.secondary('activate')['automation_mode'], 'manual')
        self.assertEqual(self.global_file.read_bytes(), primary)
        self.assertEqual({p.relative_to(self.target): p.read_bytes() for p in self.target.rglob('*') if p.is_file()}, shared)
        self.secondary('deactivate')
        self.assertEqual(self.secondary('activate')['automation_mode'], 'policy')

    def test_automatic_mode_still_refuses_changed_activation_and_shared_files(self):
        self.run_install('install', '--automatic')
        self.global_file.write_text(self.global_file.read_text().replace('concrete reason', 'my custom reason'))
        before = self.global_file.read_bytes()
        self.run_install('install', '--manual', expected=2)
        self.assertEqual(self.global_file.read_bytes(), before)

    def test_mode_flags_on_wrong_commands_reject_before_creating_profile_state(self):
        for command, flags in [('status', ['--automatic']), ('rollback', ['--manual']),
                               ('uninstall', ['--automatic']), ('deactivate', ['--manual']),
                               ('install', ['--automatic', '--no-global']),
                               ('install', ['--manual', '--no-global']),
                               ('activate', ['--no-global'])]:
            with self.subTest(command=command, flags=flags):
                self.run_install(command, *flags, expected=2)
                self.assertFalse((self.home / 'model-switcher-install').exists())
                self.assertFalse(self.target.exists())
                self.assertFalse(self.global_file.exists())

    def test_mode_flags_are_mutually_exclusive_without_side_effects(self):
        result = subprocess.run([sys.executable, str(self.source / 'scripts/install.py'), 'install',
                                 '--skills-dir', str(self.skills), '--codex-home', str(self.home),
                                 '--automatic', '--manual'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.home / 'model-switcher-install').exists())
        self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main()
