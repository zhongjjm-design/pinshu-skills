#!/usr/bin/env bash

# Transactional installer for Aidan's original Pinshu Skills.
# Usage: curl -fsSL https://raw.githubusercontent.com/zhongjjm-design/pinshu-skills/main/install.sh | bash

set -euo pipefail

OFFICIAL_REPO="https://github.com/zhongjjm-design/pinshu-skills.git"
HOME_ROOT=${HOME%/}
REPO="${PINSHU_REPO:-$OFFICIAL_REPO}"
INSTALL_DIR="${PINSHU_INSTALL_DIR:-$HOME_ROOT/.pinshu-skills}"
SKILLS_DIR="${PINSHU_SKILLS_DIR:-$HOME_ROOT/.agents/skills}"
LOCK_DIR="$HOME_ROOT/.pinshu-installer.lock"

EXPECTED_SKILLS=(
  pinshu-course-capture
  pinshu-content-assets
  pinshu-course
  pinshu-distill
  pinshu-md2pdf
  pinshu-study
  pinshu-transcript
)
LEGACY_SKILLS=(
  transcript-cleaner
  transcript-organizer
  course-knowledge-base-builder
  transcript-formatter
  pinshu-md-to-pdf
)

WORK_ROOT=""
ACQUIRED_REPO=""
SKILL_STAGE_ROOT=""
INSTALL_STAGE_PARENT=""
INSTALL_STAGE=""
SKILLS_BACKUP_ROOT=""
INSTALL_BACKUP_ROOT=""
LOCK_HELD=0
TRANSACTION_STARTED=0
COMMITTED=0
ROLLBACK_FAILED=0
BACKED_UP_TARGETS=()
BACKUP_PATHS=()
NEW_TARGETS=()

printf_error() {
  printf 'Error: %s\n' "$*" >&2
}

die() {
  printf_error "$*"
  exit 1
}

path_exists() {
  [ -e "$1" ] || [ -L "$1" ]
}

validate_path_syntax() {
  local path=$1
  local label=$2

  [ -n "$path" ] || die "$label is empty."
  case "$path" in
    /*) ;;
    *) die "$label must be an absolute path: $path" ;;
  esac
  case "$path" in
    /) die "$label must not be the filesystem root." ;;
    *$'\n'*|*$'\r'*|*$'\t'*) die "$label contains a control character." ;;
    *//*|*/./*|*/.|*/../*|*/..) die "$label contains an unsafe path segment: $path" ;;
  esac
}

assert_directory_chain() {
  local path=$1
  local label=$2
  local remainder=${path#/}
  local current=""
  local component
  local old_ifs=$IFS
  local parts=()

  IFS='/' read -r -a parts <<<"$remainder"
  IFS=$old_ifs
  for component in "${parts[@]}"; do
    [ -n "$component" ] || die "$label contains an empty path component: $path"
    current="$current/$component"
    if [ -L "$current" ]; then
      die "$label contains a symlink component and was refused: $current"
    fi
    if [ -e "$current" ] && [ ! -d "$current" ]; then
      die "$label contains a non-directory component and was refused: $current"
    fi
  done
}

assert_safe_slug() {
  local slug=$1
  [[ "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || die "Unsafe Skill slug: $slug"
}

is_expected_skill() {
  case "$1" in
    pinshu-course-capture|pinshu-content-assets|pinshu-course|pinshu-distill|pinshu-md2pdf|pinshu-study|pinshu-transcript)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

validate_configuration() {
  local slug

  validate_path_syntax "$HOME_ROOT" "HOME"
  validate_path_syntax "$INSTALL_DIR" "PINSHU_INSTALL_DIR"
  validate_path_syntax "$SKILLS_DIR" "PINSHU_SKILLS_DIR"
  assert_directory_chain "$HOME_ROOT" "HOME"

  [ -n "$REPO" ] || die "PINSHU_REPO is empty."
  case "$REPO" in
    *$'\n'*|*$'\r'*|*$'\t'*) die "PINSHU_REPO contains a control character." ;;
  esac

  case "$INSTALL_DIR/" in
    "$SKILLS_DIR/"*) die "PINSHU_INSTALL_DIR must not be inside PINSHU_SKILLS_DIR." ;;
  esac
  case "$SKILLS_DIR/" in
    "$INSTALL_DIR/"*) die "PINSHU_SKILLS_DIR must not be inside PINSHU_INSTALL_DIR." ;;
  esac

  case "$(basename -- "$INSTALL_DIR")" in
    .pinshu-install-backups|.pinshu-clone-stage.*)
      die "PINSHU_INSTALL_DIR uses a reserved installer path."
      ;;
  esac

  for slug in "${EXPECTED_SKILLS[@]}" "${LEGACY_SKILLS[@]}"; do
    assert_safe_slug "$slug"
  done
}

