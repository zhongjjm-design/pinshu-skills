#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)
INSTALLER="$REPO_ROOT/install.sh"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/pinshu-installer-tests.XXXXXX")
REAL_GIT=$(command -v git)
NO_NETWORK_BIN="$TEST_ROOT/no-network-bin"
PASS_COUNT=0
FAIL_COUNT=0

EXPECTED_SKILLS=(
  pinshu-course-capture
  pinshu-content-assets
  pinshu-course
  pinshu-distill
  pinshu-md2pdf
  pinshu-study
  pinshu-transcript
  pinshu-visual-system
  pinshu-video-core
  pinshu-film-teardown
  pinshu-infographic
  pinshu-business-graphics
  pinshu-visual-learning
  pinshu-write
)

mkdir -p "$NO_NETWORK_BIN"
cat >"$NO_NETWORK_BIN/git" <<'GIT_WRAPPER'
#!/usr/bin/env bash
set -u
for argument in "$@"; do
  case "$argument" in
    http://*|https://*|git://*|ssh://*|git@*)
      printf 'Network Git access is forbidden in installer tests.\n' >&2
      exit 96
      ;;
  esac
done
exec "$PINSHU_REAL_GIT" "$@"
GIT_WRAPPER
chmod +x "$NO_NETWORK_BIN/git"

cleanup() {
  chmod -R u+w "$TEST_ROOT" 2>/dev/null || true
  rm -rf -- "$TEST_ROOT"
}
trap cleanup EXIT INT TERM

fail() {
  printf 'ASSERTION FAILED: %s\n' "$*" >&2
  return 1
}

assert_file() {
  [ -f "$1" ] || fail "expected regular file: $1"
}

assert_dir() {
  [ -d "$1" ] && [ ! -L "$1" ] || fail "expected real directory: $1"
}

assert_absent() {
  [ ! -e "$1" ] && [ ! -L "$1" ] || fail "expected path to be absent: $1"
}

assert_contains() {
  local file=$1
  local text=$2
  grep -Fq -- "$text" "$file" || fail "expected $file to contain: $text"
}

tree_fingerprint() {
  python3 - "$1" <<'PY'
from pathlib import Path
import hashlib
import os
import stat
import sys

root = Path(sys.argv[1])
rows = []
for current, dirs, files in os.walk(root, followlinks=False):
    dirs.sort()
    files.sort()
    cur = Path(current)
    for name in dirs + files:
        path = cur / name
        rel = path.relative_to(root).as_posix()
        st = path.lstat()
        mode = stat.S_IMODE(st.st_mode)
        if path.is_symlink():
            rows.append(f"l {rel} {mode} {os.readlink(path)}")
        elif path.is_dir():
            rows.append(f"d {rel} {mode}")
        elif path.is_file():
            rows.append(f"f {rel} {mode} {hashlib.sha256(path.read_bytes()).hexdigest()}")
        else:
            rows.append(f"s {rel} {stat.S_IFMT(st.st_mode)}")
print(hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest())
PY
}

new_case() {
  local name=$1
  CASE_ROOT="$TEST_ROOT/$name"
  HOME_DIR="$CASE_ROOT/home"
  FIXTURE_SOURCE="$CASE_ROOT/source"
  FIXTURE_REMOTE="$CASE_ROOT/remote.git"
  LOG_FILE="$CASE_ROOT/installer.log"
  mkdir -p "$HOME_DIR" "$FIXTURE_SOURCE"
  HOME_DIR=$(CDPATH= cd -- "$HOME_DIR" && pwd -P)
}

write_fixture_packages() {
  local version=$1
  local roster=${2:-valid}
  local skill

  mkdir -p "$FIXTURE_SOURCE/scripts"
  cp "$REPO_ROOT/install.sh" "$FIXTURE_SOURCE/install.sh"
  cp "$REPO_ROOT/scripts/installer_state.py" "$FIXTURE_SOURCE/scripts/installer_state.py"

  for skill in "${EXPECTED_SKILLS[@]}"; do
    if [ "$roster" = "invalid" ] && [ "$skill" = "pinshu-study" ]; then
      continue
    fi
    if [ "$roster" = "legacy-five" ] && { [ "$skill" = "pinshu-study" ] || [ "$skill" = "pinshu-content-assets" ] || [ "$skill" = "pinshu-visual-system" ] || [ "$skill" = "pinshu-video-core" ] || [ "$skill" = "pinshu-film-teardown" ] || [ "$skill" = "pinshu-infographic" ] || [ "$skill" = "pinshu-business-graphics" ] || [ "$skill" = "pinshu-visual-learning" ] || [ "$skill" = "pinshu-write" ]; }; then
      continue
    fi
    mkdir -p "$FIXTURE_SOURCE/$skill/assets" "$FIXTURE_SOURCE/$skill/__pycache__"
    printf -- '---\nname: %s\n---\n' "$skill" >"$FIXTURE_SOURCE/$skill/SKILL.md"
    if { [ "$skill" = pinshu-visual-system ] || [ "$skill" = pinshu-infographic ] || [ "$skill" = pinshu-business-graphics ]; }; then printf 'public\n' >"$FIXTURE_SOURCE/$skill/.public-bundle"; fi
    printf '%s\n' "$version" >"$FIXTURE_SOURCE/$skill/payload.txt"
    printf 'complete package content\n' >"$FIXTURE_SOURCE/$skill/assets/data.txt"
    printf 'hidden package content\n' >"$FIXTURE_SOURCE/$skill/.hidden-config"
    printf 'excluded metadata\n' >"$FIXTURE_SOURCE/$skill/.DS_Store"
    printf 'excluded bytecode\n' >"$FIXTURE_SOURCE/$skill/__pycache__/cache.pyc"
    printf 'excluded bytecode\n' >"$FIXTURE_SOURCE/$skill/compiled.pyo"
    case "$skill" in
      pinshu-video-core)
        mkdir -p "$FIXTURE_SOURCE/$skill/scripts" "$FIXTURE_SOURCE/$skill/tests"
        printf 'print("core common")\n' >"$FIXTURE_SOURCE/$skill/scripts/common.py"
        printf 'print("core doctor")\n' >"$FIXTURE_SOURCE/$skill/scripts/doctor.py"
        printf 'print("core self test")\n' >"$FIXTURE_SOURCE/$skill/tests/self_test.py"
        ;;
      pinshu-visual-learning)
        mkdir -p "$FIXTURE_SOURCE/$skill/scripts" "$FIXTURE_SOURCE/$skill/references"
        printf 'print("visual learning validator")\n' >"$FIXTURE_SOURCE/$skill/scripts/validate_visual_learning.py"
        printf '图解选型与验收\n' >"$FIXTURE_SOURCE/$skill/references/图解选型与验收.md"
        ;;
      pinshu-film-teardown)
        mkdir -p "$FIXTURE_SOURCE/$skill/scripts" "$FIXTURE_SOURCE/$skill/tests"
        printf 'print("core shim")\n' >"$FIXTURE_SOURCE/$skill/scripts/_video_core.py"
        printf 'print("film self test")\n' >"$FIXTURE_SOURCE/$skill/tests/self_test.py"
        ;;
    esac
    if [ "$version" = "v1" ]; then
      printf 'removed by upgrade\n' >"$FIXTURE_SOURCE/$skill/obsolete.txt"
    fi
  done

  if [ "$roster" = "invalid" ]; then
    mkdir -p "$FIXTURE_SOURCE/pinshu-surprise"
    printf -- '---\nname: pinshu-surprise\n---\n' >"$FIXTURE_SOURCE/pinshu-surprise/SKILL.md"
  fi
}

