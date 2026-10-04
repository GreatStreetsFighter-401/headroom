"""``headroom`` — the command line.

    headroom acquire [--refresh] [--no-transit]
    headroom build   [--tier A|B|C] [--params PATH]
    headroom run     [--tier A|B|C] [--draws N] [--seed S]
    headroom calibrate [--tier A|B|C]
    headroom explain  <parameter id | scenario id | all>
    headroom report  [--tier A|B|C]
    headroom all     [--tier ...]       acquire → build → run → report

Every command writes under ``out/`` and reads only the cache and the ledger,
so a second machine with the same cache produces byte-identical results.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from headroom import DATA_DIR, OUT_DIR
from headroom.ledger import load as load_ledger


def _towns_path(tier: str) -> Path:
    return OUT_DIR / "build" / f"towns_tier{tier.upper()}.json"


def cmd_acquire(args) -> int:
    from headroom.build import pipeline

    inputs = pipeline.acquire_all(refresh=args.refresh, with_transit=not args.no_transit)
    print("zoning     ", inputs["paths"]["zoning"])
    print("sewer      ", inputs["paths"]["sewer"])
    print("points     ", inputs["paths"]["points"])
    print("bps rows   ", len(inputs["bps"]))
    print("eoh report ", "ok" if inputs["eoh"] else f"unavailable ({inputs['eoh_error']})")
    print("acs api    ", "ok" if inputs["acs"] else "no CENSUS_API_KEY; using State report tables")
    print("gtfs       ", f"{len(inputs['gtfs']['stops'])} stops" if inputs["gtfs"] else "skipped")
    return 0


def cmd_build(args) -> int:
    from headroom.build import pipeline

    ledger = load_ledger()
    inputs = pipeline.acquire_all(refresh=False, with_transit=not args.no_transit)
    tiers = ["A", "B", "C"] if args.tier == "all" else [args.tier.upper()]
    params_path = Path(args.params) if args.params else (DATA_DIR / "district_params_ri.csv")
    if "A" in tiers and not params_path.exists():
        print(
            f"tier A: no ordinance-derived table at {params_path}; tier A will equal tier B "
            "until `scripts/export_district_params.py` (MuniAnchor) produces it",
            file=sys.stderr,
        )
    for tier in tiers:
        out = pipeline.build_towns(
            inputs,
            tier=tier,
            params_path=params_path,
            frequent_per_hour=ledger.parameters["tod_frequent_peak_departures_per_hour"].default,
            hub_min_routes=int(ledger.parameters["tod_hub_min_routes"].default),
        )
        print(f"tier {tier}: {_towns_path(tier)}")
        if out.get("districts_summary"):
            print("  districts:", json.dumps(out["districts_summary"]))
        if out.get("derived_shares"):
            print("  derived:  ", json.dumps(out["derived_shares"]))
        if out.get("transit"):
            tr = dict(out["transit"])
            tr.pop("hub_stops", None)
            print("  transit:  ", json.dumps(tr))
        print(
            "  stock from:",
            out["stock_source"],
            "| EOH:",
            "ok" if out["eoh_available"] else out["eoh_error"],
        )
    return 0


def cmd_run(args) -> int:
    from headroom.model.core import Model

    ledger = load_ledger()
    tiers = ["A", "B", "C"] if args.tier == "all" else [args.tier.upper()]
    for tier in tiers:
        p = _towns_path(tier)
        if not p.exists():
            print(f"no build for tier {tier}; run `headroom build --tier {tier}`", file=sys.stderr)
            return 2
        towns = json.loads(p.read_text())
        model = Model(ledger, towns, draws=args.draws, seed=args.seed)
        res = model.run()
        out = OUT_DIR / f"results_tier{tier}.json"
        out.write_text(json.dumps(res, indent=1))
        sw = res["statewide"]
        print(f"tier {tier} → {out}")
        print(
            f"  baseline 5-yr permits  P10/P50/P90: "
            f"{sw['baseline']['five_year']['p10']:.0f} / {sw['baseline']['five_year']['p50']:.0f} / "
            f"{sw['baseline']['five_year']['p90']:.0f}"
        )
        for s in ("adu", "missing_middle", "parking", "fees_handbook", "fees_ri", "tod"):
            f = sw[s]["five_year"]
            print(f"  {s:16s} +{f['p10']:.0f} / +{f['p50']:.0f} / +{f['p90']:.0f}")
    return 0


def cmd_calibrate(args) -> int:
    from headroom.model.core import calibrate_adu

    ledger = load_ledger()
    towns = json.loads(_towns_path(args.tier).read_text())
    print(json.dumps(calibrate_adu(ledger, towns), indent=2))
    return 0


def cmd_hindcast(args) -> int:
    from headroom.model.hindcast import hindcast

    ledger = load_ledger()
    towns = json.loads(_towns_path(args.tier).read_text())
    res = hindcast(ledger, towns, fit_through=args.fit_through)
    out = OUT_DIR / "hindcast.json"
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=2))
    print("→", out)
    return 0


def cmd_explain(args) -> int:
    ledger = load_ledger()
    what = args.what
    if what == "all":
        for s in ledger.scenarios.values():
            print(f"## {s.label}\n\n{s.handbook_definition.strip()}\n\nModelled as: {s.modelled_as.strip()}\n")
        for pid in ledger.parameters:
            print(ledger.explain(pid), "\n")
        return 0
    if what in ledger.scenarios:
        s = ledger.scenarios[what]
        print(f"# {s.label}\n")
        print("Handbook:", s.handbook_definition.strip(), "\n")
        print("Modelled as:", s.modelled_as.strip(), "\n")
        if s.ri_law_today:
            print("Rhode Island law today:", s.ri_law_today.strip(), "\n")
        if s.what_it_cannot_say:
            print("What it cannot say:", s.what_it_cannot_say.strip(), "\n")
        print("Parameters:")
        for p in ledger.for_scenario(what):
            print(f"  - {p.id}: {p.default} {p.unit} [{p.status}]")
        return 0
    if what in ledger.parameters:
        print(ledger.explain(what))
        return 0
    print(f"unknown id {what!r}", file=sys.stderr)
    return 2


def cmd_report(args) -> int:
    from headroom import report

    paths = report.write_all(tier=args.tier.upper())
    for p in paths:
        print(p)
    return 0


def cmd_site(args) -> int:
    """Publish results, inputs and the ledger as JSON for the static page."""
    import shutil
    from dataclasses import asdict

    from headroom import ROOT

    ledger = load_ledger()
    dest = ROOT / "site" / "data"
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for t in ("A", "B", "C"):
        for src in (OUT_DIR / f"results_tier{t}.json", OUT_DIR / "build" / f"towns_tier{t}.json"):
            if src.exists():
                shutil.copy(src, dest / src.name)
                copied.append(src.name)
    (dest / "ledger.json").write_text(
        json.dumps(
            {
                "meta": ledger.meta,
                "scenarios": {k: asdict(v) for k, v in ledger.scenarios.items()},
                "parameters": {k: asdict(v) for k, v in ledger.parameters.items()},
            },
            indent=1,
        )
    )
    from headroom.acquire.base import manifest_path

    if manifest_path().exists():
        shutil.copy(manifest_path(), dest / "manifest.json")
        copied.append("manifest.json")
    print("site/data:", ", ".join(copied + ["ledger.json"]))
    return 0


def cmd_check(args) -> int:
    """Compare this run's statewide results with the committed reference."""
    ref_dir = OUT_DIR / "reference"
    if args.update:
        ref_dir.mkdir(parents=True, exist_ok=True)
        for t in ("A", "B", "C"):
            p = OUT_DIR / f"results_tier{t}.json"
            if p.exists():
                res = json.loads(p.read_text())
                (ref_dir / f"statewide_tier{t}.json").write_text(
                    json.dumps({"meta": res["meta"], "statewide": res["statewide"]}, indent=1)
                )
                print("reference updated:", ref_dir / f"statewide_tier{t}.json")
        return 0
    bad = 0
    for t in ("A", "B", "C"):
        p = OUT_DIR / f"results_tier{t}.json"
        r = ref_dir / f"statewide_tier{t}.json"
        if not (p.exists() and r.exists()):
            continue
        cur = json.loads(p.read_text())["statewide"]
        ref = json.loads(r.read_text())["statewide"]
        for s, block in ref.items():
            for q in ("p10", "p50", "p90"):
                a, b = cur[s]["five_year"][q], block["five_year"][q]
                tol = max(1.0, abs(b) * args.tolerance)
                if abs(a - b) > tol:
                    bad += 1
                    print(f"tier {t} {s} {q}: {a} vs reference {b}")
    if bad:
        print(
            f"{bad} statewide values drifted beyond tolerance; a source was republished "
            "(see cache/manifest.json) or the model changed its answer",
            file=sys.stderr,
        )
        return 1
    print("results match the committed reference")
    return 0


