"""Tests for scripts/market_reference.py: ratio, the 100,000 cap, money safety, dedupe, cache, never blocking."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "market_reference.py"
SPEC = importlib.util.spec_from_file_location("market_reference", SCRIPT)
mr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mr)

NOW = time.time()


class FakeApi:
    """Answers and charges like the real API (it deducts even when told to drop the reply)."""

    def __init__(self, reads, histories, balance=100.0, search=None, charge=None, report_cost=True):
        self.reads, self.histories, self.balance, self.search = reads, histories, balance, search
        self.charge = charge or dict(mr.PRICE)
        self.report_cost = report_cost
        self.calls = []
        self.fail = None          # function(endpoint, body) -> exception to raise after charging, or None

    def __call__(self, endpoint, body):
        self.calls.append((endpoint, body))
        if endpoint == "get_remain_money":
            return {"code": 0, "remain_money": self.balance}
        self.balance = round(self.balance - self.charge[endpoint], 2)
        error = self.fail(endpoint, body) if self.fail else None
        if error is not None:
            raise error
        out = {"code": 0, "remain_money": self.balance}
        if self.report_cost:
            out["cost_money"] = self.charge[endpoint]
        if endpoint == "web_search":
            out["data"] = self.search
        elif endpoint == "read_zan":
            out["data"] = {"read": self.reads.get(body["url"]), "zan": 1, "looking": 1}
        elif endpoint == "post_history":
            out["data"] = self.histories.get(body["nickname"], [])
        return out

    def paid(self):
        return round(sum(self.charge[e] for e, _ in self.calls if e != "get_remain_money"), 2)


def search_box(*items):
    return [{"items": [{"title": f'<em class="highlight">{t}</em>', "doc_url": u, "source": {"title": a}, "date": int(NOW)}
                       for t, a, u in items]}]


def leads(prefix, n):
    return [{"position": 1, "post_time": int(NOW) - 86400 * (i + 1), "url": f"{prefix}{i}", "title": f"头条{i}"} for i in range(n)]


class MarketReferenceTests(unittest.TestCase):
    def setUp(self):
        self.search = search_box(("银行AI员工上岗", "小号", "u1"), ("大厂逼员工用AI", "大号", "u2"),
                                 ("银行AI员工上岗", "转载号", "u3"), ("阿里Token考核", "中号", "u4"))
        self.reads = {"u1": 21102, "u2": 100001, "u4": 18069}
        self.reads.update({f"s{i}": v for i, v in enumerate([2043, 4967, 39606, 5000, 4000])})
        self.reads.update({f"m{i}": v for i, v in enumerate([1795, 18132, 76960, 20000, 15000])})
        self.histories = {"小号": leads("s", 5), "中号": leads("m", 5)}

    def api(self, **kw):
        return FakeApi(self.reads, self.histories, search=self.search, **kw)

    def run_main(self, tmp, cap=3.0, extra=(), env=None, api=None):
        api = api or self.api()
        env = {"DAJIALA_API_KEY": "secret-key"} if env is None else env
        code = mr.main(["--dir", tmp, "--keyword", "AI考核员工", "--cap", str(cap), *extra], post=api, env=env, sleep=lambda s: None)
        return code, api

    def page(self, tmp):
        return next(Path(tmp).glob("数据参照_*.md")).read_text(encoding="utf-8")

    def spend_lines(self, tmp):
        return [json.loads(l) for l in (Path(tmp) / mr.SPEND_LOG).read_text(encoding="utf-8").splitlines()]

    def test_ratio_marks_small_account_big_response_and_skips_capped(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, api = self.run_main(tmp)
            self.assertEqual(code, 0)
            page = self.page(tmp)
            self.assertIn("| 待判 | 4.25 | 小号高表现 | 21,102 | 4,967 | 小号 |", page)
            self.assertIn("10万+（封顶，不比）", page)
            self.assertIn("| 待判 | 1.00 | 常规 |", page)
            self.assertNotIn("转载号", page)            # the repost counts once
            self.assertNotIn("<em", page)
            self.assertNotIn(("post_history", "大号"), [(e, b.get("nickname")) for e, b in api.calls])
            for line in ("- 数据源：", "- 取数时间：", "- 口径：", "- 样本量：", "不是撞题扫描"):
                self.assertIn(line, page)
            self.assertIn("小号高表现 1/3 篇（样本不到 5 篇，仅供参考）", page)
            self.assertAlmostEqual(sum(l["cost"] for l in self.spend_lines(tmp)), api.paid())

    def test_cap_holds_even_when_replies_do_not_report_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, api = self.run_main(tmp, cap=0.6, api=self.api(report_cost=False))
            self.assertLessEqual(api.paid(), 0.6 + 1e-9)
            self.assertIn("到每篇花费上限 0.6 元", self.page(tmp))
            self.assertEqual(len(self.spend_lines(tmp)), len([c for c in api.calls if c[0] != "get_remain_money"]))

    def test_balance_drop_corrects_an_underpriced_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            charge = dict(mr.PRICE, read_zan=0.1)           # the provider raised its price; the reply hides it
            _, api = self.run_main(tmp, cap=1.0, api=self.api(charge=charge, report_cost=False))
            self.assertLessEqual(api.paid(), 1.0 + 0.1 + 1e-9)   # at most one call's difference over the cap

    def test_lost_replies_count_as_spent_and_two_in_a_row_stop_everything(self):
        with tempfile.TemporaryDirectory() as tmp:
            api = self.api()
            api.fail = lambda e, b: TimeoutError("timed out") if e == "read_zan" else None
            code, _ = self.run_main(tmp, api=api)
            self.assertEqual(code, 0)
            self.assertEqual([e for e, _ in api.calls].count("read_zan"), 2)
            lines = self.spend_lines(tmp)
            self.assertEqual(sum(1 for l in lines if l["status"].startswith("回复丢失")), 2)
            self.assertIn("连续 2 次网络出错", self.page(tmp))
            self.assertAlmostEqual(sum(l["cost"] for l in lines), api.paid())

    def test_timeout_mid_run_keeps_what_was_already_paid_for(self):
        with tempfile.TemporaryDirectory() as tmp:
            api = self.api()
            api.fail = lambda e, b: TimeoutError("timed out") if e == "post_history" and b["nickname"] == "中号" else None
            self.run_main(tmp, api=api)
            page = self.page(tmp)
            self.assertIn("| 待判 | 4.25 | 小号高表现 | 21,102 |", page)
            self.assertIn("发文列表：中号：timed out", page)
            raw = json.loads(next(Path(tmp).glob("数据参照_*.json")).read_text(encoding="utf-8"))
            self.assertEqual(len(raw["items"]), 3)
            self.assertIn("cover", raw["items"][0])

    def test_interrupt_still_writes_page_and_every_paid_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            api = self.api()
            state = {"n": 0}
            def stop_on_fourth(e, b):
                state["n"] += 1
                return KeyboardInterrupt() if state["n"] == 4 else None
            api.fail = stop_on_fourth
            code, _ = self.run_main(tmp, api=api)
            self.assertEqual(code, 130)
            self.assertIn("被手动中断", self.page(tmp))
            self.assertAlmostEqual(sum(l["cost"] for l in self.spend_lines(tmp)), api.paid())

    def test_same_keyword_today_is_refused_unless_forced(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, first = self.run_main(tmp)
            _, second = self.run_main(tmp)
            self.assertEqual([e for e, _ in second.calls], [])
            _, third = self.run_main(tmp, extra=("--force",))
            self.assertIn("web_search", [e for e, _ in third.calls])

    def test_no_key_and_low_balance_spend_nothing_and_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, api = self.run_main(tmp, env={})
            self.assertEqual((code, api.calls), (0, []))
            self.assertIn("未取数", self.page(tmp))
        with tempfile.TemporaryDirectory() as tmp:
            code, api = self.run_main(tmp, api=self.api(balance=0.5))
            self.assertEqual([e for e, _ in api.calls], ["get_remain_money"])
            self.assertIn("不够这一轮", self.page(tmp))

    def test_cache_in_a_missing_folder_is_created_and_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache, ledger = Path(tmp) / "new" / "cache.json", Path(tmp) / "ledger.jsonl"
            extra = ("--cache", str(cache), "--ledger", str(ledger), "--force")
            _, first = self.run_main(tmp, extra=extra)
            _, second = self.run_main(tmp, extra=extra)
            self.assertTrue(cache.exists())
            self.assertNotIn("post_history", [e for e, _ in second.calls])
            paid = [c for c in first.calls + second.calls if c[0] != "get_remain_money"]
            self.assertEqual(len(ledger.read_text(encoding="utf-8").splitlines()), len(paid))

    def test_bad_cache_entries_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            cache.write_text(json.dumps({"小号": {"baseline": 5000}, "中号": "x"}), encoding="utf-8")
            code, api = self.run_main(tmp, extra=("--cache", str(cache)))
            self.assertEqual(code, 0)
            self.assertIn("| 待判 | 4.25 | 小号高表现 |", self.page(tmp))

    def test_key_echoed_by_the_api_is_redacted(self):
        def echo(endpoint, body):
            if endpoint == "get_remain_money":
                return {"code": 0, "remain_money": 50}
            return {"code": 101, "msg": f"bad key {body['key']}", "cost_money": 0}
        with tempfile.TemporaryDirectory() as tmp:
            self.run_main(tmp, api=echo)
            text = self.page(tmp) + (Path(tmp) / mr.SPEND_LOG).read_text(encoding="utf-8")
            self.assertNotIn("secret-key", text)
            self.assertIn("***", self.page(tmp))

    def test_arguments_are_bounded(self):
        for bad in (["--cap", "nan"], ["--cap", "inf"], ["--cap", "0"], ["--max-articles", "-1"], ["--keyword", " "]):
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
                mr.main(["--dir", tmp, "--keyword", "AI", *bad] if bad[0] != "--keyword" else ["--dir", tmp, *bad],
                        post=self.api(), env={"DAJIALA_API_KEY": "k"})

    def test_every_keyword_gets_its_share_of_articles(self):
        two = {"k1": search_box(*[(f"甲{i}", "号", f"a{i}") for i in range(10)]),
               "k2": search_box(*[(f"乙{i}", "号", f"b{i}") for i in range(10)])}
        api = self.api()
        orig = api.__call__
        def by_keyword(endpoint, body):
            if endpoint == "web_search":
                api.search = two[body["keyword"]]
            return orig(endpoint, body)
        with tempfile.TemporaryDirectory() as tmp:
            mr.main(["--dir", tmp, "--keyword", "k1", "--keyword", "k2", "--max-articles", "6", "--max-accounts", "0"],
                    post=by_keyword, env={"DAJIALA_API_KEY": "k"}, sleep=lambda s: None)
            raw = json.loads(next(Path(tmp).glob("数据参照_*.json")).read_text(encoding="utf-8"))
            self.assertEqual([i["keyword"] for i in raw["items"]].count("k2"), 3)

    def test_judge_and_baseline(self):
        self.assertEqual(mr.judge(695, 185)[1], "倍数高但阅读不到 2,000（不算）")
        self.assertEqual(mr.baseline_of([2043, 4967, 39606]), 4967)
        self.assertEqual(mr.baseline_of([5000, 100001]), "capped")
        self.assertIsNone(mr.baseline_of([None]))
        self.assertEqual(mr.judge(10000, 5000), (2.0, "小号高表现"))
        self.assertEqual(mr.judge(None, 5000)[1], "阅读数未取到")
        self.assertEqual(mr.judge(9000, "capped")[1], "大号（平时10万+，不比）")


if __name__ == "__main__":
    unittest.main()