fixture_file_list() {
  find "$FIXTURE_SOURCE" -type f ! -path '*/.git/*' -print | sed "s#^$FIXTURE_SOURCE/##" | LC_ALL=C sort
}

stage_fixture_tree() {
  local paths=()
  local tracked=()
  local path

  while IFS= read -r path; do
    [ -n "$path" ] && paths+=("$path")
  done < <(fixture_file_list)
  if [ "${#paths[@]}" -gt 0 ]; then
    git -C "$FIXTURE_SOURCE" add -f -- "${paths[@]}"
  fi

  while IFS= read -r path; do
    [ -n "$path" ] && [ -e "$FIXTURE_SOURCE/$path" ] || tracked+=("$path")
  done < <(git -C "$FIXTURE_SOURCE" ls-files)
  if [ "${#tracked[@]}" -gt 0 ]; then
    git -C "$FIXTURE_SOURCE" rm -q --ignore-unmatch -- "${tracked[@]}"
  fi
}

make_remote() {
  local version=$1
  local roster=${2:-valid}

  write_fixture_packages "$version" "$roster"
  git -C "$FIXTURE_SOURCE" init -q -b main
  git -C "$FIXTURE_SOURCE" config user.name 'Installer Test'
  git -C "$FIXTURE_SOURCE" config user.email 'installer-test@example.invalid'
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m "fixture $version"
  git clone -q --bare "$FIXTURE_SOURCE" "$FIXTURE_REMOTE"
}

update_remote() {
  local version=$1
  local skill

  for skill in "${EXPECTED_SKILLS[@]}"; do
    printf '%s\n' "$version" >"$FIXTURE_SOURCE/$skill/payload.txt"
    rm -f -- "$FIXTURE_SOURCE/$skill/obsolete.txt"
  done
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m "fixture $version"
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
}

installer_env() {
  env \
    HOME="$HOME_DIR" \
    PATH="$NO_NETWORK_BIN:$PATH" \
    PINSHU_REAL_GIT="$REAL_GIT" \
    PINSHU_REPO="file://$FIXTURE_REMOTE" \
    PINSHU_INSTALL_DIR="$HOME_DIR/.pinshu-skills" \
    PINSHU_SKILLS_DIR="$HOME_DIR/.agents/skills" \
    "$@"
}

run_installer_success() {
  if ! installer_env bash "$INSTALLER" "$@" >"$LOG_FILE" 2>&1; then
    printf '%s\n' 'Installer output:' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'installer unexpectedly failed'
  fi
}

run_installer_failure() {
  if installer_env bash "$INSTALLER" "$@" >"$LOG_FILE" 2>&1; then
    printf '%s\n' 'Installer output:' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'installer unexpectedly succeeded'
  fi
}

run_piped_installer_success() {
  if ! (cd "$HOME_DIR" && installer_env bash -s -- "$@" <"$INSTALLER" >"$LOG_FILE" 2>&1); then
    printf '%s\n' 'Installer output:' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'piped installer unexpectedly failed'
  fi
}

run_piped_installer_failure() {
  if (cd "$HOME_DIR" && installer_env bash -s -- "$@" <"$INSTALLER" >"$LOG_FILE" 2>&1); then
    printf '%s\n' 'Installer output:' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'piped installer unexpectedly succeeded'
  fi
}

assert_active_version() {
  local version=$1
  local skill
  for skill in "${EXPECTED_SKILLS[@]}"; do
    assert_dir "$HOME_DIR/.agents/skills/$skill" || return 1
    assert_file "$HOME_DIR/.agents/skills/$skill/SKILL.md" || return 1
    assert_contains "$HOME_DIR/.agents/skills/$skill/payload.txt" "$version" || return 1
  done
}

assert_exact_active_roster() {
  local count=0
  local path
  shopt -s nullglob
  for path in "$HOME_DIR/.agents/skills"/pinshu-*; do
    count=$((count + 1))
  done
  shopt -u nullglob
  [ "$count" -eq "${#EXPECTED_SKILLS[@]}" ] || fail "expected ${#EXPECTED_SKILLS[@]} active Pinshu packages, found $count"
}

assert_public_visual_link() {
  local skill=$1 version=$2 target="$HOME_DIR/.agents/skills/$1"
  [ -L "$target" ] || fail "expected managed public link: $target"
  [ "$(readlink "$target")" = "$HOME_DIR/.pinshu-skills/$skill" ] || fail 'wrong public link target'
  assert_file "$target/SKILL.md"
  assert_file "$target/.public-bundle"
  assert_contains "$target/payload.txt" "$version"
}

test_clean_install() {
  local skill
  local git_artifact

  new_case clean-install
  make_remote v1 valid
  run_installer_success
  assert_active_version v1
  assert_exact_active_roster

  for skill in "${EXPECTED_SKILLS[@]}"; do
    assert_file "$HOME_DIR/.agents/skills/$skill/assets/data.txt"
    assert_file "$HOME_DIR/.agents/skills/$skill/.hidden-config"
    assert_absent "$HOME_DIR/.agents/skills/$skill/.DS_Store"
    assert_absent "$HOME_DIR/.agents/skills/$skill/__pycache__"
    assert_absent "$HOME_DIR/.agents/skills/$skill/compiled.pyo"
  done

  git_artifact=$(find "$HOME_DIR/.agents/skills" -name .git -print -quit)
  [ -z "$git_artifact" ] || fail "active Skill contains .git content: $git_artifact"
  assert_dir "$HOME_DIR/.pinshu-skills/.git"
  assert_file "$HOME_DIR/.agents/skills/.pinshu-installer-state.json"
  assert_contains "$HOME_DIR/.agents/skills/.pinshu-installer-state.json" '"schema_version": 1'
  [ -L "$HOME_DIR/.claude/skills" ] || fail 'expected Claude skills link'
  [ "$(readlink "$HOME_DIR/.claude/skills")" = "$HOME_DIR/.agents/skills" ] || fail 'Claude skills link points elsewhere'
}

