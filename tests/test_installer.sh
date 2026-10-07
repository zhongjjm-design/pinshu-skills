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
  pinshu-film-teardown
  pinshu-infographic
  pinshu-business-graphics
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

  for skill in "${EXPECTED_SKILLS[@]}"; do
    if [ "$roster" = "invalid" ] && [ "$skill" = "pinshu-study" ]; then
      continue
    fi
    if [ "$roster" = "legacy-five" ] && { [ "$skill" = "pinshu-study" ] || [ "$skill" = "pinshu-content-assets" ] || [ "$skill" = "pinshu-visual-system" ] || [ "$skill" = "pinshu-film-teardown" ] || [ "$skill" = "pinshu-infographic" ] || [ "$skill" = "pinshu-business-graphics" ]; }; then
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
    if [ "$version" = "v1" ]; then
      printf 'removed by upgrade\n' >"$FIXTURE_SOURCE/$skill/obsolete.txt"
    fi
  done

  if [ "$roster" = "invalid" ]; then
    mkdir -p "$FIXTURE_SOURCE/pinshu-surprise"
    printf -- '---\nname: pinshu-surprise\n---\n' >"$FIXTURE_SOURCE/pinshu-surprise/SKILL.md"
  fi
}

make_remote() {
  local version=$1
  local roster=${2:-valid}

  write_fixture_packages "$version" "$roster"
  git -C "$FIXTURE_SOURCE" init -q -b main
  git -C "$FIXTURE_SOURCE" config user.name 'Installer Test'
  git -C "$FIXTURE_SOURCE" config user.email 'installer-test@example.invalid'
  git -C "$FIXTURE_SOURCE" add .
  git -C "$FIXTURE_SOURCE" add -f -- \
    'pinshu-*/.DS_Store' \
    'pinshu-*/__pycache__/cache.pyc' \
    'pinshu-*/compiled.pyo'
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
  git -C "$FIXTURE_SOURCE" add -A
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
  if ! installer_env bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    printf '%s\n' 'Installer output:' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'installer unexpectedly failed'
  fi
}

