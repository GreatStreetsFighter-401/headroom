"""Generate the overview chapters from the ledger and the results.

The Model and Assumptions Overview the challenge asks for has to document
every dataset's provenance, every assumption with its justification, the
sensitivity of the results and what the tool cannot say. Those four things
already exist as data — the manifest, the ledger, the sensitivity table and
the ledger's ``what_it_cannot_say`` fields — so the chapters are written
from them. The prose that frames them is in ``docs/`` by hand; the tables
are never typed twice.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from headroom import OUT_DIR, ROOT
from headroom.acquire.base import sources_table
from headroom.ledger import load as load_ledger

DOCS = ROOT / "docs" / "generated"
SCEN_ORDER = ("adu", "missing_middle", "parking", "fees_handbook", "fees_ri", "tod", "combined")
SCEN_LABEL = {
    "adu": "Accessory dwelling units",
    "missing_middle": "Missing middle (2–6 units on single-family lots)",
    "parking": "Parking requirement reduction",
    "fees_handbook": "Fee reduction (handbook $50,000 baseline)",
    "fees_ri": "Fee reduction (Rhode Island actual fees)",
    "tod": "Transit-oriented density",
    "combined": "All five together (fees at RI level; upper bound, capped)",
}


def _fmt(v: float) -> str:
    return f"{v:,.0f}"


def chapter_assumptions(ledger) -> str:
    lines = [
        "# Assumptions",
        "",
        "Generated from `assumptions.yaml`. Status: **statutory** fixed by law or by the "
        "challenge handbook; **verified** read from a primary Rhode Island source; **prior** "
        "evidence from elsewhere adapted to Rhode Island; **placeholder** not yet collected, "
        "and said so; **design** a modelling choice.",
        "",
    ]
    for sid, s in ledger.scenarios.items():
        lines += [
            f"## {s.label}",
            "",
            f"**Handbook definition.** {s.handbook_definition.strip()}",
            "",
            f"**Modelled as.** {s.modelled_as.strip()}",
            "",
        ]
        if s.ri_law_today:
            lines += [f"**Rhode Island law today.** {s.ri_law_today.strip()}", ""]
        if s.what_it_cannot_say:
            lines += [f"**What it cannot tell policymakers.** {s.what_it_cannot_say.strip()}", ""]
        params = (
            [p for p in ledger.for_scenario(sid) if "all" not in p.scenarios]
            if sid != "baseline"
            else [p for p in ledger.parameters.values() if "all" in p.scenarios]
        )
        if params:
            lines += ["| Parameter | Default | Range | Status | Source |", "|---|---|---|---|---|"]
            for p in params:
                rng = "fixed" if p.distribution == "fixed" else f"{p.low} – {p.high} ({p.distribution})"
                lines.append(
                    f"| `{p.id}` — {p.label} | {p.default} {p.unit} | {rng} | {p.status} | {p.source.strip()} |"
                )
            lines.append("")
            for p in params:
                lines += [f"### `{p.id}`", "", f"**Why this value.** {p.justification.strip()}"]
                if p.ri_calibration:
                    lines += ["", f"**Rhode Island calibration.** {p.ri_calibration.strip()}"]
                if p.what_it_cannot_say:
                    lines += ["", f"**What it cannot say.** {p.what_it_cannot_say.strip()}"]
                lines.append("")
    return "\n".join(lines)


def chapter_data(towns: dict) -> str:
    sources, entries = sources_table()
    lines = [
        "# Data",
        "",
        "Every dataset is retrieved by `headroom acquire` from the source below; "
        "the manifest records what was fetched, when, and its SHA-256.",
        "",
        "| Source | Publisher | Licence | Notes |",
        "|---|---|---|---|",
    ]
    for s in sources:
        lines.append(f"| [{s['title']}]({s['url']}) | {s['publisher']} | {s['license']} | {s['notes']} |")
    lines += [
        "",
        "## Files retrieved",
        "",
        "| File | Source | Retrieved | Bytes | SHA-256 |",
        "|---|---|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| `{e['name']}` | {e['source']} | {e['retrieved_at']} | {e['bytes']:,} | `{e['sha256'][:16]}…` |"
        )
    ds = towns.get("districts_summary") or {}
    if ds:
        lines += [
            "",
            "## Stage 1 join (this build)",
            "",
            f"- Zoning polygons: {ds['n_polygons']:,}; structure points loaded: {ds['n_points_loaded']:,}; "
            f"unmatched points: {sum(ds['n_points_unmatched_by_type'].values()):,}.",
            f"- Allowed-use reading of residential districts from the State layer's text: "
            f"{ds['allowed_reading_counts']}.",
            f"- Rows carrying an ordinance reading (tier A): {ds['tier_A_rows']:,}.",
        ]
    d = towns.get("derived_shares") or {}
    if d:
        lines += ["", "## Derived statewide shares", ""] + [f"- `{k}`: {v}" for k, v in d.items()]
    if towns.get("eoh_checks"):
        lines += [
            "",
            "## State report tables: sum of municipalities vs printed statewide total",
            "",
            "| Table | Sum | Printed | Agrees |",
            "|---|---|---|---|",
        ]
        for k, v in towns["eoh_checks"].items():
            lines.append(f"| {k} | {v['sum_of_municipalities']:,} | {v['printed_statewide']} | {v['agrees']} |")
    lines += [
        "",
        f"Stock source: {towns.get('stock_source')}. EOH report: "
        f"{'available' if towns.get('eoh_available') else 'unavailable — ' + str(towns.get('eoh_error'))}.",
    ]
    return "\n".join(lines)


def chapter_results(res: dict, tier: str) -> str:
    sw = res["statewide"]
    yrs = res["meta"]["years"]
    lines = [
        f"# Results — tier {tier}",
        "",
        f"Metric: {res['meta']['metric']}. {res['meta']['draws']:,} draws, seed {res['meta']['seed']}. "
        f"Horizon {yrs[0]}–{yrs[-1]}. Values are permitted units over the five years, as P10 / P50 / P90.",
        "",
        "| Scenario | 5-year increment over baseline (P10 / P50 / P90) | Mean |",
        "|---|---|---|",
    ]
    b = sw["baseline"]["five_year"]
    lines.append(
        f"| Baseline (level, not increment) | {_fmt(b['p10'])} / {_fmt(b['p50'])} / {_fmt(b['p90'])} "
        f"| {_fmt(sw['baseline']['five_year_mean'])} |"
    )
    for s in SCEN_ORDER:
        f = sw[s]["five_year"]
        lines.append(
            f"| {SCEN_LABEL[s]} | +{_fmt(f['p10'])} / +{_fmt(f['p50'])} / +{_fmt(f['p90'])} "
            f"| +{_fmt(sw[s]['five_year_mean'])} |"
        )
    lines += [
        "",
        "## By year (P50, statewide)",
        "",
        "| Scenario | " + " | ".join(str(y) for y in yrs) + " |",
        "|---|" + "---|" * len(yrs),
    ]
    lines.append("| Baseline | " + " | ".join(_fmt(v) for v in sw["baseline"]["p50"]) + " |")
    for s in SCEN_ORDER:
        lines.append(f"| {SCEN_LABEL[s]} | " + " | ".join("+" + _fmt(v) for v in sw[s]["p50"]) + " |")
    lines += [
        "",
        "## Sensitivity",
        "",
        "Spearman rank correlation between each sampled parameter and the scenario's five-year "
        "statewide increment across draws, with the median increment in the parameter's bottom and "
        "top quintiles.",
        "",
    ]
    for s in SCEN_ORDER:
        rows = res["sensitivity"].get(s) or []
        if not rows:
            continue
        lines += [
            f"### {SCEN_LABEL[s]}",
            "",
            "| Parameter | ρ | P50 at low quintile | P50 at high quintile | Status |",
            "|---|---|---|---|---|",
        ]
        for r in rows:
            lines.append(
                f"| `{r['parameter']}` | {r['spearman']:+.2f} | +{_fmt(r['p50_at_low_quintile'])} "
                f"| +{_fmt(r['p50_at_high_quintile'])} | {r['status']} |"
            )
        lines.append("")
    lines += [
        "## By municipality (5-year P50 increment)",
        "",
        "| Municipality | Baseline | " + " | ".join(SCEN_LABEL[s] for s in SCEN_ORDER) + " |",
        "|---|---|" + "---|" * len(SCEN_ORDER),
    ]
    for name, t in res["towns"].items():
        cells = [_fmt(t["baseline"]["five_year"]["p50"])] + ["+" + _fmt(t[s]["five_year"]["p50"]) for s in SCEN_ORDER]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def chapter_tiers(results: dict[str, dict]) -> str:
    lines = [
        "# Data tiers — what richer data buys",
        "",
        "The same model run on three input sets. Tier A adds ordinance-derived allowed uses "
        "(MuniAnchor); tier B is the State zoning layer alone; tier C is Census structure counts "
        "with ledger shares, which any state can run from federal data.",
        "",
        "| Scenario | " + " | ".join(f"Tier {t} (P10 / P50 / P90)" for t in results) + " |",
        "|---|" + "---|" * len(results),
    ]
    for s in ("baseline",) + SCEN_ORDER:
        cells = []
        for _t, res in results.items():
            f = res["statewide"][s]["five_year"]
            sign = "" if s == "baseline" else "+"
            cells.append(f"{sign}{_fmt(f['p10'])} / {sign}{_fmt(f['p50'])} / {sign}{_fmt(f['p90'])}")
        lines.append(f"| {SCEN_LABEL.get(s, 'Baseline')} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_all(*, tier: str = "B") -> list[Path]:
    ledger = load_ledger()
    DOCS.mkdir(parents=True, exist_ok=True)
    out: list[Path] = []
    stamp = f"\n\n---\n_Generated {datetime.now(UTC).isoformat(timespec='minutes')} by `headroom report`._\n"
    (DOCS / "assumptions.md").write_text(chapter_assumptions(ledger) + stamp)
    out.append(DOCS / "assumptions.md")
    tp = OUT_DIR / "build" / f"towns_tier{tier}.json"
    if tp.exists():
        towns = json.loads(tp.read_text())
        (DOCS / "data.md").write_text(chapter_data(towns) + stamp)
        out.append(DOCS / "data.md")
    rp = OUT_DIR / f"results_tier{tier}.json"
    if rp.exists():
        res = json.loads(rp.read_text())
        (DOCS / f"results_tier{tier}.md").write_text(chapter_results(res, tier) + stamp)
        out.append(DOCS / f"results_tier{tier}.md")
    results = {}
    for t in ("A", "B", "C"):
        p = OUT_DIR / f"results_tier{t}.json"
        if p.exists():
            results[t] = json.loads(p.read_text())
    if len(results) >= 2:
        (DOCS / "tiers.md").write_text(chapter_tiers(results) + stamp)
        out.append(DOCS / "tiers.md")
    return out
