#!/usr/bin/env python3
"""Run one model call and stop it only when it has gone silent (references/models.md, "Watching a call").

The command runs in a fresh empty folder with no input; stdout goes to --out, stderr to <out>.err.
Until --check-after seconds pass the call is never stopped. After that it is stopped (SIGKILL to its
whole process group) only once it has been silent for --silent seconds in a row: the output files and
every --watch path unchanged, and its processes used less than --cpu-min seconds of CPU in that window.
--answer-idle N ends a call whose output is non-empty and unchanged for N seconds (some CLIs keep running
after their answer). The last line of <out>.err and of stdout says how it ended.

Exit code: the command's own code when it exits; 0 when ended by --answer-idle; 124 when stopped silent.

Example:
  python3 scripts/run_watched.py --out pens/06-draft-opus46-v1.md --check-after 1500 --watch-claude-log \\
      -- env CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000 claude -p "$(cat pens/06-draft-brief.md)" --model claude-opus-4-6
"""
import argparse
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from collections import deque
from pathlib import Path


def parse_cputime(text):
    """ps TIME field ([[dd-]hh:]mm:ss[.ss]) to seconds."""
    text = text.strip()
    days = 0
    if "-" in text:
        d, text = text.split("-", 1)
        days = int(d)
    parts = [float(p) for p in text.split(":")]
    secs = 0.0
    for p in parts:
        secs = secs * 60 + p
    return days * 86400 + secs


def linux_tree_cpu(root_pid, proc_root=Path("/proc")):
    """Read subsecond Linux CPU ticks; ps TIME truncates to seconds on procps.

    Return None if procfs or the root is unavailable so other systems retain ps.
    Names may contain spaces and ')' characters: fields follow the final ')'.
    """
    try:
        ticks = os.sysconf("SC_CLK_TCK")
        if ticks <= 0:
            return None
        entries = list(proc_root.iterdir())
    except (OSError, ValueError, AttributeError):
        return None
    children, cpu = {}, {}
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            fields = (entry / "stat").read_text().rsplit(")", 1)[1].split()
            pid, parent = int(entry.name), int(fields[1])
            cpu[pid] = (int(fields[11]) + int(fields[12])) / ticks
        except (OSError, ValueError, IndexError):
            continue  # A process can exit between directory enumeration and reading stat.
        children.setdefault(parent, []).append(pid)
    if root_pid not in cpu:
        return None
    total, stack, seen = 0.0, [root_pid], set()
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        total += cpu.get(pid, 0.0)
        stack.extend(children.get(pid, []))
    return total


def tree_cpu(root_pid):
    """CPU seconds of the live process tree: Linux procfs ticks, portable ps fallback."""
    if sys.platform.startswith("linux"):
        precise = linux_tree_cpu(root_pid)
        if precise is not None:
            return precise
    try:
        out = subprocess.run(["ps", "-A", "-o", "pid=,ppid=,time="], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    children, cpu = {}, {}
    for line in out.splitlines():
        fields = line.split()
        if len(fields) < 3:
            continue
        try:
            pid, ppid = int(fields[0]), int(fields[1])
            cpu[pid] = parse_cputime(fields[2])
        except ValueError:
            continue
        children.setdefault(ppid, []).append(pid)
    total, stack, seen = 0.0, [root_pid], set()
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        total += cpu.get(pid, 0.0)
        stack.extend(children.get(pid, []))
    return total


def path_state(path):
    """(newest mtime, total size) of a file, or of every file under a folder; (0, 0) when missing."""
    p = Path(path)
    if p.is_file():
        st = p.stat()
        return (st.st_mtime, st.st_size)
    newest, size = 0.0, 0
    if p.is_dir():
        for f in p.rglob("*"):
            try:
                if f.is_file():
                    st = f.stat()
                    newest, size = max(newest, st.st_mtime), size + st.st_size
            except OSError:
                continue
    return (newest, size)


def claude_log_dirs(workdir):
    """Claude Code keeps a session log per working folder under ~/.claude/projects/, named from the path."""
    base = Path.home() / ".claude" / "projects"
    names = {re.sub(r"[^A-Za-z0-9]", "-", p) for p in (str(workdir), os.path.realpath(workdir))}
    return [str(base / n) for n in sorted(names)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="file for the call's output")
    ap.add_argument("--check-after", type=float, default=600, help="seconds before any stop is considered (default 600)")
    ap.add_argument("--silent", type=float, default=300, help="seconds of silence in a row that stop the call (default 300)")
    ap.add_argument("--cpu-min", type=float, default=1.0, help="CPU seconds within the silent window that still count as working (default 1.0)")
    ap.add_argument("--answer-idle", type=float, default=0, help="end once output is non-empty and unchanged this long; 0 = off (agy: 90)")
    ap.add_argument("--watch", action="append", default=[], help="file or folder whose growth counts as activity; repeatable")
    ap.add_argument("--watch-claude-log", action="store_true", help="also watch the Claude Code session log of the working folder")
    ap.add_argument("--poll", type=float, default=5, help="seconds between checks (default 5)")
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="-- then the command")
    args = ap.parse_args(argv)
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        ap.error("give the command after --")

    out = Path(args.out).expanduser().resolve()
    err = out.with_name(out.name + ".err")
    workdir = tempfile.mkdtemp(prefix="pw_run_")
    watch = list(args.watch) + (claude_log_dirs(workdir) if args.watch_claude_log else [])

    with open(out, "wb") as fo, open(err, "wb") as fe:
        proc = subprocess.Popen(cmd, cwd=workdir, stdin=subprocess.DEVNULL, stdout=fo, stderr=fe, start_new_session=True)
    start = time.time()
    last_activity = start
    last_state = None
    out_changed_at, last_out = start, None
    cpu_samples = deque()
    ended = None

    while True:
        try:
            code = proc.wait(timeout=args.poll)
            ended = f"exited with code {code}"
            break
        except subprocess.TimeoutExpired:
            pass
        now = time.time()
        out_state = path_state(out)
        state = (out_state, path_state(err), tuple(path_state(w) for w in watch))
        if state != last_state:
            last_activity, last_state = now, state
        if out_state != last_out:
            out_changed_at, last_out = now, out_state
        cpu = tree_cpu(proc.pid)
        if cpu is not None:
            cpu_samples.append((now, cpu))
            while len(cpu_samples) > 1 and cpu_samples[1][0] <= now - args.silent:
                cpu_samples.popleft()
        if args.answer_idle and out_state[1] > 0 and now - out_changed_at >= args.answer_idle:
            ended, code = f"answer idle {now - out_changed_at:.0f}s, stopped", 0
            break
        if now - start < args.check_after or now - last_activity < args.silent:
            continue
        window_full = cpu_samples and cpu_samples[0][0] <= now - args.silent + args.poll
        cpu_used = cpu_samples[-1][1] - cpu_samples[0][1] if cpu_samples else 0.0
        if window_full and cpu_used >= args.cpu_min:
            continue
        ended, code = f"silent {now - last_activity:.0f}s, stopped", 124
        break

    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
    try:
        os.rmdir(workdir)
        where = ""
    except OSError:
        where = f"; the call left files in {workdir}"
    line = f"ELAPSED {time.time() - start:.0f}s; {ended}{where}"
    with open(err, "a", encoding="utf-8") as fe:
        fe.write("\n" + line + "\n")
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
