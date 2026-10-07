"""Find pinshu-video-core, the shared base this skill runs on.

Since 2026-10-07 the scripts every Pinshu video type shares live in
pinshu-video-core/scripts. This package keeps thin files under the same names so
`python3 $S/<script>.py ...` keeps working when the core is installed beside it
or explicitly configured with PINSHU_VIDEO_CORE.
"""
import importlib.util
import os
import runpy
import sys


def scripts_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [os.environ.get("PINSHU_VIDEO_CORE")]
    for base in (here, os.path.realpath(here)):
        candidates.append(os.path.join(os.path.dirname(os.path.dirname(base)), "pinshu-video-core"))
    for candidate in candidates:
        if candidate and os.path.isfile(os.path.join(candidate, "scripts", "common.py")):
            return os.path.join(os.path.abspath(candidate), "scripts")
    raise SystemExit(
        "pinshu-video-core not found. Install it next to this skill "
        "(~/.agents/skills/pinshu-video-core) or set PINSHU_VIDEO_CORE=/path/to/pinshu-video-core."
    )


def run(name):
    directory = scripts_dir()
    sys.path.insert(0, directory)
    runpy.run_path(os.path.join(directory, name), run_name="__main__")


def load(name, alias):
    spec = importlib.util.spec_from_file_location(alias, os.path.join(scripts_dir(), name))
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module
