#!/usr/bin/env zsh
set -euo pipefail

# --------------------------------------------------------------------
#   Tiny Checklist (for you and for students)
#
#   1. Make sure this repo has no uncommitted changes:
#        git status
#
#   2. Run:
#        ./update-submodules.sh
#      Or to auto-commit:
#        ./update-submodules.sh --commit
#      Or commit + push:
#        ./update-submodules.sh --push
#
#   3. This updates submodules (by path):
#        • classlib      → HickernellClassLib repo
#        • qmcsoftware   → QMCSoftware (develop branch)
# --------------------------------------------------------------------

AUTO_COMMIT=0
AUTO_PUSH=0

case "${1:-}" in
  --commit)
    AUTO_COMMIT=1
    ;;
  --push)
    AUTO_COMMIT=1
    AUTO_PUSH=1
    ;;
  "")
    ;;
  *)
    echo "Usage: $(basename "$0") [--commit | --push]"
    exit 1
    ;;
esac

log() {
  local ts
  ts=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$ts] $*"
}

# Must run from repo root
if [[ ! -d ".git" ]]; then
  echo "Error: run this script from the root of the repository."
  exit 1
fi

SCRIPT_NAME="$(basename "$0")"
EXTRA_FLAGS=""
if [[ "$AUTO_PUSH" -eq 1 ]]; then
  EXTRA_FLAGS=" --push"
elif [[ "$AUTO_COMMIT" -eq 1 ]]; then
  EXTRA_FLAGS=" --commit"
fi

ensure_clean_worktree() {
  local ws
  ws="$(git status --porcelain)"

  # Completely clean — good to go
  if [[ -z "${ws}" ]]; then
    return 0
  fi

  # Check if *only* submodule pointers (classlib/qmcsoftware) are dirty
  local only_submodules=1
  local line path
  while IFS= read -r line; do
    path="${line##* }"
    if [[ "${path}" != "classlib" && "${path}" != "qmcsoftware" ]]; then
      only_submodules=0
      break
    fi
  done <<< "${ws}"

  if (( only_submodules == 1 )); then
    log "Uncommitted changes present — submodule pointers (classlib/qmcsoftware) are modified."
    echo
    echo "git status --short:"
    echo "${ws}"
    echo
    echo "This usually means:"
    echo "  • You pulled new changes and updated submodule pointers."
    echo "  • A previous run of this script stopped before committing."
    echo
    echo "To record these pointer updates, run:"
    echo "  git add classlib qmcsoftware"
    echo "  git commit -m \"Update submodule pointers\""
    echo
    echo "To discard them, run:"
    echo "  git restore --staged classlib qmcsoftware 2>/dev/null || true"
    echo "  git submodule update --init --recursive"
    echo
    echo "Then re-run:"
    echo "  ./${SCRIPT_NAME}${EXTRA_FLAGS}"
  else
    log "Uncommitted changes present — working tree is not clean."
    echo
    echo "git status --short:"
    echo "${ws}"
    echo
    echo "Please commit, stash, or discard these changes before running:"
    echo "  ./${SCRIPT_NAME}${EXTRA_FLAGS}"
  fi
  exit 1
}


ensure_clean_worktree

# IMPORTANT: these are **paths** in the repo, not GitHub names
SUBMODULES=(
  "classlib"
  "qmcsoftware"
)

for sm in "${SUBMODULES[@]}"; do
  if ! grep -q "path = ${sm}" .gitmodules 2>/dev/null; then
    log "Skipping: no submodule with path '${sm}' in this repo."
    continue
  fi

  log "Updating submodule at path: ${sm} ..."

  if [[ "$sm" == "qmcsoftware" ]]; then
    git submodule update --init "$sm"
    (
      cd "$sm"
      git fetch origin develop
      git checkout develop
      git pull --ff-only origin develop
    )
  else
    git submodule update --init --remote "$sm"
  fi
done

# If nothing changed, we are done
if [[ -z "$(git status --porcelain)" ]]; then
  log "All submodules already up to date."
  exit 0
fi

git status --short

if [[ "$AUTO_COMMIT" -eq 1 ]]; then
  log "Committing updated submodule pointers..."
  git add classlib qmcsoftware
  git commit -m "Update submodules (classlib + qmcsoftware)"

  if [[ "$AUTO_PUSH" -eq 1 ]]; then
    log "Pushing commit..."
    git push
  else
    log "Commit created; remember to push if needed."
  fi
else
  log "Review changes above; commit manually if desired."
fi

log "Done."