def cmd_all(args) -> int:
    for fn in (cmd_acquire, cmd_build, cmd_run, cmd_report):
        rc = fn(args)
        if rc:
            return rc
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="headroom", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("acquire", help="retrieve every input from its authoritative source")
    a.add_argument("--refresh", action="store_true")
    a.add_argument("--no-transit", action="store_true")
    a.set_defaults(fn=cmd_acquire)

    b = sub.add_parser("build", help="Stage 1: capacity + municipal input table")
    b.add_argument("--tier", default="B", help="A, B, C or all")
    b.add_argument("--params", default=None, help="district_params CSV (tier A)")
    b.add_argument("--no-transit", action="store_true")
    b.set_defaults(fn=cmd_build)

    r = sub.add_parser("run", help="Stage 2: Monte Carlo over the ledger")
    r.add_argument("--tier", default="B")
    r.add_argument("--draws", type=int, default=None)
    r.add_argument("--seed", type=int, default=None)
    r.set_defaults(fn=cmd_run)

    c = sub.add_parser("calibrate", help="implied vs observed 2024 ADU permits")
    c.add_argument("--tier", default="B")
    c.set_defaults(fn=cmd_calibrate)

    hc = sub.add_parser("hindcast", help="fit the baseline through a year and score the next ones")
    hc.add_argument("--tier", default="B")
    hc.add_argument("--fit-through", type=int, default=2023)
    hc.set_defaults(fn=cmd_hindcast)

    e = sub.add_parser("explain", help="print a ledger entry")
    e.add_argument("what")
    e.set_defaults(fn=cmd_explain)

    rp = sub.add_parser("report", help="generate the overview chapters from the ledger + results")
    rp.add_argument("--tier", default="B")
    rp.set_defaults(fn=cmd_report)

    st = sub.add_parser("site", help="copy results + ledger into site/data for the static page")
    st.set_defaults(fn=cmd_site)

    ck = sub.add_parser("check", help="compare results with out/reference (reproducibility)")
    ck.add_argument("--update", action="store_true", help="rewrite the reference from this run")
    ck.add_argument("--tolerance", type=float, default=0.0, help="relative tolerance (0 = exact)")
    ck.set_defaults(fn=cmd_check)

    al = sub.add_parser("all", help="acquire → build → run → report")
    al.add_argument("--tier", default="all")
    al.add_argument("--params", default=None)
    al.add_argument("--draws", type=int, default=None)
    al.add_argument("--seed", type=int, default=None)
    al.add_argument("--refresh", action="store_true")
    al.add_argument("--no-transit", action="store_true")
    al.set_defaults(fn=cmd_all)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
