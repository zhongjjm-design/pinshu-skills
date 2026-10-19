"""Tests for scripts/run_watched.py."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_watched.py"
SPEC = importlib.util.spec_from_file_location("run_watched", SCRIPT)
run_watched = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_watched)

PY = sys.executable


def run(out, *opts, code):
    buf = io.StringIO()
    started = time.time()
    with contextlib.redirect_stdout(buf):
        rc = run_watched.main(["--out", str(out), "--poll", "0.1", *opts, "--", PY, "-c", code])
    return rc, buf.getvalue(), time.time() - started


class RunWatchedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "out.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_quick_exit_keeps_output_and_code(self):
        rc, line, _ = run(self.out, code="print('稿子'); import sys; sys.exit(3)")
        self.assertEqual(rc, 3)
        self.assertEqual(self.out.read_text(encoding="utf-8").strip(), "稿子")
        self.assertIn("exited with code 3", line)
        self.assertIn("exited with code 3", Path(str(self.out) + ".err").read_text(encoding="utf-8"))

    def test_runs_in_empty_folder_and_removes_it(self):
        rc, line, _ = run(self.out, code="import os; print(os.getcwd()); print(len(os.listdir('.')))")
        cwd, count = self.out.read_text(encoding="utf-8").split()
        self.assertEqual((rc, count), (0, "0"))
        self.assertFalse(Path(cwd).exists())
        self.assertNotIn("left files", line)

    def test_silent_call_is_stopped_after_check_time(self):
        rc, line, took = run(self.out, "--check-after", "0.5", "--silent", "0.5",
                             code="import time; time.sleep(30)")
        self.assertEqual(rc, 124)
        self.assertIn("silent", line)
        self.assertLess(took, 10)

    def test_writing_call_is_never_stopped(self):
        code = "import time, sys\nfor i in range(15):\n    print(i, flush=True); time.sleep(0.1)\n"
        rc, line, _ = run(self.out, "--check-after", "0.2", "--silent", "0.5", code=code)
        self.assertEqual(rc, 0)
        self.assertIn("exited with code 0", line)
        self.assertEqual(len(self.out.read_text(encoding="utf-8").split()), 15)

    def test_thinking_call_using_cpu_is_not_stopped(self):
        code = "import time\nend = time.time() + 2.5\nwhile time.time() < end: pass\nprint('done')\n"
        rc, line, _ = run(self.out, "--check-after", "0.2", "--silent", "0.6", "--cpu-min", "0.2", code=code)
        self.assertEqual(rc, 0)
        self.assertIn("exited with code 0", line)
        self.assertEqual(self.out.read_text(encoding="utf-8").strip(), "done")

    def test_growing_watched_file_counts_as_activity(self):
        log = Path(self.tmp.name) / "session.log"
        code = (f"import time\nfor i in range(15):\n    open({str(log)!r}, 'a').write('x'); time.sleep(0.1)\n")
        rc, line, _ = run(self.out, "--check-after", "0.2", "--silent", "0.5", "--cpu-min", "100",
                          "--watch", str(log), code=code)
        self.assertEqual(rc, 0)
        self.assertIn("exited with code 0", line)

    def test_answer_idle_ends_finished_call(self):
        rc, line, took = run(self.out, "--answer-idle", "0.5",
                             code="import time; print('答完了', flush=True); time.sleep(30)")
        self.assertEqual(rc, 0)
        self.assertIn("answer idle", line)
        self.assertLess(took, 10)
        self.assertEqual(self.out.read_text(encoding="utf-8").strip(), "答完了")

    def test_nothing_stops_before_check_time(self):
        rc, line, _ = run(self.out, "--check-after", "30", "--silent", "0.2", code="import time; time.sleep(1.5)")
        self.assertEqual(rc, 0)
        self.assertIn("exited with code 0", line)

    def test_cputime_parsing(self):
        self.assertAlmostEqual(run_watched.parse_cputime("0:01.50"), 1.5)
        self.assertAlmostEqual(run_watched.parse_cputime("1:02:03.00"), 3723.0)
        self.assertAlmostEqual(run_watched.parse_cputime("2-00:00:01"), 172801.0)

    def test_claude_log_dir_follows_working_folder(self):
        dirs = run_watched.claude_log_dirs("/tmp/pw_run_ab.c")
        self.assertTrue(any(d.endswith("-tmp-pw-run-ab-c") for d in dirs))


if __name__ == "__main__":
    unittest.main()
