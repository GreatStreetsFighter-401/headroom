#!/usr/bin/env sh
# Run the automated tests (the challenge's "Test" command). CI runs this script.
# Exits non-zero when a test fails or the code is not lint-clean.
set -eu

uv run pytest -q
uv run ruff check .
uv run ruff format --check .
