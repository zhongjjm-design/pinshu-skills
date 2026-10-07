#!/usr/bin/env python3
"""Ownership state helpers for the Pinshu installer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path


EXCLUDED_DIRS = {".git", "__pycache__"}
EXCLUDED_FILES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def is_excluded(path: Path) -> bool:
    name = path.name
    return (
        name in EXCLUDED_FILES
        or name in EXCLUDED_DIRS
        or any(name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_manifest(root: Path) -> list[dict[str, object]]:
    if not root.exists() or not root.is_dir() or root.is_symlink():
        fail(f"Expected a real package directory: {root}")

    entries: list[dict[str, object]] = []
    root_stat = root.lstat()
    entries.append(
        {
            "type": "dir",
            "path": ".",
            "mode": stat.S_IMODE(root_stat.st_mode),
        }
    )
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        kept_dirs = []
        for dirname in sorted(dirnames):
            if is_excluded(Path(dirname)):
                continue
            child = current_path / dirname
            rel = child.relative_to(root).as_posix()
            child_stat = child.lstat()
            if stat.S_ISLNK(child_stat.st_mode) or not stat.S_ISDIR(child_stat.st_mode):
                fail(f"Package contains a symlink or special directory entry: {child}")
            entries.append(
                {
                    "type": "dir",
                    "path": rel,
                    "mode": stat.S_IMODE(child_stat.st_mode),
                }
            )
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        filenames = sorted(name for name in filenames if not is_excluded(Path(name)))

        for filename in filenames:
            path = current_path / filename
            if path.is_symlink() or not path.is_file():
                fail(f"Package contains a symlink or special file: {path}")
            rel = path.relative_to(root).as_posix()
            st = path.lstat()
            entries.append(
                {
                    "type": "file",
                    "path": rel,
                    "mode": stat.S_IMODE(st.st_mode),
                    "sha256": file_sha256(path),
                }
            )
    return entries


def package_state(skills_dir: Path, slug: str) -> dict[str, object]:
    active = skills_dir / slug
    if active.is_symlink():
        target_text = os.readlink(active)
        target = Path(target_text)
        if not target.is_absolute():
            target = (active.parent / target).resolve()
        return {
            "slug": slug,
            "active_type": "symlink",
            "link_target": target_text,
            "tree": tree_manifest(target),
        }
    return {
        "slug": slug,
        "active_type": "directory",
        "tree": tree_manifest(active),
    }


def load_state(path: Path) -> dict[str, object]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"Ownership state is missing: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Ownership state is invalid JSON: {path}: {exc}")


def state_packages(state: dict[str, object]) -> dict[str, dict[str, object]]:
    packages = state.get("packages")
    if not isinstance(packages, list):
        fail("Ownership state has no package list.")
    result = {}
    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("slug"), str):
            fail("Ownership state contains an invalid package entry.")
        result[package["slug"]] = package
    return result


def compare_package(actual: dict[str, object], expected: dict[str, object], slug: str) -> None:
    if actual != expected:
        fail(
            "Existing package differs from the installer ownership state; "
            f"refusing to replace possible local customization: {slug}"
        )


def run_git(clone_dir: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(clone_dir), *args],
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"Could not inspect legacy Git clone: {clone_dir}: {exc}")
    if result.returncode:
        fail(f"Legacy clone Git inspection failed: {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def assert_clean_committed_baseline(clone_dir: Path, slug: str) -> None:
    if not (clone_dir / ".git").is_dir() or (clone_dir / ".git").is_symlink():
        fail(f"Cannot adopt legacy packages without a real Git clone: {clone_dir}")
    run_git(clone_dir, "rev-parse", "--verify", "HEAD")
    run_git(clone_dir, "cat-file", "-e", f"HEAD:{slug}")
    watched = [slug, "install.sh", "scripts/installer_state.py", "RELEASE_MANIFEST.json"]
    status = run_git(clone_dir, "status", "--porcelain", "--", *watched)
    if status.strip():
        fail(f"Legacy clone has uncommitted package or installer changes; refusing adoption: {slug}")


def cmd_create(args: argparse.Namespace) -> None:
    state = {
        "schema_version": 1,
        "repository": args.repository,
        "revision": args.revision,
        "packages": [package_state(Path(args.skills_dir), slug) for slug in args.slug],
    }
    json.dump(state, sys.stdout, ensure_ascii=True, indent=2, sort_keys=True)
    print()


def cmd_verify(args: argparse.Namespace) -> None:
    skills_dir = Path(args.skills_dir)
    state = load_state(Path(args.state_file))
    if state.get("repository") != args.repository:
        fail("Ownership state repository does not match the requested source.")
    packages = state_packages(state)
    for slug in args.slug:
        active = skills_dir / slug
        if not active.exists() and not active.is_symlink():
            continue
        if slug not in packages:
            fail(f"Existing package lacks ownership proof: {slug}")
        compare_package(package_state(skills_dir, slug), packages[slug], slug)


def cmd_adopt(args: argparse.Namespace) -> None:
    skills_dir = Path(args.skills_dir)
    clone_dir = Path(args.clone_dir)
    for slug in args.slug:
        active = skills_dir / slug
        if not active.exists() and not active.is_symlink():
            continue
        assert_clean_committed_baseline(clone_dir, slug)
        if active.is_symlink():
            target_text = os.readlink(active)
            if target_text != str(clone_dir / slug):
                fail(f"Legacy package link target is not the known clone package: {slug}")
        actual = package_state(skills_dir, slug)
        expected = {
            "slug": slug,
            "active_type": "directory",
            "tree": tree_manifest(clone_dir / slug),
        }
        if active.is_symlink():
            expected["active_type"] = "symlink"
            expected["link_target"] = str(clone_dir / slug)
        compare_package(actual, expected, slug)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--skills-dir", required=True)
    create.add_argument("--repository", required=True)
    create.add_argument("--revision", required=True)
    create.add_argument("slug", nargs="+")
    create.set_defaults(func=cmd_create)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--state-file", required=True)
    verify.add_argument("--skills-dir", required=True)
    verify.add_argument("--repository", required=True)
    verify.add_argument("slug", nargs="+")
    verify.set_defaults(func=cmd_verify)

    adopt = subparsers.add_parser("adopt")
    adopt.add_argument("--skills-dir", required=True)
    adopt.add_argument("--clone-dir", required=True)
    adopt.add_argument("slug", nargs="+")
    adopt.set_defaults(func=cmd_adopt)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