preflight_target_paths() {
  local slug
  local target
  local install_parent

  install_parent=$(dirname -- "$INSTALL_DIR")
  assert_directory_chain "$SKILLS_DIR" "PINSHU_SKILLS_DIR"
  assert_directory_chain "$install_parent" "PINSHU_INSTALL_DIR parent"
  assert_directory_chain "$SKILLS_DIR/.pinshu-backups" "Skill backup container"
  assert_directory_chain "$install_parent/.pinshu-install-backups" "repository backup container"

  if path_exists "$INSTALL_DIR"; then
    [ ! -L "$INSTALL_DIR" ] || die "PINSHU_INSTALL_DIR is a symlink and was refused: $INSTALL_DIR"
    [ -d "$INSTALL_DIR" ] || die "PINSHU_INSTALL_DIR is not a real directory: $INSTALL_DIR"
  fi

  for slug in "${EXPECTED_SKILLS[@]}"; do
    target="$SKILLS_DIR/$slug"
    case "$target" in
      "$SKILLS_DIR"/*) ;;
      *) die "Skill destination escapes PINSHU_SKILLS_DIR: $target" ;;
    esac
    if path_exists "$target"; then
      [ ! -L "$target" ] || die "Destination symlink was refused: $target"
      [ -d "$target" ] || die "Destination is not a real directory: $target"
    fi
  done
}

# Earlier six-package installs have no marker. Require an exact origin and an
# unmodified clone, then compare every installed copy against its clone source.
preflight_owned_installation() {
  local skill origin status differences change bad_entry old_six=0
  local installed_count=0

  if ! path_exists "$INSTALL_DIR"; then
    for skill in "${EXPECTED_SKILLS[@]}"; do
      path_exists "$SKILLS_DIR/$skill" && die "Unowned Skill destination was refused: $SKILLS_DIR/$skill"
    done
    return 0
  fi

  [ -d "$INSTALL_DIR/.git" ] && [ ! -L "$INSTALL_DIR/.git" ] || die "Existing clone cannot prove ownership: $INSTALL_DIR"
  origin=$(git -C "$INSTALL_DIR" remote get-url origin) || die "Existing clone has no origin: $INSTALL_DIR"
  [ "$origin" = "$REPO" ] || die "Existing clone origin does not match the requested repository: $INSTALL_DIR"
  status=$(git -C "$INSTALL_DIR" status --porcelain --untracked-files=all) || die "Existing clone cannot be inspected: $INSTALL_DIR"
  [ -z "$status" ] || die "Existing clone has local changes; refusing upgrade: $INSTALL_DIR"

  if [ ! -e "$INSTALL_DIR/pinshu-content-assets" ] && [ ! -L "$INSTALL_DIR/pinshu-content-assets" ]; then
    old_six=1
  fi
  for skill in "${EXPECTED_SKILLS[@]}"; do
    if [ "$old_six" -eq 1 ] && [ "$skill" = pinshu-content-assets ]; then
      path_exists "$SKILLS_DIR/$skill" && die "Unowned Skill destination was refused: $SKILLS_DIR/$skill"
      continue
    fi
    [ -d "$INSTALL_DIR/$skill" ] && [ ! -L "$INSTALL_DIR/$skill" ] || die "Existing clone lacks expected package: $skill"
    [ -f "$INSTALL_DIR/$skill/SKILL.md" ] && [ ! -L "$INSTALL_DIR/$skill/SKILL.md" ] || die "Existing clone has invalid package: $skill"
    [ -d "$SKILLS_DIR/$skill" ] && [ ! -L "$SKILLS_DIR/$skill" ] || die "Installed copy is missing or not a real directory: $skill"
    bad_entry=$(find "$INSTALL_DIR/$skill" "$SKILLS_DIR/$skill" ! -type d ! -type f -print -quit)
    [ -z "$bad_entry" ] || die "Existing package contains a symlink or special file: $bad_entry"
    bad_entry=$(find "$SKILLS_DIR/$skill" \( -name .DS_Store -o -name __pycache__ -o -name '*.pyc' -o -name '*.pyo' -o -name .git \) -print -quit)
    [ -z "$bad_entry" ] || die "Installed copy has unexpected generated content: $bad_entry"
    differences=$(rsync -a --checksum --delete --dry-run --itemize-changes \
      --exclude='.DS_Store' --exclude='__pycache__/' \
      --exclude='*.pyc' --exclude='*.pyo' --exclude='.git' \
      "$INSTALL_DIR/$skill/" "$SKILLS_DIR/$skill/") || die "Cannot compare installed copy: $skill"
    # Git checkout timestamps need not match the earlier rsync copy. Ignore
    # timestamp-only reports, but reject any byte, mode, type or path change.
    while IFS= read -r change; do
      case "$change" in
        ''|'.f..t.... '*|'.d..t.... '*|'.f..T.... '*|'.d..T.... '*|'.f..t...... '*|'.d..t...... '*|'.f..T...... '*|'.d..T...... '*) ;;
        *) die "Installed copy differs from the owned clone: $skill ($change)" ;;
      esac
    done <<< "$differences"
    installed_count=$((installed_count + 1))
  done
  if [ "$old_six" -eq 1 ]; then
    [ "$installed_count" -eq 6 ] || die "Existing six-package installation is incomplete."
  else
    [ "$installed_count" -eq 7 ] || die "Existing seven-package installation is incomplete."
  fi
}

validate_repository() {
  local repository=$1
  local candidate
  local name
  local skill
  local bad_entry
  local found_count=0

  [ -d "$repository/.git" ] || die "Acquired repository is not a Git clone."

  shopt -s nullglob
  for candidate in "$repository"/pinshu-*; do
    if [ -d "$candidate" ] || [ -L "$candidate" ]; then
      name=$(basename -- "$candidate")
      assert_safe_slug "$name"
      is_expected_skill "$name" || die "Unexpected Pinshu package directory in repository: $name"
      [ ! -L "$candidate" ] || die "Repository package directory is a symlink: $name"
      found_count=$((found_count + 1))
    fi
  done
  shopt -u nullglob

  [ "$found_count" -eq "${#EXPECTED_SKILLS[@]}" ] || die "Repository package roster is incomplete. Expected seven packages, found $found_count."

  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ -d "$repository/$skill" ] && [ ! -L "$repository/$skill" ] || die "Missing repository package: $skill"
    [ -f "$repository/$skill/SKILL.md" ] && [ ! -L "$repository/$skill/SKILL.md" ] || die "Package lacks a regular SKILL.md: $skill"

    bad_entry=$(find "$repository/$skill" ! -type d ! -type f -print -quit)
    [ -z "$bad_entry" ] || die "Package contains a symlink or special file and was refused: $bad_entry"
  done
}

validate_staged_skills() {
  local skill
  local bad_entry

  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ -d "$SKILL_STAGE_ROOT/$skill" ] && [ ! -L "$SKILL_STAGE_ROOT/$skill" ] || die "Staged package is not a real directory: $skill"
    [ -f "$SKILL_STAGE_ROOT/$skill/SKILL.md" ] && [ ! -L "$SKILL_STAGE_ROOT/$skill/SKILL.md" ] || die "Staged package lacks a regular SKILL.md: $skill"
  done

  bad_entry=$(find "$SKILL_STAGE_ROOT" \( -name .DS_Store -o -name __pycache__ -o -name '*.pyc' -o -name '*.pyo' -o -name .git \) -print -quit)
  [ -z "$bad_entry" ] || die "Forbidden generated content reached the staging tree: $bad_entry"
}

safe_remove_temp_tree() {
  local path=${1:-}
  local name

  [ -n "$path" ] || return 0
  name=$(basename -- "$path")
  case "$name" in
    pinshu-installer.*|.pinshu-stage.*|.pinshu-clone-stage.*) ;;
    *)
      printf_error "Refusing to clean unexpected temporary path: $path"
      return 1
      ;;
  esac
  if [ -L "$path" ]; then
    printf_error "Refusing to clean a temporary path that became a symlink: $path"
    return 1
  fi
  if [ -d "$path" ]; then
    rm -rf -- "$path"
  fi
}

backup_target() {
  local target=$1
  local backup=$2

  if path_exists "$target"; then
    mkdir -p -- "$(dirname -- "$backup")"
    mv -- "$target" "$backup"
    BACKED_UP_TARGETS+=("$target")
    BACKUP_PATHS+=("$backup")
  fi
}

install_staged_target() {
  local staged=$1
  local target=$2

  mv -- "$staged" "$target"
  NEW_TARGETS+=("$target")
}

rollback_transaction() {
  local index
  local target
  local backup
  local quarantine
  local quarantine_root

  printf_error "Installation failed; restoring all prior active paths."

  index=${#NEW_TARGETS[@]}
  while [ "$index" -gt 0 ]; do
    index=$((index - 1))
    target=${NEW_TARGETS[$index]}
    if path_exists "$target"; then
      if [ "$target" = "$INSTALL_DIR" ]; then
        quarantine_root="$INSTALL_BACKUP_ROOT/failed-new"
      else
        quarantine_root="$SKILLS_BACKUP_ROOT/failed-new"
      fi
      mkdir -p "$quarantine_root"
      quarantine="$quarantine_root/$(basename -- "$target")"
      if ! mv -- "$target" "$quarantine"; then
        printf_error "Rollback could not quarantine new path: $target"
        ROLLBACK_FAILED=1
      fi
    fi
  done

  index=${#BACKED_UP_TARGETS[@]}
  while [ "$index" -gt 0 ]; do
    index=$((index - 1))
    target=${BACKED_UP_TARGETS[$index]}
    backup=${BACKUP_PATHS[$index]}
    if path_exists "$target"; then
      printf_error "Rollback target is occupied; prior data remains at: $backup"
      ROLLBACK_FAILED=1
    elif path_exists "$backup"; then
      if ! mv -- "$backup" "$target"; then
        printf_error "Rollback could not restore $target from $backup"
        ROLLBACK_FAILED=1
      fi
    else
      printf_error "Rollback backup is missing: $backup"
      ROLLBACK_FAILED=1
    fi
  done

  if [ "$ROLLBACK_FAILED" -eq 0 ]; then
    printf_error "Rollback completed. Prior active paths were restored."
  else
    printf_error "Rollback was incomplete. Inspect backups under $SKILLS_BACKUP_ROOT and $INSTALL_BACKUP_ROOT."
  fi
}

cleanup() {
  safe_remove_temp_tree "$SKILL_STAGE_ROOT" || true
  safe_remove_temp_tree "$INSTALL_STAGE_PARENT" || true
  safe_remove_temp_tree "$WORK_ROOT" || true

  if [ "$LOCK_HELD" -eq 1 ]; then
    if [ -d "$LOCK_DIR" ] && [ ! -L "$LOCK_DIR" ]; then
      rmdir -- "$LOCK_DIR" 2>/dev/null || printf_error "Could not remove installer lock: $LOCK_DIR"
    else
      printf_error "Installer lock changed type and was not removed: $LOCK_DIR"
    fi
  fi
}

on_exit() {
  local status=$1

  trap - EXIT
  set +e
  if [ "$status" -ne 0 ] && [ "$TRANSACTION_STARTED" -eq 1 ] && [ "$COMMITTED" -eq 0 ]; then
    rollback_transaction
  fi
  cleanup
  exit "$status"
}

validate_active_installation() {
  local skill

  for skill in "${EXPECTED_SKILLS[@]}"; do
    [ -d "$SKILLS_DIR/$skill" ] && [ ! -L "$SKILLS_DIR/$skill" ] || die "Installed package is not a real directory: $skill"
    [ -f "$SKILLS_DIR/$skill/SKILL.md" ] && [ ! -L "$SKILLS_DIR/$skill/SKILL.md" ] || die "Installed package lacks a regular SKILL.md: $skill"
  done
  [ -d "$INSTALL_DIR/.git" ] && [ ! -L "$INSTALL_DIR/.git" ] || die "Local repository clone is invalid: $INSTALL_DIR"
  validate_repository "$INSTALL_DIR"
}

handle_claude_link() {
  local claude_dir="$HOME_ROOT/.claude"
  local claude_skills="$claude_dir/skills"

  validate_path_syntax "$claude_dir" "Claude configuration directory"

  if path_exists "$claude_dir"; then
    if [ -L "$claude_dir" ] || [ ! -d "$claude_dir" ]; then
      printf 'Warning: %s is not a real directory; Claude skills link was not created.\n' "$claude_dir"
      return 0
    fi
  else
    if ! mkdir -- "$claude_dir"; then
      printf 'Warning: could not create %s; Claude skills link was not created.\n' "$claude_dir"
      return 0
    fi
  fi

  if path_exists "$claude_skills"; then
    printf 'Warning: %s already exists and was left untouched.\n' "$claude_skills"
    return 0
  fi

  if ln -s -- "$SKILLS_DIR" "$claude_skills"; then
    printf 'Created Claude skills link: %s -> %s\n' "$claude_skills" "$SKILLS_DIR"
  else
    printf 'Warning: could not create %s; installed Skills remain available at %s.\n' "$claude_skills" "$SKILLS_DIR"
  fi
}

trap 'on_exit $?' EXIT
trap 'exit 130' INT TERM HUP

validate_configuration
preflight_target_paths

if path_exists "$LOCK_DIR"; then
  die "Another Pinshu installer run is active or left a stale lock: $LOCK_DIR"
fi
mkdir -- "$LOCK_DIR" || die "Could not acquire installer lock: $LOCK_DIR"
LOCK_HELD=1

printf 'Acquiring Pinshu Skills repository...\n'
WORK_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/pinshu-installer.XXXXXX")
ACQUIRED_REPO="$WORK_ROOT/repository"
git clone --quiet --depth 1 -- "$REPO" "$ACQUIRED_REPO"
validate_repository "$ACQUIRED_REPO"

# Repository acquisition and validation are complete before any active path mutation.
preflight_target_paths
preflight_owned_installation
mkdir -p -- "$SKILLS_DIR" "$(dirname -- "$INSTALL_DIR")"
assert_directory_chain "$SKILLS_DIR" "PINSHU_SKILLS_DIR"
assert_directory_chain "$(dirname -- "$INSTALL_DIR")" "PINSHU_INSTALL_DIR parent"

SKILL_STAGE_ROOT=$(mktemp -d "$SKILLS_DIR/.pinshu-stage.XXXXXX")
for skill in "${EXPECTED_SKILLS[@]}"; do
  mkdir -- "$SKILL_STAGE_ROOT/$skill"
  rsync -a \
    --exclude='.DS_Store' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='.git' \
    "$ACQUIRED_REPO/$skill/" "$SKILL_STAGE_ROOT/$skill/"
done
validate_staged_skills

INSTALL_PARENT=$(dirname -- "$INSTALL_DIR")
INSTALL_STAGE_PARENT=$(mktemp -d "$INSTALL_PARENT/.pinshu-clone-stage.XXXXXX")
INSTALL_STAGE="$INSTALL_STAGE_PARENT/repository"
git clone --quiet --no-hardlinks "$ACQUIRED_REPO" "$INSTALL_STAGE"
git -C "$INSTALL_STAGE" remote set-url origin "$REPO"
validate_repository "$INSTALL_STAGE"

# Repeat preflight after staging to narrow the race window before the transaction.
preflight_target_paths
preflight_owned_installation
RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
SKILLS_BACKUP_ROOT="$SKILLS_DIR/.pinshu-backups/$RUN_ID"
INSTALL_BACKUP_ROOT="$INSTALL_PARENT/.pinshu-install-backups/$RUN_ID"
[ ! -e "$SKILLS_BACKUP_ROOT" ] && [ ! -L "$SKILLS_BACKUP_ROOT" ] || die "Backup path already exists: $SKILLS_BACKUP_ROOT"
[ ! -e "$INSTALL_BACKUP_ROOT" ] && [ ! -L "$INSTALL_BACKUP_ROOT" ] || die "Backup path already exists: $INSTALL_BACKUP_ROOT"

TRANSACTION_STARTED=1
for skill in "${EXPECTED_SKILLS[@]}"; do
  backup_target "$SKILLS_DIR/$skill" "$SKILLS_BACKUP_ROOT/active/$skill"
done
backup_target "$INSTALL_DIR" "$INSTALL_BACKUP_ROOT/previous-clone"

for skill in "${EXPECTED_SKILLS[@]}"; do
  install_staged_target "$SKILL_STAGE_ROOT/$skill" "$SKILLS_DIR/$skill"
done
install_staged_target "$INSTALL_STAGE" "$INSTALL_DIR"

validate_active_installation
COMMITTED=1
TRANSACTION_STARTED=0

if [ -d "$SKILLS_BACKUP_ROOT" ] && [ -n "$(find "$SKILLS_BACKUP_ROOT" -mindepth 1 -print -quit)" ]; then
  printf 'Preserved Skill backups: %s\n' "$SKILLS_BACKUP_ROOT"
fi
if path_exists "$INSTALL_BACKUP_ROOT/previous-clone"; then
  printf 'Preserved repository backup: %s\n' "$INSTALL_BACKUP_ROOT"
fi

handle_claude_link
for skill in "${LEGACY_SKILLS[@]}"; do
  if path_exists "$SKILLS_DIR/$skill"; then
    printf 'Warning: legacy path has no ownership proof and was left untouched: %s\n' "$SKILLS_DIR/$skill"
  fi
done
printf 'Installed Pinshu Skills:\n'
printf '  - %s\n' "${EXPECTED_SKILLS[@]}"
printf 'Installation complete. Restart your Agent client.\n'