run_installer_failure() {
  if installer_env bash "$INSTALLER" >"$LOG_FILE" 2>&1; then
    printf '%s\n' 'Installer output:' >&2
    sed 's/^/  /' "$LOG_FILE" >&2
    fail 'installer unexpectedly succeeded'
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
  rm -rf -- "$FIXTURE_SOURCE/pinshu-content-assets" "$FIXTURE_SOURCE/pinshu-visual-system" "$FIXTURE_SOURCE/pinshu-film-teardown" "$FIXTURE_SOURCE/pinshu-infographic" "$FIXTURE_SOURCE/pinshu-business-graphics"
  git -C "$FIXTURE_SOURCE" add -A
  git -C "$FIXTURE_SOURCE" commit -q -m 'old six roster'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  mkdir -p "$HOME_DIR/.agents/skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-content-assets ] && continue
    [ "$skill" = pinshu-visual-system ] && continue
    [ "$skill" = pinshu-film-teardown ] && continue
    [ "$skill" = pinshu-infographic ] && continue
    [ "$skill" = pinshu-business-graphics ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a --exclude='.DS_Store' --exclude='__pycache__/' --exclude='*.pyc' --exclude='*.pyo' --exclude='.git' \
      "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  write_fixture_packages v2 valid
  git -C "$FIXTURE_SOURCE" add -A
  git -C "$FIXTURE_SOURCE" commit -q -m 'current roster'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  run_installer_success
  assert_active_version v2
  repository_backup=$(find "$HOME_DIR/.pinshu-install-backups" -type f -path '*/previous-clone/pinshu-study/payload.txt' -exec grep -l '^v1$' {} \; | head -n 1)
  [ -n "$repository_backup" ] || fail 'old six clone was not preserved'
  assert_absent "$HOME_DIR/.agents/skills/.pinshu-backups/legacy"
}

test_altered_installed_copy_preserved() {
  local old_copy
  new_case altered-copy
  make_remote v1 valid
  run_installer_success
  printf 'local change\n' >"$HOME_DIR/.agents/skills/pinshu-content-assets/local.txt"
  update_remote v2
  run_installer_success
  assert_active_version v2
  assert_absent "$HOME_DIR/.agents/skills/pinshu-content-assets/local.txt"
  old_copy=$(find "$HOME_DIR/.agents/skills/.pinshu-backups" -type f -path '*/pinshu-content-assets/local.txt' -print -quit)
  [ -n "$old_copy" ] || fail 'local Skill change was not preserved in a backup'
  assert_contains "$old_copy" 'local change'
}

test_dirty_old_five_upgrades_to_current_with_backups() {
  local skill old_clone old_copy
  new_case dirty-old-five
  make_remote v1 legacy-five
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  mkdir -p "$HOME_DIR/.agents/skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-study ] && continue
    [ "$skill" = pinshu-content-assets ] && continue
    [ "$skill" = pinshu-visual-system ] && continue
    [ "$skill" = pinshu-film-teardown ] && continue
    [ "$skill" = pinshu-infographic ] && continue
    [ "$skill" = pinshu-business-graphics ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a --exclude='.DS_Store' --exclude='__pycache__/' --exclude='*.pyc' --exclude='*.pyo' --exclude='.git' \
      "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  printf 'edited clone\n' >>"$HOME_DIR/.pinshu-skills/pinshu-transcript/SKILL.md"
  printf 'untracked clone note\n' >"$HOME_DIR/.pinshu-skills/local-note.txt"
  printf 'edited active Skill\n' >>"$HOME_DIR/.agents/skills/pinshu-distill/SKILL.md"
  write_fixture_packages v2 valid
  git -C "$FIXTURE_SOURCE" add -- pinshu-course-capture pinshu-content-assets pinshu-course pinshu-distill pinshu-md2pdf pinshu-study pinshu-transcript pinshu-visual-system pinshu-film-teardown pinshu-infographic pinshu-business-graphics
  git -C "$FIXTURE_SOURCE" commit -q -m 'current roster'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main

  run_installer_success
  assert_active_version v2
  assert_exact_active_roster
  old_clone=$(find "$HOME_DIR/.pinshu-install-backups" -type f -name local-note.txt -print -quit)
  [ -n "$old_clone" ] || fail 'dirty old clone was not preserved'
  assert_contains "$old_clone" 'untracked clone note'
  old_copy=$(find "$HOME_DIR/.agents/skills/.pinshu-backups" -type f -path '*/pinshu-distill/SKILL.md' -exec grep -l 'edited active Skill' {} \; -quit)
  [ -n "$old_copy" ] || fail 'edited active Skill was not preserved'
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
  run_installer_success
  assert_active_version v2
  assert_exact_active_roster
  assert_contains "$LOG_FILE" 'Installed or updated 11 public Pinshu Skills'
  local saved
  saved=$(find "$HOME_DIR/.agents/skills/.pinshu-backups" -type f -path '*/pinshu-transcript/payload.txt' -print -quit)
  [ -n "$saved" ] || fail 'partial old package was not backed up'
  assert_contains "$saved" v1
}

test_local_visual_suite_is_retained_as_a_group() {
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
  for skill in pinshu-visual-system pinshu-infographic pinshu-business-graphics; do
    diff -r "$CASE_ROOT/before-$skill" "$HOME_DIR/.agents/skills/$skill"
  done
  assert_contains "$HOME_DIR/.agents/skills/pinshu-study/payload.txt" v2
  assert_contains "$LOG_FILE" 'Installed or updated 8 public Pinshu Skills'
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
  assert_contains "$LOG_FILE" 'Installed or updated 8 public Pinshu Skills'
  assert_contains "$LOG_FILE" 'kept existing, not upgraded: pinshu-visual-system'
  assert_contains "$LOG_FILE" 'not installed alongside the local suite: pinshu-infographic'
  assert_absent "$HOME_DIR/.agents/skills/pinshu-infographic"
  assert_absent "$HOME_DIR/.agents/skills/pinshu-business-graphics"
  assert_dir "$HOME_DIR/.pinshu-skills/.git"
}

test_seven_package_installation_adds_visual_system() {
  local skill
  new_case seven-to-current
  make_remote v1 valid
  rm -rf -- "$FIXTURE_SOURCE/pinshu-visual-system" "$FIXTURE_SOURCE/pinshu-film-teardown" "$FIXTURE_SOURCE/pinshu-infographic" "$FIXTURE_SOURCE/pinshu-business-graphics"
  git -C "$FIXTURE_SOURCE" add -A
  git -C "$FIXTURE_SOURCE" commit -q -m 'prior seven packages'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-visual-system ] && continue
    [ "$skill" = pinshu-film-teardown ] && continue
    [ "$skill" = pinshu-infographic ] && continue
    [ "$skill" = pinshu-business-graphics ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  write_fixture_packages v2 valid
  git -C "$FIXTURE_SOURCE" add -A
  git -C "$FIXTURE_SOURCE" commit -q -m 'shared visual package'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  run_installer_success
  assert_active_version v2
  assert_exact_active_roster
  assert_file "$HOME_DIR/.agents/skills/pinshu-visual-system/.public-bundle"
  assert_file "$HOME_DIR/.agents/skills/pinshu-film-teardown/SKILL.md"
}

run_test 'private visual core stays active while other Skills install' test_private_visual_system_is_not_replaced
run_test 'prior seven packages upgrade to the current roster with backups' test_seven_package_installation_adds_visual_system

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
    assert_absent "$HOME_DIR/.agents/skills/pinshu-visual-system"
    assert_contains "$LOG_FILE" "kept existing, not upgraded: $skill"
  done
}

test_nine_package_installation_adds_visual_companions() {
  local skill old_clone
  new_case nine-to-eleven
  make_remote v1 valid
  rm -rf -- "$FIXTURE_SOURCE/pinshu-infographic" "$FIXTURE_SOURCE/pinshu-business-graphics"
  git -C "$FIXTURE_SOURCE" add -A
  git -C "$FIXTURE_SOURCE" commit -q -m 'prior nine packages'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  git clone -q "file://$FIXTURE_REMOTE" "$HOME_DIR/.pinshu-skills"
  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ "$skill" = pinshu-infographic ] && continue
    [ "$skill" = pinshu-business-graphics ] && continue
    mkdir -p "$HOME_DIR/.agents/skills/$skill"
    rsync -a "$HOME_DIR/.pinshu-skills/$skill/" "$HOME_DIR/.agents/skills/$skill/"
  done
  write_fixture_packages v2 valid
  git -C "$FIXTURE_SOURCE" add -A
  git -C "$FIXTURE_SOURCE" commit -q -m 'full visual companion set'
  git -C "$FIXTURE_SOURCE" push -q "$FIXTURE_REMOTE" main
  run_installer_success
  assert_active_version v2
  assert_exact_active_roster
  assert_file "$HOME_DIR/.agents/skills/pinshu-infographic/.public-bundle"
  assert_file "$HOME_DIR/.agents/skills/pinshu-business-graphics/.public-bundle"
  old_clone=$(find "$HOME_DIR/.pinshu-install-backups" -type f -path '*/previous-clone/pinshu-film-teardown/payload.txt' -print -quit)
  [ -n "$old_clone" ] || fail 'prior nine-package clone was not preserved'
  assert_contains "$old_clone" 'v1'
}

