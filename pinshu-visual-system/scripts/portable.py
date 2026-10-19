"""Small cross-platform helpers (macOS, Linux, Windows). Standard library only.

- append_line: append one line under an exclusive lock (fcntl on macOS/Linux, msvcrt on Windows).
- local_now: an aware local timestamp that needs no time-zone database (Windows has none without tzdata).
- ensure_utf8_mode: on Windows, re-run the current script in Python's UTF-8 mode, because these scripts
  read and write Chinese text and Windows otherwise uses the local code page.
"""
from __future__ import annotations

from datetime import datetime
import os
import subprocess
import sys
from pathlib import Path

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
try:
    import msvcrt
except ImportError:  # macOS, Linux
    msvcrt = None


def append_line(path: Path, line: str) -> None:
    path = Path(path)
    if fcntl is not None:
        with path.open('a', encoding='utf-8') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            handle.write(line if line.endswith('\n') else line + '\n')
        return
    # Windows: lock byte 0 of a separate lock file, so every writer locks the same spot however long the log grows.
    with open(str(path) + '.lock', 'a+b') as guard:
        if msvcrt is not None:
            guard.seek(0)
            msvcrt.locking(guard.fileno(), msvcrt.LK_LOCK, 1)
        try:
            with path.open('a', encoding='utf-8') as handle:
                handle.write(line if line.endswith('\n') else line + '\n')
        finally:
            if msvcrt is not None:
                guard.seek(0)
                msvcrt.locking(guard.fileno(), msvcrt.LK_UNLCK, 1)


def lock(handle) -> None:
    """Exclusive lock on an open file; released when the file closes."""
    if fcntl is not None:
        fcntl.flock(handle, fcntl.LOCK_EX)
    elif msvcrt is not None:
        position = handle.tell()
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        handle.seek(position)


def local_now(zone: str = 'Asia/Kuala_Lumpur') -> datetime:
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(zone))
    except Exception:  # no tz database (Windows without tzdata): fall back to this computer's own offset
        return datetime.now().astimezone()


def ensure_utf8_mode(platform: str | None = None, utf8_mode: int | None = None) -> None:
    platform = os.name if platform is None else platform
    utf8_mode = sys.flags.utf8_mode if utf8_mode is None else utf8_mode
    if platform != 'nt' or utf8_mode or os.environ.get('PINSHU_UTF8_REEXEC'):
        return
    env = dict(os.environ, PYTHONUTF8='1', PINSHU_UTF8_REEXEC='1')
    raise SystemExit(subprocess.call([sys.executable, '-X', 'utf8', *sys.argv], env=env))
