#!/usr/bin/env python3
"""One-time self-check for a new user of the pinshu-write Skill.

Prints one line per item: OK / MISSING / OPTIONAL-MISSING / UNVERIFIED: what, why it matters, how to fix.
UNVERIFIED means found but not proven to work (for example a CLI on PATH that may not be logged in).
Exit 0 when the core is fine (optional items may be missing); exit 1 when a core item is missing.
Core: Python 3.9+ and the core scripts. Optional: a configuration file (without it the Skill asks for the account, reader and folders at the start),
the style assets it names (profiles, standards, material folders) being present on this computer, the seed-discovery sources (which route an author
with no seed will take, and whether the topic pool is fresh), a second-vendor model CLI, the visual Skill. Plain Python 3.9+, no third-party packages.
The configuration is read in the template's layout (accounts, top-level folders) or the older one (account, paths.*).
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

CORE_SCRIPTS = ("audit_draft", "export_article", "fix_quotes", "run_watched", "stage_log")
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


# ---- Reading the configuration -------------------------------------------------------------
# A small reader for the YAML subset the template uses (mappings, lists, "- key: value" items, [a, b] lists,
# comments). No YAML library: the core stays plain Python. Lines it does not understand (block text, document
# markers, odd syntax) are skipped, so one unusual line never hides the keys around it.

_KV = re.compile(r"""^("[^"]+"|'[^']+'|[^\s:#'"\[\]{},-][^:#]*?):(?:\s+(.*))?$""")
_FLOW_ITEM = re.compile(r"""\s*("[^"]*"|'[^']*'|[^,]+)\s*(?:,|$)""")


def _strip_comment(raw: str) -> str:
    raw = raw.strip()
    start = 0
    if raw[:1] in ("'", '"'):  # a quoted value: a # inside the quotes is not a comment
        close = raw.find(raw[0], 1)
        start = close + 1 if close > 0 else len(raw)
    for index in range(start, len(raw)):
        if raw[index] == "#" and (index == 0 or raw[index - 1].isspace()):
            return raw[:index].rstrip()
    return raw


def _scalar(raw: str):
    raw = _strip_comment(raw)
    if raw.startswith("[") and raw.endswith("]"):
        return [_scalar(item) for item in _FLOW_ITEM.findall(raw[1:-1]) if item.strip()]
    if raw[:1] in ("[", "{"):  # a flow value spread over several lines: not read, rather than misread as a path
        return ""
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "'\"":
        return raw[1:-1]
    return "" if raw in ("~", "null") else raw


def _key(raw: str) -> str:
    return raw[1:-1] if raw[:1] in ("'", '"') else raw.strip()


def _tokens(text: str):
    """(indent, kind, payload) per meaningful line; kind is item, kv or text. A "- key: value" item becomes an
    empty item plus a kv token at the item's content column, so its later keys join the same mapping."""
    out = []
    for line in text.lstrip("\ufeff").splitlines():
        line = line.expandtabs(2)
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped in ("---", "..."):
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.lstrip(" ")
        if body == "-" or body.startswith("- "):
            content = body[1:].lstrip(" ")
            column = indent + len(body) - len(content)
            if _KV.match(content.rstrip()):
                out.append((indent, "item", None))
                body, indent = content, column
            else:
                out.append((indent, "item", content or None))
                continue
        match = _KV.match(body.rstrip())  # the value keeps its comment until _scalar, so quotes still protect a #
        out.append((indent, "kv", (_key(match.group(1)), match.group(2) or "")) if match else (indent, "text", body))
    return out


def _skip_deeper(tokens, i, indent):
    while i < len(tokens) and tokens[i][0] > indent:  # block text under a scalar, or lines not understood
        i += 1
    return i


def _block(tokens, i, indent):
    if tokens[i][1] == "item":
        items = []
        while i < len(tokens) and tokens[i][0] == indent and tokens[i][1] == "item":
            payload = tokens[i][2]
            i += 1
            if payload is not None:
                items.append(_scalar(payload))
                i = _skip_deeper(tokens, i, indent)
            elif i < len(tokens) and tokens[i][0] > indent:
                value, i = _block(tokens, i, tokens[i][0])
                items.append(value)
                i = _skip_deeper(tokens, i, indent)
            else:
                items.append("")
        return items, i
    mapping = {}
    while i < len(tokens) and tokens[i][0] == indent and tokens[i][1] != "item":
        if tokens[i][1] == "text":
            i = _skip_deeper(tokens, i + 1, indent)
            continue
        key, raw = tokens[i][2]
        i += 1
        if _strip_comment(raw):
            mapping[key] = _scalar(raw)
        elif i < len(tokens) and (tokens[i][0] > indent or (tokens[i][0] == indent and tokens[i][1] == "item")):
            mapping[key], i = _block(tokens, i, tokens[i][0])
        else:
            mapping[key] = ""
        i = _skip_deeper(tokens, i, indent)
    return mapping, i


def parse_config(text: str):
    """The configuration as a dict, or None when no top-level key could be read."""
    tokens = _tokens(text)
    mapping, i = {}, 0
    while i < len(tokens):
        if tokens[i][0] == 0 and tokens[i][1] == "kv":
            value, i = _block(tokens, i, 0)
            mapping.update(value)
        else:
            i += 1
    return mapping or None


# Older layout -> template layout. Configurations written before 1.6 used a single `account:` mapping and a
# `paths:` block; both layouts are read so no agent has to guess which one it is looking at.
LEGACY_ACCOUNT_KEYS = {"profile_authority": "profile"}
LEGACY_NESTED = {("style", "voice_profile"): "author_style_profile"}


def normalize_config(config: dict):
    """Returns (config in the template's layout, notes on what was read from the older layout)."""
    config = dict(config)
    notes = []
    if not config.get("accounts") and isinstance(config.get("account"), dict):
        config["accounts"] = [config["account"]]
        notes.append("account -> accounts")
    if isinstance(config.get("paths"), dict):
        moved = [key for key in config["paths"] if key not in config]
        for key in moved:
            config[key] = config["paths"][key]
        if moved:
            notes.append("paths." + ", paths.".join(moved) + " -> top level")
    accounts = []
    for account in config.get("accounts") or []:
        if isinstance(account, dict):
            account = dict(account)
            for old, new in LEGACY_ACCOUNT_KEYS.items():
                if account.get(old) and not account.get(new):
                    account[new] = account[old]
                    notes.append(f"account {old} -> {new}")
        accounts.append(account)
    if accounts:
        config["accounts"] = accounts
    for (parent, old), new in LEGACY_NESTED.items():
        nested = config.get(parent)
        if isinstance(nested, dict) and nested.get(old) and not config.get(new):
            config[new] = nested[old]
            notes.append(f"{parent}.{old} -> {new}")
    return config, notes


def load_config(text: str):
    """(normalized config, legacy notes), or (None, []) when the text cannot be understood."""
    parsed = parse_config(text)
    if parsed is None:
        return None, []
    return normalize_config(parsed)


def _filled(value) -> bool:
    return value not in (None, "", [], {})


def _config_problems(config: dict):
    """Missing keys in a normalized config."""
    missing = []
    accounts = config.get("accounts")
    if not isinstance(accounts, list) or not accounts:
        missing.append("accounts")
    else:
        for field in ("name", "reader"):
            if not any(isinstance(a, dict) and _filled(a.get(field)) for a in accounts):
                missing.append(f"accounts[].{field}")
    for key in ("drafts_folder", "ready_folder"):
        if not _filled(config.get(key)):
            missing.append(key)
    return missing


def _read(path: Path):
    try:
        return load_config(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None, []


def _legacy_note(notes):
    return (" Read with the older layout (" + "; ".join(notes) + "); the template's layout is "
            f"accounts and top-level folders ({CONFIG_TEMPLATE}).") if notes else ""


def check_config(skill_dir: Path, config: Path = None, env=None, cwd: Path = None):
    path, searched = find_config(skill_dir, config, env, cwd)
    if path is None:
        return {"status": "OPTIONAL-MISSING", "what": "configuration file",
                "detail": "not found (looked in: " + "; ".join(str(p) for p in searched) + "). The Skill needs your accounts, folders and models; "
                          f"without a file it asks at the start. Fix: copy {CONFIG_TEMPLATE} to {CONFIG_NAME} in your own writing folder, fill in your own paths, "
                          f"and pass --config <path> (or set {CONFIG_ENV}). Do not copy private paths into the shared Skill folder."}
    data, notes = _read(path)
    if data is None:
        return {"status": "UNVERIFIED", "what": "configuration file", "detail": f"{path}: file exists, content not checked (could not be read as simple text)."}
    missing = _config_problems(data)
    if missing:
        named = [f"{key} (needed only at export: pass --ready-dir to export_article.py)" if key == "ready_folder" else key for key in missing]
        return {"status": "OPTIONAL-MISSING", "what": "configuration file",
                "detail": f"{path} is missing or empty on: {', '.join(named)}. Fix: fill these in (see {CONFIG_TEMPLATE})." + _legacy_note(notes)}
    return {"status": "OK", "what": "configuration file", "detail": f"{path} (account, reader, drafts and ready folders are filled in)." + _legacy_note(notes)}


# Files and folders that carry the account's voice. On a new computer or a new library these are what
# goes missing first, and the article is then written without them (meeting 2026-10-12, WRITE-04).
STYLE_KEYS = ("profile", "author_style_profile", "edit_patterns", "good_article_standard", "banned_words_file",
              "published_folder", "source_list", "topic_pool")
STYLE_LISTS = ("material_folders", "style_card_folders")


def _style_paths(config: dict):
    found = []
    scopes = [config] + [a for a in config.get("accounts") or [] if isinstance(a, dict)]
    for scope in scopes:
        for key in STYLE_KEYS:
            value = scope.get(key)
            if isinstance(value, str) and value:
                found.append((key, value))
    for key in STYLE_LISTS:
        value = config.get(key)
        items = value if isinstance(value, list) else ([value] if isinstance(value, str) and value else [])
        found += [(key, item) for item in items if isinstance(item, str) and item]
    return found


def style_asset_paths(text: str):
    """The style assets the config names, in either layout. Returns [(key, raw path)]."""
    config, _ = load_config(text)
    return _style_paths(config) if config else []


def _resolve(raw: str, base: Path) -> Path:
    path = Path(raw).expanduser()
    return path if path.is_absolute() else base / path


def check_style_assets(skill_dir: Path, config: Path = None, env=None, cwd: Path = None):
    path, _ = find_config(skill_dir, config, env, cwd)
    if path is None:
        return {"status": "OPTIONAL-MISSING", "what": "style assets",
                "detail": "no configuration file, so no account profile, style profile or material folders are known. "
                          "Articles are then written against the generic floor only and voice will differ between computers."}
    data, _ = _read(path)
    if data is None:
        return {"status": "UNVERIFIED", "what": "style assets", "detail": f"{path} could not be read as simple text"}
    named = _style_paths(data)
    if not named:
        return {"status": "OPTIONAL-MISSING", "what": "style assets",
                "detail": f"{path} names no profile, style profile or material folder. Fix: fill them in (see {CONFIG_TEMPLATE})."}
    missing = [f"{key}: {raw}" for key, raw in named if not _resolve(raw, path.parent).exists()]
    if missing:
        return {"status": "OPTIONAL-MISSING", "what": "style assets",
                "detail": f"{len(missing)} of {len(named)} named in {path.name} are not on this computer: " + "; ".join(missing)
                          + ". Without them the article loses that part of the account's voice. Fix: copy them over or correct the paths."}
    return {"status": "OK", "what": "style assets", "detail": f"all {len(named)} named in {path.name} exist on this computer"}


# ---- Topic-scan sources (references/1-topic.md, "Source route") -------------------------------

DISCOVERY_WINDOW_DAYS = 7
POOL_SUFFIXES = (".md", ".json", ".yaml", ".yml", ".txt", ".csv")
# A stated generation time near the top of a topic pool: "generated_at": "2026-10-14T...", generated: 2026/10/14,
# 生成时间：2026年10月14日, 扫描时间 2026-10-14. The first strong marker wins; "updated", "更新" or a bare "date:" /
# "日期" at the start of a line count only when no strong marker exists. The first match is taken, not the latest,
# because leads below the header carry their own dates.
_DATE = r"[^\d\n]{0,30}(\d{4})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})"
_STRONG = re.compile(r"(?:\b(?:generated|created|scanned)(?:_at|_on)?\b|生成|扫描)" + _DATE, re.I)
_WEAK = re.compile(r"(?:\bupdated(?:_at|_on)?\b|更新|^[\s>*#{\"'-]*(?:date\b|日期))" + _DATE, re.I | re.M)


def pool_generated(path: Path, head_lines: int = 60):
    """The generation date stated near the top of the file, or None. File times are not used: they only show
    when a file was last touched, not when its content was gathered."""
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            head = "".join(line for _, line in zip(range(head_lines), handle))
    except OSError:
        return None
    for pattern in (_STRONG, _WEAK):
        for match in pattern.finditer(head):
            try:
                return datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            except ValueError:
                continue
    return None


def newest_pool_file(path: Path):
    """(file, stated date) for a topic pool file, or for the newest stated pool in a folder."""
    if path.is_file():
        return path, pool_generated(path)
    files = sorted(p for p in path.iterdir() if p.is_file() and p.suffix.lower() in POOL_SUFFIXES and not p.name.startswith("."))
    dated = [(pool_generated(p), p) for p in files]
    with_date = [(d, p) for d, p in dated if d]
    if with_date:
        date, best = max(with_date, key=lambda pair: pair[0])
        return best, date
    return (files[0], None) if files else (None, None)


def _entries(value):
    """A source setting may be one path or URL, or a list of them."""
    items = value if isinstance(value, list) else [value]
    return [item for item in items if isinstance(item, str) and item]


def _is_url(raw: str) -> bool:
    return raw.startswith(("http://", "https://"))


def _pool_state(raw: str, base: Path, today):
    """(state, note) for one topic pool entry; state is fresh, historical or None (unusable)."""
    if _is_url(raw):
        return "historical", f"topic_pool {raw} is online: its date is checked when it is read"
    pool = _resolve(raw, base)
    if not pool.exists():
        return None, f"topic_pool {pool} is not on this computer"
    file, date = newest_pool_file(pool)
    if file is None:
        return None, f"topic_pool {pool} holds no readable pool file"
    if date is None:
        return "historical", f"topic_pool {file} states no generation time: historical leads only, each checked online before use"
    age = (today - date).days
    if -1 <= age <= DISCOVERY_WINDOW_DAYS:
        return "fresh", f"topic_pool {file} generated {date.isoformat()} ({max(age, 0)} day(s) ago): fresh, read first"
    when = "a future date" if age < 0 else f"{age} day(s) ago, window {DISCOVERY_WINDOW_DAYS}"
    return "historical", f"topic_pool {file} generated {date.isoformat()} ({when}): historical leads only, each checked online before use"


def check_seed_sources(skill_dir: Path, config: Path = None, env=None, cwd: Path = None, today=None):
    """Which source route an author with no topic will take (references/1-topic.md, "Source route"). Never a core
    failure: every route has a fallback, except "no web and no usable source", where discovery stops and says so."""
    today = today or datetime.date.today()
    what = "seed-discovery sources"
    path, _ = find_config(skill_dir, config, env, cwd)
    if path is None:
        return {"status": "OPTIONAL-MISSING", "what": what,
                "detail": "no configuration: an author with no seed gets the public source map online (references/1-topic.md, Public source map). "
                          "Without web access that route stops."}
    data, _ = _read(path)
    if data is None:
        return {"status": "UNVERIFIED", "what": what, "detail": f"{path} could not be read as simple text"}
    web_off = str(data.get("web_access", "")).strip().lower() in ("none", "no", "false", "off")
    notes, states = [], []
    for raw in _entries(data.get("topic_pool")):
        state, note = _pool_state(raw, path.parent, today)
        states.append(state)
        notes.append(note)
    list_ok = False
    for raw in _entries(data.get("source_list")):
        if _is_url(raw):
            usable = not web_off
            notes.append(f"source_list {raw} is online: " + ("read over the web" if usable else "unreachable without web access"))
        else:
            sources = _resolve(raw, path.parent)
            usable = sources.exists()
            notes.append(f"source_list {sources} " + ("found: scanned next" if usable else "is not on this computer"))
        list_ok = list_ok or usable

    web_note = "web access: none in the configuration" if web_off else "web access: allowed or not stated (the agent's own tools decide)"
    joined = "; ".join(notes)
    if "fresh" in states:
        offline = " Without web access the pool's leads are listed as the pool states them, not rechecked." if web_off else ""
        return {"status": "OK", "what": what, "detail": f"route 1 (fresh topic pool). {joined}. {web_note}.{offline}"}
    if list_ok:
        return {"status": "OK", "what": what, "detail": f"route 2 (source list), plus public source families it does not cover. {joined}. {web_note}."}
    if web_off:
        return {"status": "OPTIONAL-MISSING", "what": what,
                "detail": "with no seed, discovery will stop: web_access is none and no fresh topic pool or usable source list is on this computer"
                          + (f" ({joined}; historical leads need web access to check)" if notes else "")
                          + ". Fix: point source_list or topic_pool at your own files, or allow web access. Authors who bring a seed are not affected."}
    return {"status": "OPTIONAL-MISSING", "what": what,
            "detail": "route 3 (public source map online, references/1-topic.md)"
                      + (f". {joined}" if notes else ": no source_list or topic_pool configured")
                      + f". {web_note}. Optional: point source_list or topic_pool at your own files to read them first."}


def check_models(search_path=None):
    found = [name for name in MODEL_CLIS if shutil.which(name, path=search_path)]
    vendors = sorted({v for name in found for v in MODEL_CLIS[name]})
    listing = ", ".join(f"{name} ({'/'.join(MODEL_CLIS[name])})" for name in found)
    if len(vendors) >= 2:
        return {"status": "UNVERIFIED", "what": "second-vendor model CLI",
                "detail": f"found on PATH: {listing}; vendors: {', '.join(vendors)}. Found on PATH, not verified to be logged in or callable. "
                          "Verify: run each CLI once with a one-line prompt. The writer and the reviewing roles should be from different vendors."}
    reason = (f"only one vendor found ({vendors[0]} via {listing})" if vendors
              else "none of " + ", ".join(MODEL_CLIS) + " found on PATH")
    return {"status": "OPTIONAL-MISSING", "what": "second-vendor model CLI",
            "detail": reason + ". Two different vendors are needed: the writer and the reviewing roles should come from different vendors; "
                      "without a second vendor the Skill marks \"same-vendor review\". Fix: install a CLI from another vendor and log in."}


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


def run(skill_dir: Path, config: Path = None, search_path=None, version=None, env=None, cwd: Path = None, today=None):
    items = [check_python(version)]
    items += check_scripts(skill_dir / "scripts")
    items.append(check_config(skill_dir, config, env, cwd))
    items.append(check_style_assets(skill_dir, config, env, cwd))
    items.append(check_seed_sources(skill_dir, config, env, cwd, today))
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
