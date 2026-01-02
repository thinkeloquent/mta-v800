#!/usr/bin/env bash
set -euo pipefail

# Pattern to delete (exact line match)
PATTERN='readme = "README.md"'

# Find all pyproject.toml files, excluding __STAGE__ and __SPECS__ directories
find . -name "pyproject.toml" \
  -not -path "./__STAGE__/*" \
  -not -path "./__SPECS__/*" \
  -not -path "./node_modules/*" \
  -not -path "./.venv/*" \
  -not -path "*/.venv/*" \
  -print0 | while IFS= read -r -d '' file; do
  echo "Processing $file"

  # macOS vs Linux sed handling
  if sed --version >/dev/null 2>&1; then
    # GNU sed (Linux)
    sed -i.bak "/^$PATTERN$/d" "$file"
  else
    # BSD sed (macOS)
    sed -i '' "/^$PATTERN$/d" "$file"
  fi
done
