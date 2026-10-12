#!/usr/bin/env python3
"""One-time self-check for a new user of the pinshu-write Skill.

Prints one line per item: OK / MISSING / OPTIONAL-MISSING / UNVERIFIED: what, why it matters, how to fix.
UNVERIFIED means found but not proven to work (for example a CLI on PATH that may not be logged in).
Exit 0 when the core is fine (optional items may be missing); exit 1 when a core item is missing.
Core: Python 3.9+ and the core scripts. Optional: a configuration file (without it the Skill asks for the account, reader and folders at the start), a second-vendor model CLI,
the visual Skill. Plain Python 3.9+, no third-party packages.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

CORE_SCRIPTS = ("audit_draft", "export_article", "fix_quotes")
# Command -> vendors whose models it can reach. agy (Antigravity) offers both Google and Anthropic models.
MODEL_CLIS = {
    "claude": ("Anthropic",),
    "gemini": ("Google",),
    "agy": ("Google", "Anthropic"),
    "codex": ("OpenAI",),
    "kimi": ("Moonshot",),
    "qwen": ("Alibaba",),
    "deepseek": ("DeepSeek",),
}
CONFIG_NAME = "pinshu-write.yaml"
CONFIG_ENV = "PINSHU_WRITE_CONFIG"
CONFIG_TEMPLATE = "templates/config.example.yaml"
# Top-level keys the Skill needs before it can start without asking: account, reader (inside accounts),
# drafts folder, ready folder.
CONFIG_KEYS = ("accounts", "drafts_folder", "ready_folder")
VISUAL_SKILL = "pinshu-visual-system"


def check_python(version=None):
    version = version or sys.version_info[:3]
    text = ".".join(str(part) for part in version)
    if tuple(version) >= (3, 9):
        return {"status": "OK", "what": "Python version", "detail": f"{text} (core needs 3.9+)"}
    return {"status": "MISSING", "what": "Python version", "detail": f"{text} is too old; the core scripts need 3.9+. Fix: install Python 3.9 or newer and run this script with it."}


def check_scripts(scripts_dir: Path):
    results = []
    for name in CORE_SCRIPTS:
        path = scripts_dir / f"{name}.py"
        if not path.is_file():
            results.append({"status": "MISSING", "what": f"script {name}.py", "detail": f"not found in {scripts_dir}. Fix: re-install the Skill folder."})
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"_pinshu_check_{name}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            results.append({"status": "OK", "what": f"script {name}.py", "detail": "importable, no third-party packages needed"})
        except Exception as exc:  # any import failure means the script is unusable
            results.append({"status": "MISSING", "what": f"script {name}.py", "detail": f"cannot be imported ({type(exc).__name__}: {exc}). Fix: use Python 3.9+ and a complete copy of the Skill."})
    return results


def find_config(skill_dir: Path, config: Path = None, env=None, cwd: Path = None):
    """Search order: --config, env PINSHU_WRITE_CONFIG, ./pinshu-write.yaml in the working directory,
    then the Skill folder (kept for compatibility). Returns (path or None, searched list)."""
    env = os.environ if env is None else env
    cwd = Path.cwd() if cwd is None else cwd
    candidates = []
    if config:
        candidates.append(config.expanduser())
    if env.get(CONFIG_ENV):
        candidates.append(Path(env[CONFIG_ENV]).expanduser())
    candidates += [cwd / CONFIG_NAME, skill_dir / CONFIG_NAME]
    candidates = list(dict.fromkeys(candidates))  # drop duplicates, keep order
    for path in candidates:
        if path.is_file():
            return path, candidates
    return None, candidates


def _config_problems(text: str):
    """Plain-text look at the config (no YAML library). Returns a list of missing keys, or None when
    the text cannot be understood."""
    lines = [l.rstrip() for l in text.splitlines()]
    top = {}
    for index, line in enumerate(lines):
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*(?:#.*)?$", line)
        if match:
            top[match.group(1)] = (index, match.group(2))
    if not top:
        return None
    missing = []
    for key in CONFIG_KEYS:
        if key not in top:
            missing.append(key)
            continue
        index, value = top[key]
        block = []
        for line in lines[index + 1:]:
            if re.match(r"^\S", line):
                break
            if line.strip() and not line.strip().startswith("#"):
                block.append(line.strip())
        if key == "accounts":
            if value not in ("", "[]") or not block:
                missing.append(key)
                continue
            for field in ("name", "reader"):
                filled = any(re.match(rf"^(?:-\s*)?{field}:\s*[^\s#]", item) for item in block)
                if not filled:
                    missing.append(f"accounts[].{field}")
        elif not value or value in ("[]", "~", "null", '""', "''"):
            missing.append(key)
    return missing


def check_config(skill_dir: Path, config: Path = None, env=None, cwd: Path = None):
    path, searched = find_config(skill_dir, config, env, cwd)
    if path is None:
        return {"status": "OPTIONAL-MISSING", "what": "configuration file",
                "detail": "not found (looked in: " + "; ".join(str(p) for p in searched) + "). The Skill needs your accounts, folders and models; "
                          f"without a file it asks at the start. Fix: copy {CONFIG_TEMPLATE} to {CONFIG_NAME} in your own writing folder, fill in your own paths, "
                          f"and pass --config <path> (or set {CONFIG_ENV}). Do not copy private paths into the shared Skill folder."}
    try:
        missing = _config_problems(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        missing = None
    if missing is None:
        return {"status": "UNVERIFIED", "what": "configuration file", "detail": f"{path}: file exists, content not checked (could not be read as simple text)."}
    if missing:
        return {"status": "OPTIONAL-MISSING", "what": "configuration file",
                "detail": f"{path} is missing or empty on: {', '.join(missing)}. Fix: fill these in (see {CONFIG_TEMPLATE})."}
    return {"status": "OK", "what": "configuration file", "detail": f"{path} (account, reader, drafts and ready folders are filled in)"}


def check_models(search_path=None):
    found = [name for name in MODEL_CLIS if shutil.which(name, path=search_path)]
    vendors = sorted({v for name in found for v in MODEL_CLIS[name]})
    listing = ", ".join(f"{name} ({'/'.join(MODEL_CLIS[name])})" for name in found)
    if len(vendors) >= 2:
        return {"status": "UNVERIFIED", "what": "second-vendor model CLI",
                "detail": f"found on PATH: {listing}; vendors: {', '.join(vendors)}. Found on PATH, not verified to be logged in or callable. "
                          "Verify: run each CLI once with a one-line prompt. The writer and the wording editor should be from different vendors."}
    reason = (f"only one vendor found ({vendors[0]} via {listing})" if vendors
              else "none of " + ", ".join(MODEL_CLIS) + " found on PATH")
    return {"status": "OPTIONAL-MISSING", "what": "second-vendor model CLI",
            "detail": reason + ". Two different vendors are needed: the writer and the wording editor should come from different vendors; "
                      "without a second vendor the Skill marks \"wording not reviewed by a second model\". Fix: install a CLI from another vendor and log in."}


def check_visual(skill_dir: Path):
    sibling = skill_dir.parent / VISUAL_SKILL
    if sibling.is_dir():
        return {"status": "OK", "what": "visual Skill", "detail": str(sibling)}
    return {"status": "OPTIONAL-MISSING", "what": "visual Skill",
            "detail": f"folder {VISUAL_SKILL} not found next to this Skill. It is needed for evidence screenshots and images; without it screenshots are delivered as a \"to capture\" list. Fix: install {VISUAL_SKILL} in the same skills folder."}


def check_screenshots(skill_dir: Path):
    script = skill_dir.parent / VISUAL_SKILL / "scripts" / "capture_evidence.py"
    if not script.is_file():
        return {"status": "OPTIONAL-MISSING", "what": "screenshot capability",
                "detail": f"{script} not found. Without it screenshots become a \"to capture\" list for you to take by hand. Fix: install {VISUAL_SKILL} (it ships capture_evidence.py)."}
    return {"status": "UNVERIFIED", "what": "screenshot capability",
            "detail": f"{script.name} found, but screenshots need a browser the visual Skill can drive; a browser cannot be detected generically. "
                      "Without it screenshots become a \"to capture\" list."}


def run(skill_dir: Path, config: Path = None, search_path=None, version=None, env=None, cwd: Path = None):
    items = [check_python(version)]
    items += check_scripts(skill_dir / "scripts")
    items.append(check_config(skill_dir, config, env, cwd))
    items.append(check_models(search_path))
    items.append(check_visual(skill_dir))
    items.append(check_screenshots(skill_dir))
    core_ok = all(item["status"] != "MISSING" for item in items)
    return items, core_ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Self-check for the pinshu-write Skill")
    parser.add_argument("--config", type=Path, help=f"path to your {CONFIG_NAME} (otherwise: env {CONFIG_ENV}, ./{CONFIG_NAME}, then the Skill folder)")
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parent.parent, help="Skill folder (default: this one)")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args(argv)
    items, core_ok = run(args.skill_dir.resolve(), args.config)
    if args.json:
        print(json.dumps({"core_ok": core_ok, "items": items}, ensure_ascii=False, indent=2))
    else:
        for item in items:
            print(f"{item['status']}: {item['what']}: {item['detail']}")
        print("Core is fine." if core_ok else "Core is NOT ready: fix the MISSING items above.")
    return 0 if core_ok else 1


if __name__ == "__main__":
    sys.exit(main())
