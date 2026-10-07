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
  pinshu-visual-system
  pinshu-film-teardown
  pinshu-infographic
  pinshu-business-graphics
)
LEGACY_SKILLS=(
  transcript-cleaner
  transcript-organizer
  course-knowledge-base-builder
  transcript-formatter
  pinshu-md-to-pdf
)

INSTALL_SKILLS=()
KEPT_SKILLS=()
LINKED_SKILLS=()
KEEP_LOCAL_VISUALS=0
VISUAL_SELECTION=""

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
    pinshu-course-capture|pinshu-content-assets|pinshu-course|pinshu-distill|pinshu-md2pdf|pinshu-study|pinshu-transcript|pinshu-visual-system|pinshu-film-teardown|pinshu-infographic|pinshu-business-graphics)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_visual_skill() {
  case "$1" in
    pinshu-visual-system|pinshu-infographic|pinshu-business-graphics) return 0 ;;
    *) return 1 ;;
  esac
}

is_managed_visual_link() {
  local slug=$1 target="$SKILLS_DIR/$1"
  case "$slug" in pinshu-infographic|pinshu-business-graphics) ;; *) return 1 ;; esac
  [ -L "$target" ] || return 1
  [ "$(readlink "$target")" = "$INSTALL_DIR/$slug" ] || return 1
  [ -d "$INSTALL_DIR/.git" ] && [ ! -L "$INSTALL_DIR" ] || return 1
  [ -d "$INSTALL_DIR/$slug" ] && [ ! -L "$INSTALL_DIR/$slug" ] || return 1
  [ -f "$target/.public-bundle" ] && [ ! -L "$target/.public-bundle" ] || return 1
  [ -f "$target/SKILL.md" ] && [ ! -L "$target/SKILL.md" ] || return 1
  grep -Eq "^name:[[:space:]]*$slug[[:space:]]*$" "$target/SKILL.md"
}

is_linked_selection() {
  local slug
  for slug in ${LINKED_SKILLS[@]+"${LINKED_SKILLS[@]}"}; do
    [ "$slug" != "$1" ] || return 0
  done
  return 1
}

is_local_visual() {
  local target="$SKILLS_DIR/$1"
  is_visual_skill "$1" && path_exists "$target" &&
    { [ ! -f "$target/.public-bundle" ] || [ -L "$target/.public-bundle" ]; }
}

has_local_visual_suite() {
  local slug
  for slug in pinshu-visual-system pinshu-infographic pinshu-business-graphics; do
    if is_local_visual "$slug"; then
      return 0
    fi
  done
  return 1
}

visual_selection_signature() {
  local slug target
  for slug in pinshu-visual-system pinshu-infographic pinshu-business-graphics; do
    target="$SKILLS_DIR/$slug"
    if is_local_visual "$slug"; then printf '%s:local\n' "$slug"
    elif is_managed_visual_link "$slug"; then printf '%s:linked\n' "$slug"
    elif path_exists "$target"; then printf '%s:public\n' "$slug"
    else printf '%s:missing\n' "$slug"; fi
  done
}

select_installation_skills() {
  local skill
  if has_local_visual_suite; then
    KEEP_LOCAL_VISUALS=1
    printf 'Keeping local visual packages; missing public companions will use their own public core.\n'
  fi
  for skill in "${EXPECTED_SKILLS[@]}"; do
    # Preserve an existing core when private companions may depend on it.
    if is_local_visual "$skill" || { [ "$KEEP_LOCAL_VISUALS" -eq 1 ] && [ "$skill" = pinshu-visual-system ] && path_exists "$SKILLS_DIR/$skill"; }; then
      KEPT_SKILLS+=("$skill")
      continue
    fi
    INSTALL_SKILLS+=("$skill")
    if is_visual_skill "$skill" && [ "$skill" != pinshu-visual-system ] && { [ "$KEEP_LOCAL_VISUALS" -eq 1 ] || is_managed_visual_link "$skill"; }; then
      LINKED_SKILLS+=("$skill")
    fi
  done
  VISUAL_SELECTION=$(visual_selection_signature)
}