run_test 'private visual companions stay intact without mixing public core' test_private_visual_companions_are_not_replaced
run_test 'prior nine packages upgrade to eleven with complete backups' test_nine_package_installation_adds_visual_companions

run_test 'owned old-six installation upgrades to the current roster with backups' test_old_six_owned_upgrade
run_test 'altered installed copy is backed up during upgrade' test_altered_installed_copy_preserved
run_test 'dirty old five upgrades to the current roster and preserves local edits' test_dirty_old_five_upgrades_to_current_with_backups
run_test 'repeated upgrade replaces stale content and preserves backup' test_repeated_upgrade
run_test 'partial installed packages without a prior clone upgrade and complete' test_partial_install_without_clone
run_test 'mixed private and public visual suite stays consistent during upgrade' test_local_visual_suite_is_retained_as_a_group
run_test 'existing Claude package stays intact while missing links are added' test_existing_claude_package_conflict_is_retained
run_test 'Linux rsync timestamp-only output permits owned upgrade' test_linux_rsync_timestamp_only_upgrade
run_test 'conflicting Claude path is left untouched' test_conflicting_claude_path_is_untouched
run_test 'invalid repository roster causes no active mutation' test_invalid_roster_causes_no_active_mutation
run_test 'mid-transaction failure restores all prior active paths' test_mid_transaction_failure_rolls_back
run_test 'symlink install directory is refused' test_symlink_install_dir_refusal
run_test 'special-file destination is refused' test_special_file_destination_refusal
run_test 'escaping destination path is refused' test_escaping_destination_refusal
run_test 'existing installer lock prevents a second run' test_existing_lock_refusal
run_test 'symlink backup container is refused' test_symlink_backup_container_refusal

printf '%s passed; %s failed\n' "$PASS_COUNT" "$FAIL_COUNT"
[ "$FAIL_COUNT" -eq 0 ]
