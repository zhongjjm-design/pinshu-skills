#!/usr/bin/env python3
"""Market reference: how readers actually responded to articles on the same topic.

Run once per article during research, by the organizer only. It searches WeChat articles for the
article's keywords, fetches each article's real read count, estimates each account's usual read count
from its recent lead articles, and divides the two. An article read several times more than its own
account usually gets is a "small account, big response" sample; a large account's ordinary read count
is not.

  python3 scripts/market_reference.py --dir <process folder> --keyword "AI考核员工" [--keyword ...]
      [--cap 3] [--env-file <file holding the key>] [--ledger <shared spend log.jsonl>]
      [--cache <account baseline cache.json>] [--dry-run] [--force]

Writes into the process folder: 数据参照_<keywords>_<date>.md (the page people read), the same name
.json (raw data), and 数据参照_花费.jsonl (one line per paid call, written the moment the call is made).
A reference, never a gate: with no key, no balance or no network it writes "未取数" and exits 0.

Money safety, in this order: every paid call is charged against the cap at list price before it is
sent and logged at once; the reply's actual charge, and the drop in balance, correct the figure upward,
never downward; a lost reply still counts as spent; two transport failures in a row stop all paid calls;
a balance below the next call's price stops them; nothing is ever retried; the same keyword already paid
for today in this folder is refused unless --force.

Data source: dajiala.com (极致了), a paid WeChat data API. Reads above 100,000 come back as 100001: such
articles and accounts are marked "10万+" and never compared. Prices are those charged in October 2026.
Plain Python 3.9+, no third-party packages.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

API_BASE = "https://www.dajiala.com/fbmain/monitor/v3/"
PRICE = {"web_search": 0.5, "read_zan": 0.04, "post_history": 0.16, "get_remain_money": 0.0}
CAPPED = 100001          # what the API returns for any read count above 100,000
HIGH_RATIO = 2.0         # starting assumption for "clearly above its own account"; revisit after ~10 articles
BASELINE_READS = 3       # lead articles read to estimate an account's usual level (5 left too few accounts within the cap)
MIN_READ = 2000          # starting assumption: below this a high ratio says little (695 vs 185 is noise)
BASELINE_DAYS = 60
CACHE_DAYS = 90
MAX_TRANSPORT_FAILURES = 2
REPORT_PREFIX = "数据参照"
SPEND_LOG = "数据参照_花费.jsonl"
TAG = re.compile(r"<[^>]+>")


class Stop(Exception):
    """No more paid calls in this run (cap, balance, or repeated transport failures)."""


def read_env_file(path: Path) -> dict:
    values = {}
    for line in Path(path).expanduser().read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            values[name.strip()] = value.strip().strip('"').strip("'")
    return values


def http_post(endpoint: str, body: dict, timeout: int = 30) -> dict:
    request = urllib.request.Request(API_BASE + endpoint, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            return json.loads(error.read().decode("utf-8"))
        except ValueError:
            return {"code": error.code, "msg": f"HTTP {error.code}"}


def _append(path: Path, line: dict):
    with Path(path).expanduser().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(line, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


class Client:
    def __init__(self, key: str, cap: float, post=http_post, gap: float = 1.0, spend_log: Path = None,
                 ledger: Path = None, clock=time.time, sleep=time.sleep):
        self.key, self.cap, self.post, self.gap = key, cap, post, gap
        self.spend_log, self.ledger, self.clock, self.sleep = spend_log, ledger, clock, sleep
        self.spent = 0.0
        self.start_balance = None
        self.remain = None
        self.stop_reason = None
        self.transport_failures = 0
        self.log = []
        self.notes = []
        self._last = 0.0

    def redact(self, text) -> str:
        text = str(text)
        return text.replace(self.key, "***") if self.key else text

    def _record(self, endpoint, label, cost, status):
        line = {"time": datetime.now().astimezone().isoformat(timespec="seconds"), "endpoint": endpoint,
                "label": label, "cost": cost, "remain": self.remain, "status": status}
        self.log.append(line)
        for target, prefix in ((self.spend_log, ""), (self.ledger, "pinshu-write 数据参照｜")):
            if target:
                try:
                    _append(target, {**line, "label": prefix + label})
                except OSError as error:
                    self.notes.append(f"花费记录没写进 {target}：{error}")

    def balance(self) -> float:
        payload = self.post("get_remain_money", {"key": self.key})
        if not isinstance(payload, dict) or payload.get("remain_money") is None:
            raise RuntimeError(self.redact(f"查余额失败：{payload.get('msg') if isinstance(payload, dict) else payload}"))
        self.start_balance = self.remain = float(payload["remain_money"])
        return self.remain

    def call(self, endpoint: str, body: dict, label: str):
        price = PRICE[endpoint]
        if self.stop_reason:
            raise Stop(self.stop_reason)
        if self.spent + price > self.cap + 1e-9:
            self.stop_reason = f"到每篇花费上限 {self.cap:g} 元"
            raise Stop(self.stop_reason)
        if self.remain is not None and self.remain < price:
            self.stop_reason = f"余额 {self.remain:.2f} 元不够下一笔"
            raise Stop(self.stop_reason)
        wait = self.gap - (self.clock() - self._last)
        if self.gap and wait > 0:
            self.sleep(wait)
        self.spent = round(self.spent + price, 2)          # charged before sending: a lost reply still counts
        try:
            payload = self.post(endpoint, {**body, "key": self.key})
        except BaseException as error:          # includes Ctrl-C: the call may have been charged, so log it first
            self._last = self.clock()
            self.transport_failures += 1
            self._record(endpoint, label, price, "回复丢失（按标价计）")
            if not isinstance(error, Exception):
                raise
            if self.transport_failures >= MAX_TRANSPORT_FAILURES:
                self.stop_reason = f"连续 {self.transport_failures} 次网络出错"
            raise RuntimeError(self.redact(f"{label}：{error}")) from None
        self._last = self.clock()
        self.transport_failures = 0
        actual = None
        if isinstance(payload, dict):
            try:
                actual = float(payload["cost_money"]) if payload.get("cost_money") is not None else None
            except (TypeError, ValueError):
                actual = None
            try:
                if payload.get("remain_money") is not None:
                    self.remain = float(payload["remain_money"])
            except (TypeError, ValueError):
                pass
        if actual is not None and actual > price:
            self.spent = round(self.spent + actual - price, 2)
        if self.start_balance is not None and self.remain is not None:
            self.spent = max(self.spent, round(self.start_balance - self.remain, 2))
        self._record(endpoint, label, actual if actual is not None else price,
                     "已扣" if actual is not None else "回复没写扣费（按标价计）")
        if not isinstance(payload, dict) or payload.get("code") not in (None, 0, "0"):
            msg = payload.get("msg") if isinstance(payload, dict) else payload
            raise RuntimeError(self.redact(f"{label}：接口报错 {msg}"))
        return payload


def _int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _date(seconds) -> str:
    value = _int(seconds)
    try:
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d") if value else ""
    except (OverflowError, OSError, ValueError):
        return ""


def search_items(payload) -> list:
    boxes = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), list) else []
    items = []
    for box in boxes:
        for item in (box.get("items") or []) if isinstance(box, dict) else []:
            if not isinstance(item, dict):
                continue
            title = TAG.sub("", str(item.get("title") or "")).strip()     # search highlights: <em class="highlight">
            source = item.get("source") if isinstance(item.get("source"), dict) else {}
            account = TAG.sub("", str(source.get("title") or "")).strip()
            url = str(item.get("doc_url") or "")
            if title and url:   # the cover link comes free with the search; kept in the raw json for the visual Skill
                items.append({"title": title, "account": account, "url": url, "date": _date(item.get("date")),
                              "cover": str(item.get("thumbUrl") or "")})
    return items


def lead_articles(rows, since_days: int = BASELINE_DAYS, now: float = None) -> list:
    cutoff = (now or time.time()) - since_days * 86400
    out = []
    for row in rows if isinstance(rows, list) else []:
        if isinstance(row, dict) and _int(row.get("position")) == 1 and (_int(row.get("post_time")) or 0) >= cutoff and row.get("url"):
            out.append({"title": str(row.get("title") or ""), "url": str(row["url"])})
    return out


def baseline_of(reads: list):
    """Median of the account's recent lead reads. None if unknown; 'capped' if the account is above 100,000."""
    values = [r for r in reads if isinstance(r, int)]
    if not values:
        return None
    if any(r >= CAPPED for r in values):
        return "capped"
    return int(statistics.median(values))


