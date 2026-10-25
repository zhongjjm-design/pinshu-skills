"""Public, self-contained release regressions: no private writer or browser fixtures."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_public_bundle import audit_root, audit_zip


class ReleaseBlockerTests(unittest.TestCase):
    def run_doctor_version(self, version):
        script = ("import sys,runpy;sys.path.insert(0," + repr(str(ROOT / 'scripts'))
                  + ");sys.version_info=" + repr(version) + ";runpy.run_path("
                  + repr(str(ROOT / 'scripts/doctor.py')) + ",run_name='__main__')")
        return subprocess.run([sys.executable, '-B', '-c', script],
                              capture_output=True, text=True, timeout=30)

    def test_doctor_unsupported_python_process_fails(self):
        proc = self.run_doctor_version((3, 9, 6))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(json.loads(proc.stdout)['planning_ready'])

    def test_doctor_supported_python_process_succeeds(self):
        proc = self.run_doctor_version((3, 10, 0))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(json.loads(proc.stdout)['planning_ready'])

    def test_hidden_extensionless_files_are_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / '.hidden' / 'nested' / 'plugin_root'
            f.parent.mkdir(parents=True)
            f.write_text('/' + 'Users' + '/example/private')
            result = audit_root(root)
            self.assertEqual(result['counts']['user_home'], 1)
            self.assertEqual(result['status'], 'FAIL')
            f.write_text('portable data only')
            self.assertEqual(audit_root(root)['status'], 'PASS')

    def test_zip_all_text_members_not_only_named_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'fixture.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('.hidden/extensionless', '/' + 'home' + '/example/private')
                z.writestr('text-disguised.bin', 'sk' + '-' + 'A' * 30)
                z.writestr('contact', 'person' + '@' + 'example.test')
                z.writestr('.video_agent/plugin_root', 'discard')
                z.writestr('.hidden/utf16', ('/' + 'home' + '/another/private').encode('utf-16'))
            result = audit_zip(archive)
            self.assertEqual(result['counts']['linux_home'], 2, result)
            for category in ['api_secret', 'email', 'private_plugin_directory']:
                self.assertEqual(result['counts'][category], 1, result)
            self.assertEqual(result['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
