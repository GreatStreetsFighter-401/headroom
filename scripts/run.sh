#!/usr/bin/env sh
# Run the tool end to end (the challenge's "Run" command):
#   acquire every input from its authoritative source (cached after the first run),
#   build Stage 1 capacity at every data tier, run the Stage 2 Monte Carlo,
#   generate the report chapters, publish the results into site/, and serve the page.
#
# Optional environment (see .env.example): CENSUS_API_KEY, HEADROOM_EOH_PDF.
# The first acquisition downloads about 100 MB and takes three to four minutes.
set -eu

uv run headroom acquire
uv run headroom build --tier all
uv run headroom run --tier all
uv run headroom calibrate
uv run headroom report
uv run headroom site

PORT="${PORT:-8765}"
echo
echo "Results are in out/ and docs/generated/. Serving the page at http://localhost:${PORT}/ (Ctrl-C to stop)."
exec uv run python -m http.server "${PORT}" --directory site
