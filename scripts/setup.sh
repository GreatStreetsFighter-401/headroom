#!/usr/bin/env sh
# Install dependencies and prepare the environment (the challenge's "Setup" command).
# Needs: Python 3.11+ and uv (https://docs.astral.sh/uv/). With pip instead:
#   python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
set -eu

uv sync --extra dev --frozen
echo "Setup complete. Next: scripts/run.sh (full pipeline + page) or scripts/test.sh."