check_visual_selection_unchanged() {
  [ "$(visual_selection_signature)" = "$VISUAL_SELECTION" ] || die "Visual installation changed during staging; rerun to select a consistent suite."
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
      if [ -L "$target" ]; then
        is_managed_visual_link "$slug" || die "Destination symlink was refused: $target"
      fi
      [ -d "$target" ] || die "Destination is not a real directory: $target"
    fi
  done
}

# A prior official clone may be dirty and may contain an earlier roster of
# packages. Back it up intact. Existing correctly named Skill directories are
# backed up intact too; a same-name directory without a matching Skill identity
# is refused rather than silently replaced.
preflight_previous_installation() {
  local skill origin target

  if path_exists "$INSTALL_DIR"; then
    [ -d "$INSTALL_DIR/.git" ] && [ ! -L "$INSTALL_DIR/.git" ] || die "Existing installation directory is not an official Git clone: $INSTALL_DIR"
    origin=$(git -C "$INSTALL_DIR" remote get-url origin) || die "Existing clone has no origin: $INSTALL_DIR"
    if [ "$REPO" = "$OFFICIAL_REPO" ]; then
      case "$origin" in
        "$OFFICIAL_REPO"|https://github.com/zhongjjm-design/pinshu-skills) ;;
        *) die "Existing clone origin does not match Pinshu's repository: $INSTALL_DIR" ;;
      esac
    else
      [ "$origin" = "$REPO" ] || die "Existing clone origin does not match the requested repository: $INSTALL_DIR"
    fi
  fi

  for skill in "${EXPECTED_SKILLS[@]}"; do
    target="$SKILLS_DIR/$skill"
    if path_exists "$target"; then
      [ -d "$target" ] || die "Destination is not a directory: $target"
      if [ -L "$target" ]; then
        is_managed_visual_link "$skill" || die "Destination symlink was refused: $target"
      fi
      [ -f "$target/SKILL.md" ] && [ ! -L "$target/SKILL.md" ] || die "Existing Skill lacks a regular SKILL.md: $target"
      grep -Eq "^name:[[:space:]]*$skill[[:space:]]*$" "$target/SKILL.md" || die "Existing Skill name does not match its directory: $target"
    fi
  done
  printf 'Preserving existing Pinshu files in backups before installation.\n'
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

  [ "$found_count" -eq "${#EXPECTED_SKILLS[@]}" ] || die "Repository package roster is incomplete. Expected ${#EXPECTED_SKILLS[@]} packages, found $found_count."

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

  for skill in "${INSTALL_SKILLS[@]}"; do
    if is_linked_selection "$skill"; then
      [ -L "$SKILL_STAGE_ROOT/$skill" ] && [ "$(readlink "$SKILL_STAGE_ROOT/$skill")" = "$INSTALL_DIR/$skill" ] || die "Staged public link is invalid: $skill"
      continue
    fi
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

  for skill in "${INSTALL_SKILLS[@]}"; do
    if is_linked_selection "$skill"; then
      is_managed_visual_link "$skill" || die "Installed public link is invalid: $skill"
      continue
    fi
    [ -d "$SKILLS_DIR/$skill" ] && [ ! -L "$SKILLS_DIR/$skill" ] || die "Installed package is not a real directory: $skill"
    [ -f "$SKILLS_DIR/$skill/SKILL.md" ] && [ ! -L "$SKILLS_DIR/$skill/SKILL.md" ] || die "Installed package lacks a regular SKILL.md: $skill"
  done
  [ -d "$INSTALL_DIR/.git" ] && [ ! -L "$INSTALL_DIR/.git" ] || die "Local repository clone is invalid: $INSTALL_DIR"
  validate_repository "$INSTALL_DIR"
}

