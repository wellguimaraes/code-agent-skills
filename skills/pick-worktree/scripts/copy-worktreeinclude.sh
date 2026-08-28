#!/usr/bin/env bash
# Copy paths listed in <main>/.worktreeinclude into a new worktree.
# Skip missing sources and paths that already exist in the destination.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: copy-worktreeinclude.sh <main-worktree> <new-worktree>" >&2
  exit 2
fi

main="${1%/}"
new="${2%/}"
include="$main/.worktreeinclude"

if [[ ! -f "$include" ]]; then
  exit 0
fi

copied=0
skipped_missing=0
skipped_exists=0

while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  [[ -z "$line" || "$line" == \#* ]] && continue

  src="$main/$line"
  dest="$new/$line"

  if [[ ! -e "$src" ]]; then
    skipped_missing=$((skipped_missing + 1))
    continue
  fi
  if [[ -e "$dest" ]]; then
    skipped_exists=$((skipped_exists + 1))
    continue
  fi

  mkdir -p "$(dirname "$dest")"
  cp -R "$src" "$dest"
  copied=$((copied + 1))
  echo "copied $line"
done < "$include"

echo "worktreeinclude: copied=$copied skipped_missing=$skipped_missing skipped_exists=$skipped_exists"
