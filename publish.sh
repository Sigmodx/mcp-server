#!/usr/bin/env bash
# Publish sigmodx-mcp to PyPI.
set -euo pipefail
cd "$(dirname "$0")"

for env_file in .env ../../Sigmodx/sdk/python/.env; do
  if [[ -f "$env_file" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
    break
  fi
done

if [[ -z "${TWINE_PASSWORD:-}" ]]; then
  echo "Set TWINE_PASSWORD in .env or Sigmodx/sdk/python/.env"
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q build twine
.venv/bin/python -m build
TWINE_USERNAME=__token__ TWINE_PASSWORD="$TWINE_PASSWORD" \
  .venv/bin/twine upload --non-interactive dist/sigmodx_mcp-0.1.0*

echo "Done. Verify: pip index versions sigmodx-mcp"
