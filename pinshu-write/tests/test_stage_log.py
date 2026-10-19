"""Tests for scripts/stage_log.py: per-stage time, retries, waits, human stops, failure and resume point."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "stage_log.py"
SPEC = importlib.util.spec_from_file_location("stage_log", SCRIPT)
stage_log = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage_log)

T0 = datetime(2026, 10, 12, 9, 0, 0)


def at(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


class StageLogTests(unittest.TestCase):
    def test_answers_slowest_retries_waits_and_human_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            stage_log.start(d, "批准1", "human", now=at(0)); stage_log.end(d, "批准1", now=at(12))
            stage_log.start(d, "5 正文", "machine", model="A", now=at(12)); stage_log.end(d, "5 正文", "empty", now=at(13))
            stage_log.start(d, "5 正文", "wait", model="A", now=at(13)); stage_log.end(d, "5 正文", "quota", now=at(23))
            stage_log.start(d, "5 正文", "machine", model="B", now=at(23)); stage_log.end(d, "5 正文", now=at(53))
            report = stage_log.summarize(d)
            self.assertEqual(report["status"], "OK")
            self.assertEqual(report["slowest_stage"], "5 正文")
            body = report["stages"][1]
            self.assertEqual((body["attempts"], body["retries"]), (3, 2))
            self.assertEqual(body["seconds"], {"machine": 1860.0, "wait": 600.0, "human": 0.0})
            self.assertEqual(report["human_stops"], ["批准1"])
            self.assertEqual(report["model_calls"], {"A": {"empty": 1, "quota": 1}, "B": {"ok": 1}})
            text = stage_log.render(report)
            self.assertIn("最慢一步：5 正文", text)
            self.assertIn("空回复×1", text)

    def test_failure_keeps_last_success_and_resume_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            stage_log.start(d, "5 正文", now=at(0)); stage_log.end(d, "5 正文", now=at(5))
            stage_log.start(d, "证据截图", "wait", now=at(5))
            stage_log.end(d, "证据截图", "blocked", note="X 帖子三次超时", resume_from="证据截图",
                          manual_handoff="/x/人工截图指引_01.md", now=at(9))
            report = stage_log.summarize(d)
            self.assertEqual(report["status"], "BLOCKED")
            self.assertEqual(report["failed_stage"], "证据截图")
            self.assertEqual(report["last_successful_stage"], "5 正文")
            self.assertEqual(report["resume_from"], "证据截图")
            self.assertEqual(report["manual_handoff"], "/x/人工截图指引_01.md")
            stage_log.start(d, "证据截图", now=at(20)); stage_log.end(d, "证据截图", now=at(21))
            self.assertEqual(stage_log.summarize(d)["status"], "OK")

    def test_end_without_start_and_bad_result_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                stage_log.end(Path(tmp), "6 审稿")
            stage_log.start(Path(tmp), "6 审稿")
            with self.assertRaises(ValueError):
                stage_log.end(Path(tmp), "6 审稿", "great")
            self.assertEqual(stage_log.summarize(Path(tmp))["status"], "RUNNING")

    def test_cli_summary_writes_readable_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(SCRIPT), "--dir", tmp, *a], capture_output=True, text=True)
            self.assertEqual(run("start", "2 研究", "--model", "M").returncode, 0)
            self.assertEqual(run("end", "2 研究", "--result", "timeout", "--note", "等了 10 分钟").returncode, 0)
            out = run("summary")
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("失败在：2 研究", out.stdout)
            self.assertTrue((Path(tmp) / stage_log.REPORT_NAME).is_file())
            self.assertEqual(run("end", "不存在").returncode, 1)

    def test_a_later_recovery_does_not_hide_an_earlier_failure(self):
        """Independent review 2026-10-12: A fails, B fails, B succeeds on retry -> still FAILED at A."""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            stage_log.start(d, "A", now=at(0)); stage_log.end(d, "A", "failed", note="A 坏了", now=at(1))
            stage_log.start(d, "B", now=at(1)); stage_log.end(d, "B", "timeout", now=at(2))
            stage_log.start(d, "B", now=at(2)); stage_log.end(d, "B", now=at(3))
            report = stage_log.summarize(d)
            self.assertEqual(report["status"], "FAILED")
            self.assertEqual([u["stage"] for u in report["unresolved"]], ["A"])
            self.assertEqual(report["failed_stage"], "A")


class ReviewFixesTests(unittest.TestCase):
    def test_second_start_of_a_running_step_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_log.start(Path(tmp), "5 正文", model="A", now=at(0))
            with self.assertRaisesRegex(ValueError, "still running"):
                stage_log.start(Path(tmp), "5 正文", model="B", now=at(1))

    def test_documented_fallback_is_a_downgrade_not_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            stage_log.start(d, "证据截图", now=at(0))
            with self.assertRaisesRegex(ValueError, "--note"):
                stage_log.end(d, "证据截图", "skipped", now=at(1))
            stage_log.end(d, "证据截图", "skipped", note="没有浏览器，交了待补截清单", now=at(1))
            stage_log.start(d, "7 交付", now=at(1)); stage_log.end(d, "7 交付", now=at(2))
            report = stage_log.summarize(d)
            self.assertEqual(report["status"], "OK")
            self.assertEqual(report["downgraded"], [{"stage": "证据截图", "note": "没有浏览器，交了待补截清单"}])
            self.assertIn("降级交付", stage_log.render(report))


class BackfillTests(unittest.TestCase):
    """--at: a start or end the organizer forgot to log can be written afterwards with its real time."""

    def test_backdated_start_counts_the_real_duration_and_is_marked(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            stage_log.start(d, "6 补料", "machine", now=at(40), at="09:05")
            stage_log.end(d, "6 补料", now=at(40))
            report = stage_log.summarize(d)
            self.assertEqual(report["stages"][0]["seconds"]["machine"], 35 * 60.0)
            self.assertTrue(stage_log.read(d)[0]["backfilled"])
            self.assertNotIn("backfilled", stage_log.read(d)[1])

    def test_full_date_form_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            stage_log.start(d, "5 正文", now=at(30), at="2026-10-12 09:10")
            stage_log.end(d, "5 正文", now=at(30), at="2026-10-12T09:25")
            self.assertEqual(stage_log.summarize(d)["stages"][0]["total_seconds"], 15 * 60.0)

    def test_future_time_bad_format_and_end_before_start_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            with self.assertRaises(ValueError):
                stage_log.start(d, "5 正文", now=at(0), at="09:30")
            with self.assertRaises(ValueError):
                stage_log.start(d, "5 正文", now=at(0), at="nine")
            stage_log.start(d, "5 正文", now=at(20), at="09:15")
            with self.assertRaises(ValueError):
                stage_log.end(d, "5 正文", now=at(20), at="09:10")
            self.assertEqual(len(stage_log.read(d)), 1)

    def test_cli_accepts_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(SCRIPT), "--dir", tmp, *a], capture_output=True, text=True)
            self.assertEqual(run("start", "6 补料", "--at", "00:00").returncode, 0)
            self.assertEqual(run("end", "6 补料").returncode, 0)
            self.assertTrue(stage_log.read(tmp)[0]["backfilled"])
            self.assertNotEqual(run("start", "7 审稿", "--at", "25:99").returncode, 0)


if __name__ == "__main__":
    unittest.main()
