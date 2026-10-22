# Submission Checklist

Advisory, from the challenge's starter template; the [Official Rules](https://housingchallenge.turnout.rocks/rules.html) govern. Status as of 2026-10-20 (evening).

## Eligibility gates

- [x] Reproducible setup from documented commands — `scripts/setup.sh`, `scripts/run.sh`, `scripts/test.sh`; dependencies pinned in `uv.lock`
- [x] Automated tests covering core logic, with a documented run command — 55 tests, `scripts/test.sh`
- [x] No committed secrets; secret scanning enabled, zero unresolved alerts — secret scanning and push protection are enabled on the public repository (read back through the API, 2026-10-20)
- [x] Dependabot alerts and CodeQL enabled; no unaddressed critical/high findings — CodeQL **default setup** is configured (so the template's advanced `codeql.yml` workflow is removed, as its own comment instructs); Dependabot alerts enabled by the owner; `dependabot.yml` schedules uv and Actions updates
- [x] Approved OSI-compliant license — Apache-2.0 (`LICENSE`, `NOTICE`)

See docs/REPO_SETUP_GUIDE.md in the starter template for the settings.

## Deliverables

- [x] Interactive tool (functional) — live at https://greatstreetsfighter-401.github.io/headroom/ (GitHub Pages, published from `site/` on every push to `main`); the page re-runs the model in the browser (Pyodide: the same Python as the CLI, on the same town table) when any assumption is pinned; 500 draws in about a second, 2,000 on request; the CLI runs everything else
- [ ] Slide deck (≤ 30 slides, PDF)
- [ ] Demo video (5 minutes, viewable without an account)
- [x] Model & Assumptions Overview (≤ 25 pages) — `docs/MODEL_AND_ASSUMPTIONS.md` (draft v0.2)
- [x] Source code (public GitHub repo) — https://github.com/GreatStreetsFighter-401/headroom; CI, CodeQL and the weekly reproduction run are green
- [ ] Software Bill of Materials (SBOM) — exported from the public repository's dependency graph at submission; `reproduce.yml` also builds a CycloneDX one
- [x] Policy scenario comparison (≤ 4 pages) — `docs/POLICY_SCENARIO_COMPARISON.md` (draft v0.2)

## Scope and disclosures

- [x] Baseline + at least three benchmark scenarios modeled at the state level — baseline + all five, plus the five together
- [x] Data provenance documented — `docs/DATA_PROVENANCE.md`
- [x] AI tools, models, APIs, and dependencies disclosed — `docs/DISCLOSURES.md`

## Still open (not gates)

- [ ] Private vulnerability reporting (Settings → Code security) — not a scored gate, but `SECURITY.md` promises it

- [ ] Publish the MuniAnchor district table at a stable URL so tier A can be acquired by script
- [ ] Replace the three placeholders (missing-middle feasibility share, mandated-parking baseline, Rhode Island fee level) with collected data
- [ ] Per-town ADU calibration from the State's annual ADU report
- [ ] Usability sessions with planners; external methods review
