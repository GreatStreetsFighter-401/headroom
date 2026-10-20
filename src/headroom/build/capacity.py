"""Stage 1 — regulatory capacity, computed from public data with no judgment.

Inputs (all retrieved by ``headroom acquire``):
  * RIGIS zoning polygons (district code, generalized class, MIN_LOT_SF)
  * RIGIS E-911 address points (typed structures)
  * RIGIS sewered areas
  * optionally, MuniAnchor's ordinance-derived district parameters (tier A)
  * optionally, RIPTA stop frequencies (transit-oriented scenario)

Output: one row per (municipality, zone code) with counts of existing
structures by type, the sewered share, residential land area, the
allowed-use reading and its provenance, and transit-buffer membership —
written to ``out/build/districts.json``. Everything downstream reads this
file; nothing downstream touches geometry.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from shapely.geometry import Point, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

from headroom import DATA_DIR, OUT_DIR
from headroom.acquire import arcgis
from headroom.build import zone_text
from headroom.municipalities import canonical

SQFT_PER_ACRE = 43560.0
RES_CLASSES = {"RES"}
STRUCTURE_TYPES = ("R1", "R2", "R3", "R4", "R5", "R6", "A1", "DV")


def _load_polys(path: Path, keep=None):
    feats = arcgis.load_features(path)
    out = []
    for f in feats:
        g = f.get("geometry")
        if not g:
            continue
        props = f.get("properties", {})
        if keep and not keep(props):
            continue
        geom = shape(g)
        if not geom.is_valid:
            geom = geom.buffer(0)
        out.append((geom, props))
    return out


def _load_points(path: Path):
    feats = arcgis.load_features(path)
    pts = []
    for f in feats:
        g = f.get("geometry")
        if not g or g.get("type") != "Point":
            continue
        x, y = g["coordinates"][:2]
        p = f.get("properties", {})
        pts.append((x, y, p.get("pointtype"), p.get("municipality"), p.get("status")))
    return pts


def load_district_params(path: Path | None = None) -> dict[tuple[str, str], dict]:
    """Tier A: MuniAnchor's ordinance-derived table keyed by (town, zone code).

    Schema (see schema/district_params.md): municipality, zone_code,
    allowed_1f, allowed_2f, allowed_3f (by_right | special | no | ''),
    min_lot_sf, max_height_ft, max_stories, max_lot_coverage, max_far,
    parking_per_unit_sf, parking_per_unit_mf, source_section, source_url.
    """
    path = path or (DATA_DIR / "district_params_ri.csv")
    if not path.exists():
        return {}
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            muni = canonical(row["municipality"])
            if muni is None:
                continue
            out[(muni, row["zone_code"].strip().upper())] = row
    return out


def _allowed_from_params(row: dict) -> str | None:
    a2 = (row.get("allowed_2f") or "").strip().lower()
    a3 = (row.get("allowed_3f") or "").strip().lower()
    if a2 == "by_right" or a3 == "by_right":
        return zone_text.ALLOWS_2PLUS
    if a2 in ("no", "special") and a3 in ("no", "special", ""):
        return zone_text.SF_ONLY
    return None


def build_districts(
    *,
    zoning_path: Path,
    points_path: Path,
    sewer_path: Path,
    params_path: Path | None = None,
    transit_buffers=None,
    out_path: Path | None = None,
) -> dict:
    """Join structures to districts and write the district table."""
    polys = _load_polys(zoning_path)
    sewer = _load_polys(sewer_path)
    sewer_union = unary_union([g for g, _ in sewer]) if sewer else None
    params = load_district_params(params_path)

    geoms = [g for g, _ in polys]
    tree = STRtree(geoms)
    counts: dict[int, dict] = defaultdict(lambda: defaultdict(int))
    unmatched = defaultdict(int)

    pts = _load_points(points_path)
    for x, y, ptype, _muni, status in pts:
        if status not in (None, "", "Current"):
            continue
        p = Point(x, y)
        hits = tree.query(p, predicate="within")
        if len(hits) == 0:
            unmatched[ptype] += 1
            continue
        i = int(hits[0])  # overlapping district polygons are rare; take the first
        c = counts[i]
        c[ptype] += 1
        if sewer_union is not None and sewer_union.contains(p):
            c[f"{ptype}_sewered"] += 1
        if transit_buffers is not None:
            for name, geom in transit_buffers.items():
                if geom.contains(p):
                    c[f"{ptype}_{name}"] += 1

    rows = []
    for i, (geom, props) in enumerate(polys):
        muni = canonical(props.get("MUNI_NAME"))
        if muni is None:
            continue
        code = (props.get("ZONE_CODE") or "").strip().upper()
        czone = props.get("CZONE_CODE") or ""
        c = counts.get(i, {})
        reading = zone_text.classify(code, props.get("ZONE_DESC"))
        allowed, allowed_src, allowed_evidence = reading.allowed, "state_layer_text", reading.evidence
        prow = params.get((muni, code))
        if prow:
            a = _allowed_from_params(prow)
            if a:
                allowed, allowed_src = a, "munianchor_ordinance"
                allowed_evidence = f"{prow.get('source_section', '')} {prow.get('source_url', '')}".strip()
        area_ac = geom.area / SQFT_PER_ACRE
        row = {
            "municipality": muni,
            "zone_code": code,
            "zone_desc": props.get("ZONE_DESC") or "",
            "czone": czone,
            "density_class": props.get("DENSITY") or "",
            "min_lot_sf": props.get("MIN_LOT_SF"),
            "area_acres": round(area_ac, 3),
            "allowed": allowed,
            "allowed_source": allowed_src,
            "allowed_evidence": allowed_evidence,
            "tier": "A" if allowed_src == "munianchor_ordinance" else "B",
        }
        for t in STRUCTURE_TYPES:
            row[f"n_{t}"] = int(c.get(t, 0))
            row[f"n_{t}_sewered"] = int(c.get(f"{t}_sewered", 0))
        if transit_buffers is not None:
            for name in transit_buffers:
                row[f"n_R1_{name}"] = int(c.get(f"R1_{name}", 0))
                row[f"n_R2_{name}"] = int(c.get(f"R2_{name}", 0))
                inter = geom.intersection(transit_buffers[name])
                row[f"area_acres_{name}"] = round(inter.area / SQFT_PER_ACRE, 3)
        if prow:
            for k in ("max_height_ft", "max_stories", "max_lot_coverage", "max_far",
                      "parking_per_unit_sf", "parking_per_unit_mf"):
                v = (prow.get(k) or "").strip()
                row[k] = float(v) if v else None
        rows.append(row)

    summary = {
        "n_polygons": len(polys),
        "n_points_loaded": len(pts),
        "n_points_unmatched_by_type": dict(unmatched),
        "n_rows": len(rows),
        "tier_A_rows": sum(1 for r in rows if r["tier"] == "A"),
        "allowed_reading_counts": {
            k: sum(1 for r in rows if r["allowed"] == k)
            for k in (zone_text.SF_ONLY, zone_text.ALLOWS_2PLUS, zone_text.UNKNOWN)
        },
    }
    out = {"summary": summary, "districts": rows}
    out_path = out_path or (OUT_DIR / "build" / "districts.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1))
    return out


def town_totals(districts: list[dict]) -> dict[str, dict]:
    """Roll district rows up to municipalities for the model."""
    towns: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    for r in districts:
        t = towns[r["municipality"]]
        res = r["czone"] in RES_CLASSES
        for s in STRUCTURE_TYPES:
            t[f"n_{s}"] += r[f"n_{s}"]
            t[f"n_{s}_sewered"] += r[f"n_{s}_sewered"]
        if res:
            t["res_area_acres"] += r["area_acres"]
            t["n_R1_res"] += r["n_R1"]
            t["n_R1_res_sewered"] += r["n_R1_sewered"]
            if r["allowed"] == zone_text.SF_ONLY:
                t["n_R1_sf_only"] += r["n_R1"]
                t["n_R1_sf_only_sewered"] += r["n_R1_sewered"]
                t["sf_only_area_acres"] += r["area_acres"]
            elif r["allowed"] == zone_text.UNKNOWN:
                t["n_R1_unknown"] += r["n_R1"]
                t["n_R1_unknown_sewered"] += r["n_R1_sewered"]
            mls = r.get("min_lot_sf")
            if mls is not None and not (isinstance(mls, float) and math.isnan(mls)):
                if mls >= 20000:
                    t["n_R1_lot20k_plus"] += r["n_R1"]
                    t["n_R1_lot20k_plus_sewered"] += r["n_R1_sewered"]
                t["res_area_weighted_min_lot"] += r["area_acres"] * mls
                t["res_area_with_min_lot"] += r["area_acres"]
            for k in r:
                if k.startswith("n_R1_tod_") or k.startswith("n_R2_tod_") or k.startswith("area_acres_tod_"):
                    t[k] += r[k]
        t["tier_A_rows"] += 1 if r["tier"] == "A" else 0
        t["rows"] += 1
    for t in towns.values():
        if t["res_area_with_min_lot"]:
            t["mean_min_lot_sf"] = t["res_area_weighted_min_lot"] / t["res_area_with_min_lot"]
    return {k: dict(v) for k, v in towns.items()}
