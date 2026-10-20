# Submission Checklist

Advisory, from the challenge's starter template; the [Official Rules](https://housingchallenge.turnout.rocks/rules.html) govern. Status as of 2026-10-20.

## Eligibility gates

- [x] Reproducible setup from documented commands — `scripts/setup.sh`, `scripts/run.sh`, `scripts/test.sh`; dependencies pinned in `uv.lock`
- [x] Automated tests covering core logic, with a documented run command — 55 tests, `scripts/test.sh`
- [ ] No committed secrets; secret scanning enabled, zero unresolved alerts — no secrets are committed; **scanning and push protection are repository settings, to switch on when the public repository is created**
- [ ] Dependabot alerts and CodeQL enabled; no unaddressed critical/high findings — `dependabot.yml` and `codeql.yml` are in place; **the settings are switched on in the repository**
- [x] Approved OSI-compliant license — Apache-2.0 (`LICENSE`, `NOTICE`)

See docs/REPO_SETUP_GUIDE.md in the starter template for the settings.

## Deliverables

- [x] Interactive tool (functional) — the CLI and the page in `site/`; in-browser re-runs of the model are the next improvement
- [ ] Slide deck (≤ 30 slides, PDF)
- [ ] Demo video (5 minutes, viewable without an account)
- [x] Model & Assumptions Overview (≤ 25 pages) — `docs/MODEL_AND_ASSUMPTIONS.md` (draft v0.2)
- [ ] Source code (public GitHub repo) — to be split from the development monorepo
- [ ] Software Bill of Materials (SBOM) — exported from the public repository's dependency graph at submission; `reproduce.yml` also builds a CycloneDX one
- [x] Policy scenario comparison (≤ 4 pages) — `docs/POLICY_SCENARIO_COMPARISON.md` (draft v0.2)

## Scope and disclosures

- [x] Baseline + at least three benchmark scenarios modeled at the state level — baseline + all five, plus the five together
- [x] Data provenance documented — `docs/DATA_PROVENANCE.md`
- [x] AI tools, models, APIs, and dependencies disclosed — `docs/DISCLOSURES.md`

## Still open (not gates)

- [ ] Publish the MuniAnchor district table at a stable URL so tier A can be acquired by script
- [ ] Replace the three placeholders (missing-middle feasibility share, mandated-parking baseline, Rhode Island fee level) with collected data
- [ ] Per-town ADU calibration from the State's annual ADU report
- [ ] Usability sessions with planners; external methods review