handle_claude_link() {
  local claude_dir="$HOME_ROOT/.claude"
  local claude_skills="$claude_dir/skills"
  local skill target

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
    if [ -L "$claude_skills" ]; then
      if [ "$(readlink "$claude_skills")" = "$SKILLS_DIR" ]; then
        printf 'Claude already uses the shared Skills directory.\n'
      else
        printf 'Warning: %s points elsewhere and was left untouched.\n' "$claude_skills"
      fi
    elif [ -d "$claude_skills" ]; then
      for skill in "${EXPECTED_SKILLS[@]}"; do
        target="$claude_skills/$skill"
        [ -f "$SKILLS_DIR/$skill/SKILL.md" ] || continue
        if ! path_exists "$target"; then
          if ln -s -- "$SKILLS_DIR/$skill" "$target"; then
            printf 'Added Claude Skill link: %s\n' "$target"
          else
            printf 'Warning: could not create Claude Skill link: %s\n' "$target"
          fi
        elif [ -L "$target" ] && [ "$(readlink "$target")" = "$SKILLS_DIR/$skill" ]; then
          :
        else
          printf 'Warning: existing Claude Skill was left untouched: %s\n' "$target"
        fi
      done
    else
      printf 'Warning: %s is not a directory and was left untouched.\n' "$claude_skills"
    fi
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
preflight_previous_installation
select_installation_skills
mkdir -p -- "$SKILLS_DIR" "$(dirname -- "$INSTALL_DIR")"
assert_directory_chain "$SKILLS_DIR" "PINSHU_SKILLS_DIR"
assert_directory_chain "$(dirname -- "$INSTALL_DIR")" "PINSHU_INSTALL_DIR parent"

SKILL_STAGE_ROOT=$(mktemp -d "$SKILLS_DIR/.pinshu-stage.XXXXXX")
for skill in "${INSTALL_SKILLS[@]}"; do
  if is_linked_selection "$skill"; then
    ln -s -- "$INSTALL_DIR/$skill" "$SKILL_STAGE_ROOT/$skill"
    continue
  fi
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
preflight_previous_installation
check_visual_selection_unchanged
RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
SKILLS_BACKUP_ROOT="$SKILLS_DIR/.pinshu-backups/$RUN_ID"
INSTALL_BACKUP_ROOT="$INSTALL_PARENT/.pinshu-install-backups/$RUN_ID"
[ ! -e "$SKILLS_BACKUP_ROOT" ] && [ ! -L "$SKILLS_BACKUP_ROOT" ] || die "Backup path already exists: $SKILLS_BACKUP_ROOT"
[ ! -e "$INSTALL_BACKUP_ROOT" ] && [ ! -L "$INSTALL_BACKUP_ROOT" ] || die "Backup path already exists: $INSTALL_BACKUP_ROOT"

TRANSACTION_STARTED=1
for skill in "${INSTALL_SKILLS[@]}"; do
  backup_target "$SKILLS_DIR/$skill" "$SKILLS_BACKUP_ROOT/active/$skill"
done
backup_target "$INSTALL_DIR" "$INSTALL_BACKUP_ROOT/previous-clone"

install_staged_target "$INSTALL_STAGE" "$INSTALL_DIR"
for skill in "${INSTALL_SKILLS[@]}"; do
  install_staged_target "$SKILL_STAGE_ROOT/$skill" "$SKILLS_DIR/$skill"
done

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
printf 'Installed or updated %s public Pinshu Skills:\n' "${#INSTALL_SKILLS[@]}"
printf '  - %s\n' "${INSTALL_SKILLS[@]}"
if [ "${#KEPT_SKILLS[@]}" -gt 0 ]; then
  printf 'Existing local visual packages retained without replacement:\n'
  printf '  - kept existing, not upgraded: %s\n' "${KEPT_SKILLS[@]}"
fi
if [ "${#LINKED_SKILLS[@]}" -gt 0 ]; then
  printf 'Public visual entry points use the complete public suite in %s:\n' "$INSTALL_DIR"
  printf '  - linked to public suite: %s\n' "${LINKED_SKILLS[@]}"
fi
printf 'Installation complete. Restart your Agent client.\n'