test_symlink_destination_refusal() {
  local skill

  new_case symlink-refusal
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills" "$CASE_ROOT/victim"
  printf 'must survive\n' >"$CASE_ROOT/victim/sentinel"
  ln -s "$CASE_ROOT/victim" "$HOME_DIR/.agents/skills/pinshu-study"

  run_installer_failure
  assert_file "$CASE_ROOT/victim/sentinel"
  assert_absent "$CASE_ROOT/victim/SKILL.md"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    if [ "$skill" != "pinshu-study" ]; then
      assert_absent "$HOME_DIR/.agents/skills/$skill"
    fi
  done
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_acquisition_failure_preserves_legacy() {
  new_case acquisition-failure
  mkdir -p "$HOME_DIR/.agents/skills/transcript-cleaner"
  printf 'legacy stays active\n' >"$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"
  FIXTURE_REMOTE="$CASE_ROOT/does-not-exist.git"

  run_installer_failure
  assert_file "$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"
  assert_absent "$HOME_DIR/.claude/skills"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_unowned_same_name_refusal() {
  local skill
  new_case unowned-same-name
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills/pinshu-content-assets"
  printf 'unowned data\n' >"$HOME_DIR/.agents/skills/pinshu-content-assets/sentinel"
  run_installer_failure
  assert_contains "$LOG_FILE" 'Existing Skill lacks a regular SKILL.md'
  assert_file "$HOME_DIR/.agents/skills/pinshu-content-assets/sentinel"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-content-assets ] || assert_absent "$HOME_DIR/.agents/skills/$skill"
  done
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_suspicious_legacy_path_untouched() {
  new_case suspicious-legacy
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills" "$CASE_ROOT/victim"
  printf 'legacy data\n' >"$CASE_ROOT/victim/sentinel"
  ln -s "$CASE_ROOT/victim" "$HOME_DIR/.agents/skills/transcript-cleaner"
  run_installer_success
  assert_active_version v1
  [ -L "$HOME_DIR/.agents/skills/transcript-cleaner" ] || fail 'legacy symlink changed'
  assert_file "$CASE_ROOT/victim/sentinel"
  assert_contains "$LOG_FILE" 'legacy path has no ownership proof and was left untouched'
}

test_old_six_owned_upgrade() {
  local skill repository_backup
  new_case owned-old-six
  make_remote v1 valid
  rm -rf -- "$FIXTURE_SOURCE/pinshu-content-assets" "$FIXTURE_SOURCE/pinshu-visual-system" "$FIXTURE_SOURCE/pinshu-video-core" "$FIXTURE_SOURCE/pinshu-film-teardown" "$FIXTURE_SOURCE/pinshu-infographic" "$FIXTURE_SOURCE/pinshu-business-graphics" "$FIXTURE_SOURCE/pinshu-visual-learning" "$FIXTURE_SOURCE/pinshu-write"
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'old six roster'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  mkdir -p "$HOME_DIR/.agents/skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-content-assets ] && continue
    [ "$skill" = pinshu-visual-system ] && continue
    [ "$skill" = pinshu-video-core ] && continue
    [ "$skill" = pinshu-film-teardown ] && continue
    [ "$skill" = pinshu-infographic ] && continue
    [ "$skill" = pinshu-business-graphics ] && continue
    [ "$skill" = pinshu-visual-learning ] && continue
    [ "$skill" = pinshu-write ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a --exclude='.DS_Store' --exclude='__pycache__/' --exclude='*.pyc' --exclude='*.pyo' --exclude='.git' \
      "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  write_fixture_packages v2 valid
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'current roster'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  run_installer_success --adopt-legacy
  assert_active_version v2
  repository_backup=$(find "$HOME_DIR/.pinshu-install-backups" -type f -path '*/previous-clone/pinshu-study/payload.txt' -exec grep -l '^v1$' {} \; | head -n 1)
  [ -n "$repository_backup" ] || fail 'old six clone was not preserved'
  assert_absent "$HOME_DIR/.agents/skills/.pinshu-backups/legacy"
}

test_altered_installed_copy_refused() {
  new_case altered-copy
  make_remote v1 valid
  run_installer_success
  printf 'local change\n' >"$HOME_DIR/.agents/skills/pinshu-content-assets/local.txt"
  update_remote v2
  run_installer_failure
  assert_active_version v1
  assert_file "$HOME_DIR/.agents/skills/pinshu-content-assets/local.txt"
  assert_contains "$LOG_FILE" 'refusing to replace possible local customization'
}

test_dirty_old_five_is_refused_without_mutation() {
  local skill old_clone old_copy
  new_case dirty-old-five
  make_remote v1 legacy-five
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  mkdir -p "$HOME_DIR/.agents/skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-study ] && continue
    [ "$skill" = pinshu-content-assets ] && continue
    [ "$skill" = pinshu-visual-system ] && continue
    [ "$skill" = pinshu-video-core ] && continue
    [ "$skill" = pinshu-film-teardown ] && continue
    [ "$skill" = pinshu-infographic ] && continue
    [ "$skill" = pinshu-business-graphics ] && continue
    [ "$skill" = pinshu-visual-learning ] && continue
    [ "$skill" = pinshu-write ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a --exclude='.DS_Store' --exclude='__pycache__/' --exclude='*.pyc' --exclude='*.pyo' --exclude='.git' \
      "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  printf 'edited clone\n' >>"$HOME_DIR/.pinshu-skills/pinshu-transcript/SKILL.md"
  printf 'untracked clone note\n' >"$HOME_DIR/.pinshu-skills/local-note.txt"
  printf 'edited active Skill\n' >>"$HOME_DIR/.agents/skills/pinshu-distill/SKILL.md"
  write_fixture_packages v2 valid
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'current roster'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main

  run_installer_failure --adopt-legacy
  assert_contains "$LOG_FILE" 'refusing to replace possible local customization'
  assert_contains "$HOME_DIR/.pinshu-skills/local-note.txt" 'untracked clone note'
  assert_contains "$HOME_DIR/.agents/skills/pinshu-distill/SKILL.md" 'edited active Skill'
  old_clone=$(find "$HOME_DIR/.pinshu-install-backups" -type f -name local-note.txt -print -quit 2>/dev/null || true)
  [ -z "$old_clone" ] || fail 'dirty old clone should not be backed up for replacement'
  old_copy=$(find "$HOME_DIR/.agents/skills/.pinshu-backups" -type f -path '*/pinshu-distill/SKILL.md' -print -quit 2>/dev/null || true)
  [ -z "$old_copy" ] || fail 'dirty active Skill should not be backed up for replacement'
}

test_repeated_upgrade() {
  local repository_backup
  local v1_backup

  new_case repeated-upgrade
  make_remote v1 valid
  run_installer_success
  update_remote v2
  run_installer_success

  assert_active_version v2
  assert_absent "$HOME_DIR/.agents/skills/pinshu-study/obsolete.txt"
  assert_dir "$HOME_DIR/.pinshu-skills/.git"
  assert_contains "$HOME_DIR/.pinshu-skills/pinshu-study/payload.txt" v2
  v1_backup=$(find "$HOME_DIR" -type f -path '*/pinshu-study/payload.txt' -exec grep -l '^v1$' {} \; | head -n 1)
  [ -n "$v1_backup" ] || fail 'upgrade did not preserve the prior active Skill backup'
  repository_backup=$(find "$HOME_DIR/.pinshu-install-backups" -type f -path '*/previous-clone/pinshu-study/payload.txt' -exec grep -l '^v1$' {} \; | head -n 1)
  [ -n "$repository_backup" ] || fail 'upgrade did not preserve the prior repository clone backup'
}

test_linux_rsync_timestamp_only_upgrade() {
  local wrapper_dir
  local real_rsync

  new_case linux-rsync-timestamp
  make_remote v1 valid
  run_installer_success
  update_remote v2
  wrapper_dir="$CASE_ROOT/wrapper-bin"
  mkdir -p "$wrapper_dir"
  real_rsync=$(command -v rsync)
  cat >"$wrapper_dir/rsync" <<'RSYNC_WRAPPER'
#!/usr/bin/env bash
set -e
for argument in "$@"; do
  if [ "$argument" = "--dry-run" ]; then
    "$PINSHU_REAL_RSYNC" "$@"
    printf '.d..t...... ./\n'
    exit 0
  fi
done
exec "$PINSHU_REAL_RSYNC" "$@"
RSYNC_WRAPPER
  chmod +x "$wrapper_dir/rsync"

  if ! installer_env \
    PATH="$wrapper_dir:$NO_NETWORK_BIN:$PATH" \
    PINSHU_REAL_RSYNC="$real_rsync" \
    bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    printf '%s\n' 'Installer output:' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'timestamp-only Linux rsync output blocked an owned upgrade'
  fi
  assert_active_version v2
}

test_conflicting_claude_path_is_untouched() {
  new_case claude-conflict
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.claude/skills"
  printf 'keep this path\n' >"$HOME_DIR/.claude/skills/sentinel"

  run_installer_success
  assert_active_version v1
  assert_dir "$HOME_DIR/.claude/skills"
  assert_file "$HOME_DIR/.claude/skills/sentinel"
  [ -L "$HOME_DIR/.claude/skills/pinshu-study" ] || fail 'existing Claude directory did not gain a missing Skill link'
}

test_partial_install_without_clone() {
  local skill
  new_case partial-no-clone
  make_remote v1 valid
  for skill in pinshu-transcript pinshu-visual-system; do
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a "$FIXTURE_SOURCE/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  update_remote v2
  run_installer_failure
  assert_contains "$LOG_FILE" 'lacks ownership record'
  assert_contains "$HOME_DIR/.agents/skills/pinshu-transcript/payload.txt" v1
  assert_absent "$HOME_DIR/.agents/skills/pinshu-study"
}

test_partial_install_without_clone_can_be_adopted_only_with_clone() {
  local skill
  new_case partial-with-clone
  make_remote v1 valid
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  for skill in pinshu-transcript pinshu-visual-system; do
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  update_remote v2
  run_installer_success --adopt-legacy
  assert_active_version v2
  assert_exact_active_roster
  assert_contains "$LOG_FILE" 'Adopting unmarked legacy public packages after exact tree verification'
  local saved
  saved=$(find "$HOME_DIR/.agents/skills/.pinshu-backups" -type f -path '*/pinshu-transcript/payload.txt' -print -quit)
  [ -n "$saved" ] || fail 'partial old package was not backed up'
  assert_contains "$saved" v1
}

test_dry_run_has_no_writes() {
  new_case dry-run-empty
  make_remote v1 valid
  run_installer_success --dry-run
  assert_contains "$LOG_FILE" 'Dry run complete'
  assert_absent "$HOME_DIR/.pinshu-installer.lock"
  assert_absent "$HOME_DIR/.pinshu-skills"
  assert_absent "$HOME_DIR/.agents"
  assert_absent "$HOME_DIR/.claude"

  new_case dry-run-custom
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills/pinshu-transcript"
  printf -- '---\nname: pinshu-transcript\n---\n' >"$HOME_DIR/.agents/skills/pinshu-transcript/SKILL.md"
  printf 'custom data\n' >"$HOME_DIR/.agents/skills/pinshu-transcript/local.txt"
  cp -R "$HOME_DIR" "$CASE_ROOT/home-before"
  run_installer_failure --dry-run
  diff -r "$CASE_ROOT/home-before" "$HOME_DIR"
  assert_contains "$LOG_FILE" 'lacks ownership record'
  assert_absent "$HOME_DIR/.pinshu-installer.lock"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_owned_piped_and_file_dry_run_no_writes() {
  local before
  new_case owned-piped-dry-run
  make_remote v1 valid
  run_installer_success
  before=$(tree_fingerprint "$HOME_DIR")
  run_piped_installer_success --dry-run
  [ "$(tree_fingerprint "$HOME_DIR")" = "$before" ] || fail 'piped dry-run changed the managed home'
  assert_contains "$LOG_FILE" 'Dry run complete'
  run_installer_success --dry-run
  [ "$(tree_fingerprint "$HOME_DIR")" = "$before" ] || fail 'file dry-run changed the managed home'

  new_case piped-dry-run-unowned
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills/pinshu-transcript"
  printf -- '---\nname: pinshu-transcript\n---\n' >"$HOME_DIR/.agents/skills/pinshu-transcript/SKILL.md"
  printf 'custom data\n' >"$HOME_DIR/.agents/skills/pinshu-transcript/local.txt"
  before=$(tree_fingerprint "$HOME_DIR")
  run_piped_installer_failure --dry-run
  [ "$(tree_fingerprint "$HOME_DIR")" = "$before" ] || fail 'refused piped dry-run changed the custom home'
  assert_contains "$LOG_FILE" 'lacks ownership record'
}

test_nested_directory_symlink_customization_refused() {
  new_case nested-dir-symlink
  make_remote v1 valid
  run_installer_success
  mkdir -p "$HOME_DIR/private-addon"
  printf 'private enhancement must stay active\n' >"$HOME_DIR/private-addon/method.md"
  ln -s "$HOME_DIR/private-addon" "$HOME_DIR/.agents/skills/pinshu-transcript/local-addon"
  cp -RP "$HOME_DIR/.agents/skills/pinshu-transcript" "$CASE_ROOT/transcript-before"
  update_remote v2
  run_installer_failure
  assert_contains "$LOG_FILE" 'symlink or special directory entry'
  diff -r "$CASE_ROOT/transcript-before" "$HOME_DIR/.agents/skills/pinshu-transcript"
  assert_contains "$HOME_DIR/.agents/skills/pinshu-transcript/payload.txt" v1
  assert_file "$HOME_DIR/private-addon/method.md"
}

test_dirty_clone_and_active_adoption_is_refused() {
  new_case dirty-clone-adoption
  make_remote v1 valid
  run_installer_success
  mv "$HOME_DIR/.agents/skills/.pinshu-installer-state.json" "$CASE_ROOT/old-state.json"
  printf '\nLOCAL_CUSTOMIZATION_MUST_STAY\n' >>"$HOME_DIR/.agents/skills/pinshu-transcript/SKILL.md"
  printf '\nLOCAL_CUSTOMIZATION_MUST_STAY\n' >>"$HOME_DIR/.pinshu-skills/pinshu-transcript/SKILL.md"
  cp -RP "$HOME_DIR/.agents/skills/pinshu-transcript" "$CASE_ROOT/transcript-before"
  update_remote v2
  run_installer_failure --adopt-legacy
  assert_contains "$LOG_FILE" 'Legacy clone has uncommitted package or installer changes'
  diff -r "$CASE_ROOT/transcript-before" "$HOME_DIR/.agents/skills/pinshu-transcript"
  assert_contains "$HOME_DIR/.agents/skills/pinshu-transcript/SKILL.md" 'LOCAL_CUSTOMIZATION_MUST_STAY'
}

test_late_customization_before_swap_is_refused() {
  local wrapper_dir real_rsync old_revision old_state_revision
  new_case late-customization
  make_remote v1 valid
  run_installer_success
  old_revision=$(git -C "$HOME_DIR/.pinshu-skills" rev-parse HEAD)
  old_state_revision=$(state_revision_file="$HOME_DIR/.agents/skills/.pinshu-installer-state.json" python3 - <<'PY'
import json, os
with open(os.environ["state_revision_file"], "r", encoding="utf-8") as handle:
    print(json.load(handle)["revision"])
PY
)
  update_remote v2
  wrapper_dir="$CASE_ROOT/wrapper-bin"
  real_rsync=$(command -v rsync)
  mkdir -p "$wrapper_dir"
  cat >"$wrapper_dir/rsync" <<'RSYNC_WRAPPER'
#!/usr/bin/env bash
set -u
last_arg=${!#}
case "$last_arg" in
  *'.pinshu-stage.'*)
    if [ ! -e "$HERMES_LATE_MARKER" ]; then
      : >"$HERMES_LATE_MARKER"
      printf 'new local enhancement written during staging\n' >"$PINSHU_SKILLS_DIR/pinshu-transcript/LATE_PRIVATE.txt"
    fi
    ;;
esac
exec "$PINSHU_REAL_RSYNC" "$@"
RSYNC_WRAPPER
  chmod +x "$wrapper_dir/rsync"

  if installer_env \
    PATH="$wrapper_dir:$NO_NETWORK_BIN:$PATH" \
    PINSHU_REAL_RSYNC="$real_rsync" \
    HERMES_LATE_MARKER="$CASE_ROOT/late-marker" \
    bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    fail 'installer unexpectedly succeeded after late active customization'
  fi

  assert_file "$CASE_ROOT/late-marker"
  assert_contains "$LOG_FILE" 'refusing to replace possible local customization'
  assert_file "$HOME_DIR/.agents/skills/pinshu-transcript/LATE_PRIVATE.txt"
  assert_contains "$HOME_DIR/.agents/skills/pinshu-transcript/payload.txt" v1
  [ "$(git -C "$HOME_DIR/.pinshu-skills" rev-parse HEAD)" = "$old_revision" ] || fail 'clone revision changed after refused late customization'
  [ "$(state_revision_file="$HOME_DIR/.agents/skills/.pinshu-installer-state.json" python3 - <<'PY'
import json, os
with open(os.environ["state_revision_file"], "r", encoding="utf-8") as handle:
    print(json.load(handle)["revision"])
PY
)" = "$old_state_revision" ] || fail 'ownership state changed after refused late customization'
}

test_owned_tree_mutations_are_refused() {
  local mutation
  for mutation in added modified deleted permission; do
    new_case "owned-$mutation"
    make_remote v1 valid
    run_installer_success
    case "$mutation" in
      added)
        printf 'local file\n' >"$HOME_DIR/.agents/skills/pinshu-study/local-added.txt"
        ;;
      modified)
        printf 'locally modified\n' >"$HOME_DIR/.agents/skills/pinshu-study/payload.txt"
        ;;
      deleted)
        mv "$HOME_DIR/.agents/skills/pinshu-study/payload.txt" "$CASE_ROOT/deleted-payload.txt"
        ;;
      permission)
        chmod 600 "$HOME_DIR/.agents/skills/pinshu-study/payload.txt"
        ;;
    esac
    update_remote v2
    run_installer_failure
    assert_contains "$LOG_FILE" 'refusing to replace possible local customization'
    case "$mutation" in
      added)
        assert_file "$HOME_DIR/.agents/skills/pinshu-study/local-added.txt"
        ;;
      modified)
        assert_contains "$HOME_DIR/.agents/skills/pinshu-study/payload.txt" 'locally modified'
        ;;
      deleted)
        assert_absent "$HOME_DIR/.agents/skills/pinshu-study/payload.txt"
        ;;
      permission)
        local mode
        mode=$(python3 -c 'import os, stat, sys; print(format(stat.S_IMODE(os.stat(sys.argv[1]).st_mode), "o"))' "$HOME_DIR/.agents/skills/pinshu-study/payload.txt")
        [ "$mode" = "600" ] || fail 'permission mutation was not preserved'
        ;;
    esac
    assert_contains "$HOME_DIR/.pinshu-skills/pinshu-study/payload.txt" v1
  done
}