def judge(read, baseline):
    if not isinstance(read, int):
        return None, "阅读数未取到"
    if read >= CAPPED:
        return None, "10万+（封顶，不比）"
    if baseline == "capped":
        return None, "大号（平时10万+，不比）"
    if not isinstance(baseline, int) or baseline <= 0:
        return None, "账号平时水平未知"
    ratio = round(read / baseline, 2)
    if ratio >= HIGH_RATIO and read < MIN_READ:
        return ratio, f"倍数高但阅读不到 {MIN_READ:,}（不算）"
    return ratio, ("小号高表现" if ratio >= HIGH_RATIO else "常规")


def load_cache(path) -> dict:
    if not path or not Path(path).expanduser().exists():
        return {}
    try:
        data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    good = {}
    for account, entry in (data.items() if isinstance(data, dict) else []):
        try:
            datetime.fromisoformat(entry["date"])
            if entry["baseline"] == "capped" or isinstance(entry["baseline"], int):
                good[account] = entry
        except (KeyError, TypeError, ValueError):
            continue
    return good


def save_cache(path, cache: dict, notes: list):
    try:
        target = Path(path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, target)
    except OSError as error:
        notes.append(f"账号基线缓存没存上：{error}")


def _safe(client: Client, result: dict, endpoint, body, label):
    try:
        return client.call(endpoint, body, label)
    except Stop:
        return None
    except Exception as error:
        result["missing"].append(client.redact(error))
        return None


