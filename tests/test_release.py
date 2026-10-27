import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release', ROOT / 'scripts/build_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def test_repeatable_public_archive_excludes_private_state(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory).resolve()
            a, b = temp / 'a.zip', temp / 'b.zip'
            first = release.build(ROOT, a); second = release.build(ROOT, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(first['sha256'], second['sha256'])
            with zipfile.ZipFile(a) as archive:
                self.assertEqual(archive.namelist(), [p.as_posix() for p in release.files(ROOT)])
                self.assertIsNone(archive.testzip())
                self.assertIn('LICENSE', archive.namelist())
                self.assertIn('model-switcher/SKILL.md', archive.namelist())
                self.assertFalse(any('.checkpoint' in p or '.forge' in p or p.endswith('manual-real-output.json') for p in archive.namelist()))

    def test_export_refuses_existing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory).resolve() / 'public'
            release.export(ROOT, dest)
            with self.assertRaisesRegex(ValueError, 'empty'):
                release.export(ROOT, dest)
            self.assertTrue((dest / 'README.md').is_file())


if __name__ == '__main__':
    unittest.main()
