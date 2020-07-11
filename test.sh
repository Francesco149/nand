#!/bin/sh

out=$(mktemp)
for f in ./*.py; do
  echo "$f"
  "$f" > "$out" || exit
  cmp="$(echo "$f" | sed s/\.py$/.cmp/g)"
  if ! diff "$cmp" "$out"; then
    echo "$f did not match, check $cmp for the full output"
    exit 1
  fi
done
rm "$out"