def run(keywords, client: Client, result: dict, max_articles: int = 15, max_accounts: int = 5, cache: dict = None,
        today: datetime = None, now: float = None) -> dict:
    """Fills `result` in place, so whatever was paid for survives an unexpected stop."""
    cache = cache if cache is not None else {}
    today = today or datetime.now()
    seen = set()
    per_keyword = []
    for keyword in keywords:
        payload = _safe(client, result, "web_search", {"mode": 1, "keyword": keyword, "search_type": 1,
                        "publish_time_type": 3, "sort_type": 2, "currentPage": 1, "offset": 0,
                        "cookies_buffer": "", "verifycode": ""}, f"搜一搜：{keyword}")
        found = []
        for item in search_items(payload):
            if item["title"] not in seen:            # reposts count once
                seen.add(item["title"])
                found.append({**item, "keyword": keyword})
        per_keyword.append(found)
    # Every keyword gets its share of the article budget; leftovers go to whoever has more.
    # (10-14: the first keyword filled the whole budget and the second search was paid for nothing.)
    share = -(-max_articles // max(len(per_keyword), 1))
    picked = [found[:share] for found in per_keyword]
    rest = [item for found in per_keyword for item in found[share:]]
    result["items"] = [item for group in picked for item in group]
    result["items"] += rest[:max(0, max_articles - len(result["items"]))]
    result["items"] = result["items"][:max_articles]
    for item in result["items"]:
        zan = _safe(client, result, "read_zan", {"url": item["url"], "verifycode": ""}, f"阅读：{item['title'][:20]}")
        data = zan.get("data") if isinstance(zan, dict) and isinstance(zan.get("data"), dict) else {}
        item["read"], item["likes"], item["looking"] = _int(data.get("read")), _int(data.get("zan")), _int(data.get("looking"))
    reads = {}
    for item in result["items"]:
        if isinstance(item.get("read"), int) and item["read"] < CAPPED and item["account"]:
            reads[item["account"]] = max(reads.get(item["account"], 0), item["read"])
    searched = {i["url"] for i in result["items"]}
    for account in sorted(reads, key=lambda a: -reads[a])[:max_accounts]:
        cached = cache.get(account)
        if cached and (today - datetime.fromisoformat(cached["date"])).days <= CACHE_DAYS:
            result["accounts"][account] = {**cached, "from_cache": True}
            continue
        history = _safe(client, result, "post_history", {"nickname": account, "ghid": "", "url": "", "offset": "",
                        "verifycode": ""}, f"发文列表：{account}")
        if history is None:
            continue
        leads = [a for a in lead_articles(history.get("data"), now=now) if a["url"] not in searched][:BASELINE_READS]
        base_reads = []
        for lead in leads:
            zan = _safe(client, result, "read_zan", {"url": lead["url"], "verifycode": ""}, f"平时水平：{account}")
            data = zan.get("data") if isinstance(zan, dict) and isinstance(zan.get("data"), dict) else {}
            base_reads.append(_int(data.get("read")))
        base = baseline_of(base_reads)
        entry = {"baseline": base, "sample": len([r for r in base_reads if isinstance(r, int)]), "date": today.strftime("%Y-%m-%d")}
        result["accounts"][account] = entry
        if base is not None:
            cache[account] = entry
    return result


def finish(result: dict, client: Client):
    for item in result["items"]:
        item["ratio"], item["band"] = judge(item.get("read"), (result["accounts"].get(item["account"]) or {}).get("baseline"))
    if client.stop_reason:
        result["missing"].append(f"{client.stop_reason}，后面没再取")
    result["missing"] += client.notes


def render(result: dict, client: Client, state: str, when: datetime) -> str:
    items = result.get("items", [])
    high = [i for i in items if i.get("band") == "小号高表现"]
    lines = [
        f"# 数据参照：{'、'.join(result.get('keywords', []))}",
        "",
        "- 数据源：极致了公众号数据接口（微信搜一搜，近半年最热；阅读数为取数当时的数字）",
        f"- 取数时间：{when.strftime('%Y-%m-%d %H:%M')}",
        f"- 口径：倍数 = 这篇阅读 ÷ 该号近 {BASELINE_DAYS} 天头条阅读的中位数（最多 {BASELINE_READS} 篇）；10 万以上接口只返回 100001，这类文章和账号不比；倍数 ≥ {HIGH_RATIO:g} 且阅读 ≥ {MIN_READ:,} 记为小号高表现（两个数都是起始假设，跑约十篇后按实际分布调）",
        f"- 样本量：文章 {len(items)} 篇（同题转载只算一篇），算出倍数的 {len([i for i in items if i.get('ratio') is not None])} 篇，小号高表现 {len(high)}/{len(items)} 篇" + ("（样本不到 5 篇，仅供参考）" if len(items) < 5 else ""),
        f"- 状态：{state}；本次花费 {client.spent:.2f} 元" + (f"，余额 {client.remain:.2f} 元" if client.remain is not None else ""),
        "",
        "这是读者反应的参照，不是撞题扫描（不进第 6 问的计数，不能拿来说\"没撞题\"）；不给标题打分，不替作者做决定；小号高表现文章的标题和写法只放在旁边对照。",
        "\"对题\"一列由总调度逐行填：对题 / 相邻 / 不相关。只有对题的行能当参照；关键词搜偏了（不相关占多数）就换读者会搜的说法，别拿偏的结果下结论。",
        "",
    ]
    if result.get("missing"):
        lines += ["缺的：" + "；".join(result["missing"]), ""]
    if items:
        lines += ["| 对题 | 倍数 | 相对本号分档 | 阅读 | 该号平时 | 账号 | 标题 | 日期 | 关键词 |", "|---|---|---|---|---|---|---|---|---|"]
        for i in sorted(items, key=lambda i: (-(i.get("ratio") or 0), -(i.get("read") or 0))):
            base = (result["accounts"].get(i["account"]) or {}).get("baseline")
            base_text = "10万+" if base == "capped" else (f"{base:,}" if isinstance(base, int) else "未知")
            read = i.get("read")
            read_text = "10万+" if isinstance(read, int) and read >= CAPPED else (f"{read:,}" if isinstance(read, int) else "未取到")
            ratio_text = f"{i['ratio']:.2f}" if i.get("ratio") is not None else "—"
            lines.append(f"| 待判 | {ratio_text} | {i['band']} | {read_text} | {base_text} | {i['account']} | "
                         f"[{i['title'].replace('|', '｜')}]({i['url']}) | {i.get('date', '')} | {i.get('keyword', '')} |")
    return "\n".join(lines) + "\n"


def report_path(folder: Path, keywords, when: datetime) -> Path:
    stem = "_".join(re.sub(r"[\\/:*?\"<>|\s]+", "-", k) for k in keywords)[:40]
    return folder / f"{REPORT_PREFIX}_{stem}_{when.strftime('%Y-%m-%d')}.md"


def write_page(path: Path, text: str, raw=None) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        if raw is not None:
            path.with_suffix(".json").write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
        return True
    except OSError as error:
        print(f"报告没写上：{error}", file=sys.stderr)
        return False


def paid_today(folder: Path, keywords, when: datetime) -> list:
    log = folder / SPEND_LOG
    if not log.exists():
        return []
    day = when.strftime("%Y-%m-%d")
    done = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("endpoint") == "web_search" and str(entry.get("time", "")).startswith(day):
            done += [k for k in keywords if entry.get("label") == f"搜一搜：{k}"]
    return sorted(set(done))


def _bounded_int(text, low, high):
    value = int(text)
    if not low <= value <= high:
        raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
    return value


def _cap(text):
    value = float(text)
    if not math.isfinite(value) or not 0 < value <= 20:
        raise argparse.ArgumentTypeError("cap must be a number above 0 and at most 20 (yuan)")
    return value


def main(argv=None, post=http_post, env=None, sleep=time.sleep) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dir", required=True, help="the article's process folder")
    parser.add_argument("--keyword", action="append", required=True, help="up to 3, de-duplicated; each search costs 0.5 yuan")
    parser.add_argument("--cap", type=_cap, default=3.0, help="spend cap for this run, in yuan (default 3, at most 20)")
    parser.add_argument("--max-articles", type=lambda t: _bounded_int(t, 1, 30), default=15)
    parser.add_argument("--max-accounts", type=lambda t: _bounded_int(t, 0, 10), default=5)
    parser.add_argument("--key-env", default="DAJIALA_API_KEY")
    parser.add_argument("--env-file", help="a KEY=value file holding the key, if it is not in the environment")
    parser.add_argument("--ledger", help="a shared spend log to append every paid call to as well")
    parser.add_argument("--cache", help="account baseline cache (json); reused for 90 days")
    parser.add_argument("--dry-run", action="store_true", help="check key and balance (free) and print the worst-case cost")
    parser.add_argument("--force", action="store_true", help="run even if these keywords were already paid for today")
    args = parser.parse_args(argv)
    env = os.environ if env is None else env
    keywords = list(dict.fromkeys(k.strip() for k in args.keyword if k.strip()))[:3]
    if not keywords:
        parser.error("give at least one non-empty --keyword")
    folder = Path(args.dir).expanduser()
    when = datetime.now()
    page = report_path(folder, keywords, when)

    def not_fetched(reason: str) -> int:
        write_page(page, f"# 数据参照：{'、'.join(keywords)}\n\n- 状态：未取数（{reason}）。本篇按经验和联网搜索继续。\n")
        print(f"未取数：{reason}；{page}")
        return 0

    key = env.get(args.key_env, "")
    if not key and args.env_file:
        try:
            key = read_env_file(Path(args.env_file)).get(args.key_env, "")
        except OSError:
            key = ""
    if not key:
        return not_fetched(f"没有找到 {args.key_env}")
    repeat = paid_today(folder, keywords, when)
    if repeat and not args.force and not args.dry_run:
        print(f"这些关键词今天已经付费查过：{'、'.join(repeat)}。结果在 {folder}；确实要重查加 --force。")
        return 0
    worst = (len(keywords) * PRICE["web_search"] + args.max_articles * PRICE["read_zan"]
             + args.max_accounts * (PRICE["post_history"] + BASELINE_READS * PRICE["read_zan"]))
    client = Client(key, args.cap, post=post, gap=1.0 if post is http_post else 0, spend_log=folder / SPEND_LOG,
                    ledger=Path(args.ledger) if args.ledger else None, sleep=sleep)
    try:
        folder.mkdir(parents=True, exist_ok=True)
        remain = client.balance()
    except Exception as error:   # network, bad key: a reference must never block the article
        return not_fetched(client.redact(error))
    if args.dry_run:
        print(json.dumps({"余额": remain, "最多花费": round(min(worst, args.cap), 2), "上限": args.cap}, ensure_ascii=False))
        return 0
    if remain < min(worst, args.cap):
        return not_fetched(f"余额 {remain:.2f} 元，不够这一轮")
    cache = load_cache(args.cache)
    result = {"keywords": keywords, "items": [], "accounts": {}, "missing": []}
    interrupted = False
    try:
        run(keywords, client, result, args.max_articles, args.max_accounts, cache=cache)
    except KeyboardInterrupt:
        interrupted = True
        result["missing"].append("被手动中断")
    except Exception as error:
        result["missing"].append(client.redact(f"意外出错：{error}"))
    finally:
        finish(result, client)
        if args.cache and cache:
            save_cache(args.cache, cache, result["missing"])
        state = "降级" if result["missing"] else "已取数"
        write_page(page, render(result, client, state, when), raw=result)
        print(json.dumps({"状态": state, "花费": client.spent, "余额": client.remain, "文章": len(result["items"]),
                          "报告": str(page)}, ensure_ascii=False))
    return 130 if interrupted else 0


if __name__ == "__main__":
    sys.exit(main())