test_weak_identity_markers_do_not_adopt() {
  new_case weak-markers
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills/pinshu-film-teardown"
  printf -- '---\nname: pinshu-film-teardown\n---\n' >"$HOME_DIR/.agents/skills/pinshu-film-teardown/SKILL.md"
  printf 'public marker is not ownership\n' >"$HOME_DIR/.agents/skills/pinshu-film-teardown/.public-bundle"
  printf 'must stay\n' >"$HOME_DIR/.agents/skills/pinshu-film-teardown/sentinel"
  run_installer_failure
  assert_contains "$LOG_FILE" 'lacks ownership record'
  assert_contains "$HOME_DIR/.agents/skills/pinshu-film-teardown/sentinel" 'must stay'
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_private_dependencies_and_public_companion_update() {
  local skill
  new_case mixed-visual-group
  make_remote v1 valid
  run_installer_success
  rm -f "$HOME_DIR/.agents/skills/pinshu-business-graphics/.public-bundle"
  printf 'local identity\n' >"$HOME_DIR/.agents/skills/pinshu-business-graphics/assets/local.txt"
  for skill in pinshu-visual-system pinshu-infographic pinshu-business-graphics; do
    cp -R "$HOME_DIR/.agents/skills/$skill" "$CASE_ROOT/before-$skill"
  done
  update_remote v2
  run_installer_success
  for skill in pinshu-visual-system pinshu-business-graphics; do
    diff -r "$CASE_ROOT/before-$skill" "$HOME_DIR/.agents/skills/$skill"
  done
  assert_public_visual_link pinshu-infographic v2
  assert_contains "$HOME_DIR/.agents/skills/pinshu-study/payload.txt" v2
  assert_contains "$LOG_FILE" 'Installed or updated 12 public Pinshu Skills'
  local saved
  saved=$(find "$HOME_DIR/.agents/skills/.pinshu-backups" -type f -path '*/pinshu-infographic/payload.txt' -print -quit)
  assert_contains "$saved" v1
}

test_existing_claude_package_conflict_is_retained() {
  new_case claude-package-conflict
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.claude/skills/pinshu-study"
  printf 'private Claude copy\n' >"$HOME_DIR/.claude/skills/pinshu-study/sentinel"
  run_installer_success
  assert_contains "$HOME_DIR/.claude/skills/pinshu-study/sentinel" 'private Claude copy'
  assert_contains "$LOG_FILE" 'existing Claude Skill was left untouched'
  [ -L "$HOME_DIR/.claude/skills/pinshu-transcript" ] || fail 'missing Claude package was not linked'
}

test_invalid_roster_causes_no_active_mutation() {
  local skill

  new_case invalid-roster
  make_remote v1 invalid
  mkdir -p "$HOME_DIR/.agents/skills/transcript-cleaner"
  printf 'legacy active\n' >"$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    printf 'old active\n' >"$HOME_DIR/.agents/skills/$skill/old-sentinel"
  done

  run_installer_failure
  for skill in "${EXPECTED_SKILLS[@]}"; do
    assert_file "$HOME_DIR/.agents/skills/$skill/old-sentinel"
    assert_absent "$HOME_DIR/.agents/skills/$skill/payload.txt"
  done
  assert_file "$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"
  assert_absent "$HOME_DIR/.agents/skills/pinshu-surprise"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_incomplete_video_core_is_refused_before_mutation() {
  local skill

  new_case incomplete-video-core
  make_remote v1 valid
  rm -f -- "$FIXTURE_SOURCE/pinshu-video-core/scripts/common.py"
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'incomplete video core'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  mkdir -p "$HOME_DIR/.agents/skills/transcript-cleaner"
  printf 'legacy active\n' >"$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"

  run_installer_failure
  assert_contains "$LOG_FILE" 'Repository package dependency is incomplete: pinshu-video-core/scripts/common.py'
  for skill in "${EXPECTED_SKILLS[@]}"; do
    assert_absent "$HOME_DIR/.agents/skills/$skill"
  done
  assert_file "$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_mid_transaction_failure_rolls_back() {
  local skill
  local real_mv
  local wrapper_dir

  new_case rollback
  make_remote v1 valid
  run_installer_success
  mkdir -p "$HOME_DIR/.agents/skills/transcript-cleaner"
  printf 'legacy active\n' >"$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"
  update_remote v2

  wrapper_dir="$CASE_ROOT/wrapper-bin"
  mkdir -p "$wrapper_dir"
  real_mv=$(command -v mv)
  cat >"$wrapper_dir/mv" <<'WRAPPER'
#!/usr/bin/env bash
set -u
last_arg=${!#}
if [ "$last_arg" = "$PINSHU_SKILLS_DIR/pinshu-study" ] && [ ! -e "$MV_FAIL_STATE" ]; then
  : >"$MV_FAIL_STATE"
  exit 97
fi
exec "$PINSHU_REAL_MV" "$@"
WRAPPER
  chmod +x "$wrapper_dir/mv"

  if installer_env \
    PATH="$wrapper_dir:$NO_NETWORK_BIN:$PATH" \
    PINSHU_REAL_MV="$real_mv" \
    MV_FAIL_STATE="$CASE_ROOT/mv-failed-once" \
    bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    fail 'installer unexpectedly succeeded after injected move failure'
  fi

  if [ ! -f "$CASE_ROOT/mv-failed-once" ]; then
    printf 'Rollback fixture installer output:\n' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'injected move failure was not reached'
  fi
  assert_active_version v1
  assert_file "$HOME_DIR/.agents/skills/transcript-cleaner/sentinel"
  assert_contains "$HOME_DIR/.pinshu-skills/pinshu-study/payload.txt" v1
  for skill in "${EXPECTED_SKILLS[@]}"; do
    assert_file "$HOME_DIR/.agents/skills/$skill/obsolete.txt"
  done
}

test_claude_link_failure_rolls_back() {
  local real_ln
  local wrapper_dir

  new_case claude-link-rollback
  make_remote v1 valid
  run_installer_success
  mv "$HOME_DIR/.claude/skills" "$CASE_ROOT/old-claude-skills-link"
  mkdir -p "$HOME_DIR/.claude/skills"
  printf 'client state\n' >"$HOME_DIR/.claude/skills/sentinel"
  update_remote v2

  wrapper_dir="$CASE_ROOT/wrapper-bin"
  mkdir -p "$wrapper_dir"
  real_ln=$(command -v ln)
  cat >"$wrapper_dir/ln" <<'WRAPPER'
#!/usr/bin/env bash
set -u
last_arg=${!#}
if [ "$last_arg" = "$HOME/.claude/skills/pinshu-business-graphics" ]; then
  exit 98
fi
exec "$PINSHU_REAL_LN" "$@"
WRAPPER
  chmod +x "$wrapper_dir/ln"

  if installer_env \
    PATH="$wrapper_dir:$NO_NETWORK_BIN:$PATH" \
    PINSHU_REAL_LN="$real_ln" \
    bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    fail 'installer unexpectedly succeeded after injected Claude link failure'
  fi

  assert_contains "$LOG_FILE" 'Could not create required Claude Skill link'
  assert_contains "$LOG_FILE" 'Rollback completed'
  assert_active_version v1
  assert_contains "$HOME_DIR/.pinshu-skills/pinshu-study/payload.txt" v1
  assert_file "$HOME_DIR/.claude/skills/sentinel"
  assert_absent "$HOME_DIR/.claude/skills/pinshu-transcript"
}

test_symlink_install_dir_refusal() {
  new_case install-dir-symlink
  make_remote v1 valid
  mkdir -p "$CASE_ROOT/install-victim"
  printf 'must survive\n' >"$CASE_ROOT/install-victim/sentinel"
  ln -s "$CASE_ROOT/install-victim" "$HOME_DIR/.pinshu-skills"

  run_installer_failure
  assert_file "$CASE_ROOT/install-victim/sentinel"
  assert_absent "$CASE_ROOT/install-victim/pinshu-study"
  assert_absent "$HOME_DIR/.agents/skills/pinshu-study"
}

test_special_file_destination_refusal() {
  new_case special-file-destination
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills"
  printf 'must remain a file\n' >"$HOME_DIR/.agents/skills/pinshu-study"

  run_installer_failure
  assert_file "$HOME_DIR/.agents/skills/pinshu-study"
  assert_contains "$HOME_DIR/.agents/skills/pinshu-study" 'must remain a file'
  assert_absent "$HOME_DIR/.agents/skills/pinshu-course"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_escaping_destination_refusal() {
  local escaping_path

  new_case escaping-destination
  make_remote v1 valid
  escaping_path="$HOME_DIR/.agents/../escaped-skills"

  if installer_env PINSHU_SKILLS_DIR="$escaping_path" bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    fail 'installer unexpectedly accepted an escaping destination path'
  fi
  assert_absent "$HOME_DIR/escaped-skills"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_existing_lock_refusal() {
  new_case existing-lock
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.pinshu-installer.lock"

  run_installer_failure
  assert_dir "$HOME_DIR/.pinshu-installer.lock"
  assert_absent "$HOME_DIR/.agents/skills/pinshu-study"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_symlink_backup_container_refusal() {
  new_case backup-container-symlink
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills" "$CASE_ROOT/backup-victim"
  printf 'must survive\n' >"$CASE_ROOT/backup-victim/sentinel"
  ln -s "$CASE_ROOT/backup-victim" "$HOME_DIR/.agents/skills/.pinshu-backups"

  run_installer_failure
  assert_file "$CASE_ROOT/backup-victim/sentinel"
  assert_absent "$CASE_ROOT/backup-victim/active"
  assert_absent "$HOME_DIR/.agents/skills/pinshu-study"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

run_test() {
  local name=$1
  local function_name=$2
  local status

  (set -e; "$function_name")
  status=$?
  if [ "$status" -eq 0 ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    printf 'ok - %s\n' "$name"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    printf 'not ok - %s\n' "$name"
  fi
}

run_test 'clean install copies the complete allowed packages' test_clean_install
run_test 'symlink destination is refused and victim survives' test_symlink_destination_refusal
run_test 'acquisition failure leaves legacy Skill active' test_acquisition_failure_preserves_legacy
run_test 'unowned same-name directory is refused without mutation' test_unowned_same_name_refusal
run_test 'suspicious legacy symlink is left untouched' test_suspicious_legacy_path_untouched
test_private_visual_system_is_not_replaced() {
  new_case private-visual
  make_remote v1 valid
  mkdir -p "$HOME_DIR/.agents/skills/pinshu-visual-system/assets"
  printf -- '---\nname: pinshu-visual-system\n---\n' >"$HOME_DIR/.agents/skills/pinshu-visual-system/SKILL.md"
  printf 'private identity\n' >"$HOME_DIR/.agents/skills/pinshu-visual-system/assets/identity.txt"
  cp -R "$HOME_DIR/.agents/skills/pinshu-visual-system" "$CASE_ROOT/private-before"
  run_installer_success
  diff -r "$CASE_ROOT/private-before" "$HOME_DIR/.agents/skills/pinshu-visual-system"
  assert_contains "$HOME_DIR/.agents/skills/pinshu-visual-system/assets/identity.txt" 'private identity'
  assert_contains "$HOME_DIR/.agents/skills/pinshu-transcript/payload.txt" v1
  assert_contains "$LOG_FILE" 'Installed or updated 13 public Pinshu Skills'
  assert_exact_active_roster
  assert_contains "$LOG_FILE" 'kept existing, not upgraded: pinshu-visual-system'
  assert_public_visual_link pinshu-infographic v1
  assert_public_visual_link pinshu-business-graphics v1
  assert_dir "$HOME_DIR/.pinshu-skills/.git"
}

test_twelve_package_installation_adds_video_core_and_visual_learning() {
  local skill
  new_case twelve-to-current
  make_remote v1 valid
  rm -rf -- "$FIXTURE_SOURCE/pinshu-video-core" "$FIXTURE_SOURCE/pinshu-visual-learning"
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'prior twelve packages'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-video-core ] && continue
    [ "$skill" = pinshu-visual-learning ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  write_fixture_packages v2 valid
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'shared visual package'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  run_installer_success --adopt-legacy
  assert_active_version v2
  assert_exact_active_roster
  assert_file "$HOME_DIR/.agents/skills/pinshu-video-core/SKILL.md"
  assert_file "$HOME_DIR/.agents/skills/pinshu-visual-learning/SKILL.md"
}

run_test 'private core remains intact and missing companions use the public core' test_private_visual_system_is_not_replaced
run_test 'prior twelve packages upgrade to fourteen with backups' test_twelve_package_installation_adds_video_core_and_visual_learning

test_private_visual_companions_are_not_replaced() {
  local skill
  for skill in pinshu-infographic pinshu-business-graphics; do
    new_case "private-$skill"
    make_remote v1 valid
    mkdir -p "$HOME_DIR/.agents/skills/$skill/assets"
    printf -- '---\nname: %s\n---\n' "$skill" >"$HOME_DIR/.agents/skills/$skill/SKILL.md"
    printf 'private original survives\n' >"$HOME_DIR/.agents/skills/$skill/assets/original.txt"
    cp -R "$HOME_DIR/.agents/skills/$skill" "$CASE_ROOT/private-before"
    run_installer_success
    diff -r "$CASE_ROOT/private-before" "$HOME_DIR/.agents/skills/$skill"
    assert_contains "$HOME_DIR/.agents/skills/$skill/assets/original.txt" 'private original survives'
    assert_dir "$HOME_DIR/.pinshu-skills/.git"
    assert_contains "$HOME_DIR/.agents/skills/pinshu-transcript/payload.txt" v1
    assert_dir "$HOME_DIR/.agents/skills/pinshu-visual-system"
    assert_contains "$HOME_DIR/.agents/skills/pinshu-visual-system/payload.txt" v1
    assert_exact_active_roster
    assert_contains "$LOG_FILE" "kept existing, not upgraded: $skill"
    update_remote v2
    run_installer_success
    assert_contains "$HOME_DIR/.agents/skills/pinshu-visual-system/payload.txt" v1
    diff -r "$CASE_ROOT/private-before" "$HOME_DIR/.agents/skills/$skill"
    local public_companion=pinshu-infographic
    [ "$skill" != pinshu-infographic ] || public_companion=pinshu-business-graphics
    assert_public_visual_link "$public_companion" v2
  done
}

test_eleven_package_installation_adds_write_video_core_and_visual_learning() {
  local skill old_clone
  new_case eleven-to-fourteen
  make_remote v1 valid
  rm -rf -- "$FIXTURE_SOURCE/pinshu-write" "$FIXTURE_SOURCE/pinshu-video-core" "$FIXTURE_SOURCE/pinshu-visual-learning"
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'prior eleven packages'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-write ] && continue
    [ "$skill" = pinshu-video-core ] && continue
    [ "$skill" = pinshu-visual-learning ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  write_fixture_packages v2 valid
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'full visual companion set'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  run_installer_success --adopt-legacy
  assert_active_version v2
  assert_exact_active_roster
  assert_file "$HOME_DIR/.agents/skills/pinshu-write/SKILL.md"
  assert_file "$HOME_DIR/.agents/skills/pinshu-video-core/SKILL.md"
  assert_file "$HOME_DIR/.agents/skills/pinshu-visual-learning/SKILL.md"
  old_clone=$(find "$HOME_DIR/.pinshu-install-backups" -type f -path '*/previous-clone/pinshu-film-teardown/payload.txt' -print -quit)
  [ -n "$old_clone" ] || fail 'prior eleven-package clone was not preserved'
  assert_contains "$old_clone" 'v1'
}

run_test 'private companions remain intact and missing public packages are added' test_private_visual_companions_are_not_replaced
run_test 'prior eleven packages upgrade to fourteen with complete backups' test_eleven_package_installation_adds_write_video_core_and_visual_learning

run_test 'owned old-six installation upgrades to the current roster with backups' test_old_six_owned_upgrade
run_test 'altered installed copy is refused before replacement' test_altered_installed_copy_refused
run_test 'dirty old five is refused before mutation' test_dirty_old_five_is_refused_without_mutation
run_test 'repeated upgrade replaces stale content and preserves backup' test_repeated_upgrade
run_test 'partial installed packages without a prior clone upgrade and complete' test_partial_install_without_clone
run_test 'partial installed packages require clone-backed explicit adoption' test_partial_install_without_clone_can_be_adopted_only_with_clone
run_test 'dry-run leaves empty and customized homes unchanged' test_dry_run_has_no_writes
run_test 'owned piped and file dry-run leaves managed homes unchanged' test_owned_piped_and_file_dry_run_no_writes
run_test 'nested directory symlink customization is refused before replacement' test_nested_directory_symlink_customization_refused
run_test 'dirty clone and active legacy adoption is refused' test_dirty_clone_and_active_adoption_is_refused
run_test 'late customization before swap is refused and preserved' test_late_customization_before_swap_is_refused
run_test 'owned package add modify delete and permission changes are refused' test_owned_tree_mutations_are_refused
run_test 'weak name and public-bundle markers do not prove ownership' test_weak_identity_markers_do_not_adopt
run_test 'mixed visual upgrade preserves private dependencies and updates public companion' test_private_dependencies_and_public_companion_update
run_test 'existing Claude package stays intact while missing links are added' test_existing_claude_package_conflict_is_retained
run_test 'Linux rsync timestamp-only output permits owned upgrade' test_linux_rsync_timestamp_only_upgrade
run_test 'conflicting Claude path is left untouched' test_conflicting_claude_path_is_untouched
run_test 'invalid repository roster causes no active mutation' test_invalid_roster_causes_no_active_mutation
run_test 'incomplete video-core dependency is refused before mutation' test_incomplete_video_core_is_refused_before_mutation
run_test 'mid-transaction failure restores all prior active paths' test_mid_transaction_failure_rolls_back
run_test 'Claude link failure restores prior packages and clone' test_claude_link_failure_rolls_back
run_test 'symlink install directory is refused' test_symlink_install_dir_refusal
run_test 'special-file destination is refused' test_special_file_destination_refusal
run_test 'escaping destination path is refused' test_escaping_destination_refusal
run_test 'existing installer lock prevents a second run' test_existing_lock_refusal
run_test 'symlink backup container is refused' test_symlink_backup_container_refusal


seed_private_core() {
  mkdir -p "$HOME_DIR/.agents/skills/pinshu-visual-system/assets"
  printf -- '---\nname: pinshu-visual-system\n---\n' >"$HOME_DIR/.agents/skills/pinshu-visual-system/SKILL.md"
  printf 'private identity\n' >"$HOME_DIR/.agents/skills/pinshu-visual-system/assets/identity.txt"
  cp -R "$HOME_DIR/.agents/skills/pinshu-visual-system" "$CASE_ROOT/private-before"
}

test_managed_visual_links_upgrade() {
  new_case linked-upgrade
  make_remote v1 valid
  seed_private_core
  run_installer_success
  printf 'local public edit\n' >"$HOME_DIR/.agents/skills/pinshu-infographic/local.txt"
  update_remote v2
  run_installer_failure
  assert_contains "$LOG_FILE" 'refusing to replace possible local customization'
  assert_public_visual_link pinshu-infographic v1
  assert_public_visual_link pinshu-business-graphics v1
  assert_exact_active_roster
  diff -r "$CASE_ROOT/private-before" "$HOME_DIR/.agents/skills/pinshu-visual-system"
  assert_contains "$HOME_DIR/.agents/skills/pinshu-infographic/local.txt" 'local public edit'
}

test_managed_links_rollback() {
  new_case linked-rollback
  make_remote v1 valid
  seed_private_core
  run_installer_success
  update_remote v2
  local wrapper_dir="$CASE_ROOT/wrapper-bin" real_mv
  real_mv=$(command -v mv)
  mkdir -p "$wrapper_dir"
  cat >"$wrapper_dir/mv" <<'WRAPPER'
#!/usr/bin/env bash
set -u
last_arg=${!#}
if [ "$last_arg" = "$PINSHU_SKILLS_DIR/pinshu-business-graphics" ] && [ ! -e "$MV_FAIL_STATE" ]; then
  : >"$MV_FAIL_STATE"
  exit 97
fi
exec "$PINSHU_REAL_MV" "$@"
WRAPPER
  chmod +x "$wrapper_dir/mv"
  if installer_env PATH="$wrapper_dir:$NO_NETWORK_BIN:$PATH" PINSHU_REAL_MV="$real_mv" MV_FAIL_STATE="$CASE_ROOT/failed-once" bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    fail 'linked upgrade unexpectedly succeeded after injected failure'
  fi
  assert_file "$CASE_ROOT/failed-once"
  assert_contains "$LOG_FILE" 'Rollback completed'
  assert_public_visual_link pinshu-infographic v1
  assert_public_visual_link pinshu-business-graphics v1
  assert_contains "$HOME_DIR/.agents/skills/pinshu-study/payload.txt" v1
  diff -r "$CASE_ROOT/private-before" "$HOME_DIR/.agents/skills/pinshu-visual-system"
}

test_foreign_visual_link_refused() {
  new_case foreign-visual-link
  make_remote v1 valid
  seed_private_core
  mkdir -p "$CASE_ROOT/foreign"
  printf 'foreign sentinel\n' >"$CASE_ROOT/foreign/sentinel"
  ln -s "$CASE_ROOT/foreign" "$HOME_DIR/.agents/skills/pinshu-infographic"
  run_installer_failure
  assert_contains "$LOG_FILE" 'Destination symlink was refused'
  assert_file "$CASE_ROOT/foreign/sentinel"
  assert_absent "$HOME_DIR/.pinshu-skills"
}

test_managed_link_requires_official_clone() {
  new_case linked-origin-refusal
  make_remote v1 valid
  seed_private_core
  run_installer_success
  git -C "$HOME_DIR/.pinshu-skills" remote set-url origin "$CASE_ROOT/unrelated.git"
  run_installer_failure
  assert_contains "$LOG_FILE" 'Existing clone origin does not match'
  assert_public_visual_link pinshu-infographic v1
}

test_all_private_visual_packages_retained() {
  new_case all-private-visual
  make_remote v1 valid
  local skill
  for skill in pinshu-visual-system pinshu-infographic pinshu-business-graphics; do
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    printf -- '---\nname: %s\n---\n' "$skill" >"$HOME_DIR/.agents/skills/$skill/SKILL.md"
    printf 'private sentinel\n' >"$HOME_DIR/.agents/skills/$skill/sentinel"
    cp -R "$HOME_DIR/.agents/skills/$skill" "$CASE_ROOT/before-$skill"
  done
  run_installer_success
  for skill in pinshu-visual-system pinshu-infographic pinshu-business-graphics; do
    diff -r "$CASE_ROOT/before-$skill" "$HOME_DIR/.agents/skills/$skill"
  done
  assert_exact_active_roster
  assert_contains "$LOG_FILE" 'Installed or updated 11 public Pinshu Skills'
}

test_real_planners_through_shared_links() {
  new_case real-linked-planners
  make_remote v1 valid
  local skill
  for skill in "${EXPECTED_SKILLS[@]}"; do
    rsync -a --exclude=__pycache__/ --exclude='*.pyc' "$REPO_ROOT/$skill/" "$FIXTURE_SOURCE/$skill/"
  done
  stage_fixture_tree
  git -C "$FIXTURE_SOURCE" commit -q -m 'real public packages'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  seed_private_core
  run_installer_success
  # The private core deliberately has no scripts. Wrong dependency routing fails.
  python3 "$HOME_DIR/.agents/skills/pinshu-infographic/scripts/plan_infographic.py" \
    --brief "$HOME_DIR/.agents/skills/pinshu-infographic/examples/brief.json" --output-dir "$CASE_ROOT/infographic-out"
  python3 "$HOME_DIR/.agents/skills/pinshu-business-graphics/scripts/plan_business_graphic.py" \
    --brief "$HOME_DIR/.agents/skills/pinshu-business-graphics/examples/brief.json" --output-dir "$CASE_ROOT/business-out"
  assert_file "$CASE_ROOT/infographic-out/route-plan.json"
  assert_file "$CASE_ROOT/business-out/route-plan.json"
  diff -r "$CASE_ROOT/private-before" "$HOME_DIR/.agents/skills/pinshu-visual-system"
}

run_test 'managed public visual links update repeatedly and preserve canonical edits' test_managed_visual_links_upgrade
run_test 'linked upgrade failure restores old clone and both entry links' test_managed_links_rollback
run_test 'foreign visual symlink is refused without mutation' test_foreign_visual_link_refused
run_test 'managed visual links require the prior official clone origin' test_managed_link_requires_official_clone
run_test 'all three private visual packages remain unchanged' test_all_private_visual_packages_retained
run_test 'real companion planners invoked through shared links use their public core' test_real_planners_through_shared_links

printf '%s passed; %s failed\n' "$PASS_COUNT" "$FAIL_COUNT"
[ "$FAIL_COUNT" -eq 0 ]
