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
#   3. This updates:
#        • HickernellClassLib
#        • QMCSoftware (develop branch)
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
  local ts=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$ts] $*"
}

# Must run from repo root
if [[ ! -d ".git" ]]; then
  echo "Error: run this script from the root of the repository."
  exit 1
fi

# Safety: require clean working tree
if [[ -n "$(git status --porcelain)" ]]; then
  log "Uncommitted changes present — please commit or stash first."
  git status --short
  exit 1
fi

SUBMODULES=(
  "HickernellClassLib"
  "QMCSoftware"
)

for sm in "${SUBMODULES[@]}"; do
  if ! grep -q "$sm" .gitmodules 2>/dev/null; then
    log "Skipping: no submodule named $sm in this repo."
    continue
  fi

  log "Updating submodule: $sm ..."
  git submodule update --init --remote "$sm"
done

if [[ -z "$(git status --porcelain)" ]]; then
  log "All submodules already up to date."
  exit 0
fi

git status --short

if [[ "$AUTO_COMMIT" -eq 1 ]]; then
  log "Committing updated submodule pointers..."
  git commit -am "Update submodules (HCL + QMCSoftware)"

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
