#!/usr/bin/env python3
"""Per-article stage log: where the time went, what failed, where to resume.

One append-only file per article, 阶段记录.jsonl in the article's process folder. The organizer logs
each step as it starts and ends; `summary` answers "which step was slowest, how many retries, how long
we waited, where a person stepped in, and if it stopped, where it stopped and where to resume".

  python3 scripts/stage_log.py --dir <process folder> start "5 正文" --kind machine --model "Claude Opus 4.6"
  python3 scripts/stage_log.py --dir <process folder> end "5 正文" --result ok
  python3 scripts/stage_log.py --dir <process folder> end "证据截图" --result failed --note "X 帖子超时" \
      --resume-from "证据截图" --manual-handoff <人工截图指引.md>
  python3 scripts/stage_log.py --dir <process folder> summary        # also writes 阶段耗时账.md
  python3 scripts/stage_log.py --dir <process folder> start "6 补料" --at 14:05   # forgot to log the start: give the real time

--at takes HH:MM (today) or YYYY-MM-DD HH:MM; it may not lie in the future, and an end may not lie before its start.
A back-dated event is marked "backfilled" in the log, so the timing record shows it was written afterwards.

kind: machine (a model or script is working), wait (waiting on something outside: a queue, a login,
a browser), human (the author reading or deciding). result: ok, or one of the failure kinds below.
The failure fields (status, failed_stage, last_successful_stage, error, resume_from, manual_handoff)
use the same names as the visual Skill's 流程核验.json, so one reader understands both.
Plain Python 3.9+, no third-party packages.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

LOG_NAME = "阶段记录.jsonl"
REPORT_NAME = "阶段耗时账.md"
KINDS = ("machine", "wait", "human")
KIND_LABEL = {"machine": "机器在跑", "wait": "等外部", "human": "等人"}
FAILURES = ("failed", "empty", "quota", "timeout", "login", "blocked", "skipped")
RESULT_LABEL = {"ok": "完成", "failed": "失败", "empty": "空回复", "quota": "额度不足", "timeout": "超时",
                "login": "未登录", "blocked": "卡住待人工", "skipped": "跳过"}


def _now(now=None) -> datetime:
    return (now or datetime.now()).astimezone()


def parse_at(value: str, now=None) -> datetime:
    """A back-dated time: HH:MM today, or YYYY-MM-DD HH:MM (a T between date and time also works)."""
    current = _now(now)
    text = value.strip().replace("T", " ")
    try:
        if len(text) <= 5:
            clock = datetime.strptime(text, "%H:%M")
            moment = current.replace(hour=clock.hour, minute=clock.minute, second=0, microsecond=0)
        else:
            moment = datetime.fromisoformat(text)
            moment = moment.replace(tzinfo=current.tzinfo) if moment.tzinfo is None else moment.astimezone(current.tzinfo)
    except ValueError:
        raise ValueError(f"--at must be HH:MM or YYYY-MM-DD HH:MM, got {value!r}")
    if moment > current:
        raise ValueError(f"--at {value} lies in the future")
    return moment


def append(folder: Path, event: dict, now=None, at=None) -> dict:
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError(f"Process folder does not exist: {folder}")
    moment = parse_at(at, now) if at else _now(now)
    if at:
        event = {**event, "backfilled": True}
    event = {"time": moment.isoformat(timespec="seconds"), **{k: v for k, v in event.items() if v not in (None, "")}}
    with (folder / LOG_NAME).open("a", encoding="utf-8") as log:
        log.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def start(folder, stage, kind="machine", model=None, note=None, now=None, at=None):
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    opened = [e for e in read(folder) if e.get("stage") == stage]
    if opened and opened[-1]["event"] == "start":
        raise ValueError(f"'{stage}' is still running; end it first, or give a parallel run its own name (e.g. '{stage} · B')")
    return append(folder, {"event": "start", "stage": stage, "kind": kind, "model": model, "note": note}, now, at)


def end(folder, stage, result="ok", note=None, resume_from=None, manual_handoff=None, now=None, at=None):
    if result != "ok" and result not in FAILURES:
        raise ValueError(f"result must be ok or one of {FAILURES}")
    if result == "skipped" and not (note or "").strip():
        raise ValueError("A skipped step needs --note: what was delivered instead (e.g. a to-capture list) and why")
    opened = [e for e in read(folder) if e.get("stage") == stage]
    if not opened or opened[-1]["event"] != "start":
        raise ValueError(f"'{stage}' was not started (or already ended); log `start` first (with --at if you forgot)")
    if at and parse_at(at, now) < datetime.fromisoformat(opened[-1]["time"]):
        raise ValueError(f"--at {at} lies before '{stage}' started")
    return append(folder, {"event": "end", "stage": stage, "result": result, "note": note,
                           "resume_from": resume_from, "manual_handoff": manual_handoff}, now, at)


def read(folder) -> list:
    path = Path(folder) / LOG_NAME
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize(folder) -> dict:
    events = read(folder)
    stages, order, open_runs = {}, [], {}
    model_calls = {}
    last_ok, open_failures, downgrades = None, {}, {}  # unresolved failures and documented fallbacks, per step
    for event in events:
        stage = event["stage"]
        if stage not in stages:
            stages[stage] = {"stage": stage, "attempts": 0, "seconds": {k: 0.0 for k in KINDS}, "results": {}, "models": []}
            order.append(stage)
        row = stages[stage]
        if event["event"] == "start":
            row["attempts"] += 1
            open_runs[stage] = event
            if event.get("model") and event["model"] not in row["models"]:
                row["models"].append(event["model"])
            continue
        began = open_runs.pop(stage, None)
        if began:
            seconds = (datetime.fromisoformat(event["time"]) - datetime.fromisoformat(began["time"])).total_seconds()
            row["seconds"][began.get("kind", "machine")] += max(seconds, 0.0)
            if began.get("model"):
                model_calls.setdefault(began["model"], {}).setdefault(event["result"], 0)
                model_calls[began["model"]][event["result"]] += 1
        row["results"][event["result"]] = row["results"].get(event["result"], 0) + 1
        if event["result"] == "ok":
            last_ok = stage
            open_failures.pop(stage, None)  # this step recovered; others stay open
            downgrades.pop(stage, None)
        elif event["result"] == "skipped":
            # A documented fallback (e.g. no browser -> a to-capture list) is not a failure, but stays visible.
            open_failures.pop(stage, None)
            downgrades[stage] = event
        else:
            open_failures.pop(stage, None)
            open_failures[stage] = event
    rows = [stages[s] for s in order]
    for row in rows:
        row["retries"] = max(row["attempts"] - 1, 0)
        row["total_seconds"] = round(sum(row["seconds"].values()), 1)
        row["seconds"] = {k: round(v, 1) for k, v in row["seconds"].items()}
    totals = {k: round(sum(r["seconds"][k] for r in rows), 1) for k in KINDS}
    slowest = max(rows, key=lambda r: r["total_seconds"], default=None)
    human_stops = [r["stage"] for r in rows if r["seconds"]["human"] > 0]
    failures = list(open_failures.values())
    last_failure = failures[-1] if failures else None
    if open_runs:
        status = "RUNNING"
    elif failures:
        status = "FAILED" if any(f["result"] != "blocked" for f in failures) else "BLOCKED"
    else:
        status = "OK" if rows else "EMPTY"
    report = {"status": status, "stages": rows, "totals_seconds": totals,
              "slowest_stage": slowest["stage"] if slowest else None, "human_stops": human_stops,
              "model_calls": model_calls, "still_running": sorted(open_runs),
              "downgraded": [{"stage": d["stage"], "note": d.get("note", "")} for d in downgrades.values()],
              "unresolved": [{"stage": f["stage"], "result": f["result"], "error": f.get("note", RESULT_LABEL[f["result"]]),
                              "resume_from": f.get("resume_from") or f["stage"], "manual_handoff": f.get("manual_handoff")}
                             for f in failures]}
    if last_failure:
        report.update(failed_stage=last_failure["stage"], last_successful_stage=last_ok,
                      error=last_failure.get("note", RESULT_LABEL[last_failure["result"]]),
                      resume_from=last_failure.get("resume_from") or last_failure["stage"],
                      manual_handoff=last_failure.get("manual_handoff"))
    return report


def _minutes(seconds: float) -> str:
    return f"{seconds / 60:.1f} 分钟"


def render(report: dict) -> str:
    lines = ["# 阶段耗时账", "", "由 `stage_log.py summary` 生成；原始记录在同目录 `" + LOG_NAME + "`。", ""]
    state = {"OK": "全部步骤已结束", "RUNNING": "还有步骤没结束：" + "、".join(report["still_running"]),
             "FAILED": "停在失败", "BLOCKED": "卡住，等人工", "EMPTY": "还没有记录"}[report["status"]]
    lines += ["状态：" + state]
    if report["downgraded"]:
        lines.append("降级交付（没失败，但这一步没按原样做完）：" + "；".join(f"{d['stage']}（{d['note']}）" for d in report["downgraded"]))
    if report.get("failed_stage"):
        lines += ["", f"- 失败在：{report['failed_stage']}（{report['error']}）",
                  f"- 最后成功：{report.get('last_successful_stage') or '无'}",
                  f"- 从这里接着做：{report['resume_from']}"]
        if report.get("manual_handoff"):
            lines.append(f"- 人工接手说明：{report['manual_handoff']}")
        if len(report["unresolved"]) > 1:
            lines.append("- 还没解决的失败一共 %d 处：" % len(report["unresolved"]) + "；".join(
                f"{u['stage']}（{u['error']}）" for u in report["unresolved"]))
    t = report["totals_seconds"]
    lines += ["", f"合计：机器在跑 {_minutes(t['machine'])}，等外部 {_minutes(t['wait'])}，等人 {_minutes(t['human'])}。",
              f"最慢一步：{report['slowest_stage'] or '无'}。人工停点：{'、'.join(report['human_stops']) or '无'}。", "",
              "| 步骤 | 次数 | 重跑 | 机器在跑 | 等外部 | 等人 | 结果 | 模型 |", "|---|---|---|---|---|---|---|---|"]
    for row in report["stages"]:
        results = "、".join(f"{RESULT_LABEL.get(k, k)}×{v}" for k, v in row["results"].items()) or "未结束"
        s = row["seconds"]
        lines.append(f"| {row['stage']} | {row['attempts']} | {row['retries']} | {_minutes(s['machine'])} | {_minutes(s['wait'])} | "
                     f"{_minutes(s['human'])} | {results} | {'、'.join(row['models']) or '—'} |")
    if report["model_calls"]:
        lines += ["", "模型调用：" + "；".join(
            f"{model}：" + "、".join(f"{RESULT_LABEL.get(k, k)}×{v}" for k, v in calls.items())
            for model, calls in report["model_calls"].items())]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="写稿阶段耗时与失败记录")
    parser.add_argument("--dir", type=Path, required=True, help="the article's process folder")
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("start")
    s.add_argument("stage")
    s.add_argument("--kind", choices=KINDS, default="machine")
    s.add_argument("--model")
    s.add_argument("--note")
    s.add_argument("--at", help="the real start time if you forgot to log it: HH:MM or YYYY-MM-DD HH:MM")
    e = sub.add_parser("end")
    e.add_argument("stage")
    e.add_argument("--result", choices=("ok",) + FAILURES, default="ok")
    e.add_argument("--note")
    e.add_argument("--resume-from")
    e.add_argument("--manual-handoff")
    e.add_argument("--at", help="the real end time if you forgot to log it: HH:MM or YYYY-MM-DD HH:MM")
    m = sub.add_parser("summary")
    m.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            start(args.dir, args.stage, args.kind, args.model, args.note, at=args.at)
        elif args.command == "end":
            end(args.dir, args.stage, args.result, args.note, args.resume_from, args.manual_handoff, at=args.at)
        else:
            report = summarize(args.dir)
            (args.dir / REPORT_NAME).write_text(render(report), encoding="utf-8")
            print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    except ValueError as exc:
        parser.exit(1, f"stage_log.py: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
