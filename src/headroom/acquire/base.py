"""Cached, manifest-recording downloads.

Challenge rule: a submission must not bundle its source datasets; it must
retrieve them from their authoritative sources by an automated process.
Every download goes through :func:`fetch`, which stores the bytes under
``cache/`` (git-ignored) and appends a manifest entry — URL, SHA-256, size,
retrieval time, content type and the source's licence — so the Model and
Assumptions Overview can list every dataset's provenance from one file
instead of from memory.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests

from headroom import CACHE_DIR

USER_AGENT = (
    "headroom/0.2 (+https://github.com/GreatStreetsFighter-401/headroom; Housing Data and Technology Innovation "
    "Challenge entry; polite automated acquisition)"
)


@dataclass(frozen=True)
class Source:
    """A dataset's identity and terms, independent of any one file."""

    id: str
    title: str
    publisher: str
    url: str
    license: str
    notes: str = ""


SOURCES: dict[str, Source] = {
    s.id: s
    for s in (
        Source(
            "rigis_zoning",
            "Rhode Island Zoning and Overlay Zones — Municipal Zoning Classifications (layer 1)",
            "Rhode Island Division of Statewide Planning (Land Use 2050 Data Services; "
            "HR&A Advisors + Go Consulting), distributed by RIGIS",
            "https://www.rigis.org/maps/c8d4094c9141466eb6d3e9d82c349dd8",
            "RIGIS licence: provided as-is; acknowledge RIGIS and the primary producer in "
            "derived products. Statewide Planning: publicly supported research, may be "
            "reprinted or used with credit.",
            "Zoning district polygons for all 39 municipalities compiled from municipal "
            "planning offices in 2025. Carries generalized class, a lot-size density class "
            "and MIN_LOT_SF; does NOT carry allowed unit types, height, parking or FAR.",
        ),
        Source(
            "rigis_overlays",
            "Rhode Island Zoning and Overlay Zones — Zoning Overlay Areas (layer 0)",
            "Rhode Island Division of Statewide Planning, distributed by RIGIS",
            "https://www.rigis.org/maps/c8d4094c9141466eb6d3e9d82c349dd8",
            "RIGIS licence (as above).",
            "Overlay districts with SOURCE_ORD (ordinance URL) and SOURCE_DATE.",
        ),
        Source(
            "rigis_e911_points",
            "E-911 Address Points (2026)",
            "Rhode Island E 9-1-1 Uniform Emergency Telephone System, distributed by RIGIS",
            "https://www.arcgis.com/home/item.html?id=26c8df834cbb4aa49ed571ad35c5647f",
            "RIGIS licence (as above).",
            "One point per addressed structure, typed (R1 single-family, R2 multi-family, "
            "A1 accessory building, DV development site, ...). Used as the statewide count "
            "of existing single-family structures; it is not a parcel layer.",
        ),
        Source(
            "rigis_sewered",
            "Sewered Areas",
            "RIGIS",
            "https://www.arcgis.com/home/item.html?id=d1f22828f48946be88e8c30c422ec61b",
            "RIGIS licence (as above).",
            "Service areas of wastewater treatment facilities; used to separate sewered from "
            "septic lots as a feasibility filter for a second unit.",
        ),
        Source(
            "census_bps",
            "Building Permits Survey — annual permits by permit-issuing place",
            "U.S. Census Bureau",
            "https://www2.census.gov/econ/bps/Place/Northeast%20Region/",
            "Public domain (U.S. federal government work).",
            "Units in new privately-owned residential buildings by size class. Months "
            "reported is carried; imputed values are used for non-reporting months as "
            "published. Rhode Island's Executive Office of Housing states its own municipal "
            "survey is more accurate for 2018 onward; both series are kept.",
        ),
        Source(
            "census_acs",
            "American Community Survey 5-year estimates (county subdivisions)",
            "U.S. Census Bureau",
            "https://api.census.gov/data/",
            "Public domain (U.S. federal government work). An API key is free and required.",
            "B25024 units in structure, B25002 occupancy, B25003 tenure.",
        ),
        Source(
            "census_acs_sf",
            "American Community Survey 5-year estimates — table-based summary files",
            "U.S. Census Bureau",
            "https://www2.census.gov/programs-surveys/acs/summary_file/",
            "Public domain (U.S. federal government work). No API key needed.",
            "One pipe-delimited file per table for every geography in the country (≈48 MB each); "
            "the acquisition streams the file and keeps only the state's county subdivisions. "
            "Geography names and codes from the Geos{year}5YR.txt index.",
        ),
        Source(
            "ri_transit_master_plan",
            "Transit Forward RI 2040 — regional mobility hubs",
            "Rhode Island Division of Statewide Planning / RIPTA (2020 Transit Master Plan)",
            "https://www.ripta.com/wp-content/uploads/2021/07/SPC-9-10-20.pdf",
            "State of Rhode Island public record.",
            "The eight regional mobility hubs the plan names, encoded in data/ri_mobility_hubs.csv "
            "with coordinates taken from RIPTA's GTFS stops; the statute (§ 45-24-33(a)(28)) "
            "defers to this plan for the definition.",
        ),
        Source(
            "eoh_integrated_2025",
            "2025 Integrated Housing Report",
            "Rhode Island Executive Office of Housing (published 2026-04-15; attested by the "
            "Office of Revenue Analysis)",
            "https://housing.ri.gov/sites/g/files/xkgbur401/files/2026-04/2025%20Integrated%20Housing%20Report.pdf",
            "State of Rhode Island public record.",
            "Municipal 2025 permits and certificates of occupancy by building size (EOH "
            "municipal survey, Feb–Mar 2026); ACS-derived stock tables; 2024 LMIH chart; "
            "household projections 2025–2035. Some hosts refuse automated clients (HTTP 403); "
            "the parser also accepts a locally supplied copy.",
        ),
        Source(
            "ripta_gtfs",
            "RIPTA GTFS schedule feed",
            "Rhode Island Public Transit Authority",
            "https://ripta.com/RIPTA-GTFS.zip",
            "Published for public developer use.",
            "Stops, trips and stop_times used to identify frequent-transit stops for the "
            "transit-oriented scenario per R.I.G.L. § 45-24-33(a)(28).",
        ),
        Source(
            "munianchor_district_params",
            "MuniAnchor ordinance-derived district parameters (allowed residential uses by "
            "district, dimensional envelopes), Rhode Island",
            "MuniAnchor (Gregory Guertin), derived from adopted municipal zoning ordinances",
            "https://munianchor.com/",
            "Apache-2.0 for this derived table; the underlying ordinances are public law. "
            "Each row cites the ordinance section it was read from.",
            "Optional tier-A input. When the file is absent the model runs at tier B from "
            "the State layer alone, which is the data-sparse demonstration.",
        ),
    )
}


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")[:120]


def manifest_path() -> Path:
    return CACHE_DIR / "manifest.json"


def _load_manifest() -> dict:
    p = manifest_path()
    if p.exists():
        return json.loads(p.read_text())
    return {"entries": {}}


def _save_manifest(m: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path().write_text(json.dumps(m, indent=2, sort_keys=True))


def record(name: str, *, source_id: str, url: str, path: Path, content_type: str = "") -> dict:
    """Append (or refresh) a manifest entry for a file already on disk."""
    data = path.read_bytes()
    entry = {
        "name": name,
        "source": source_id,
        "source_title": SOURCES[source_id].title,
        "publisher": SOURCES[source_id].publisher,
        "license": SOURCES[source_id].license,
        "url": url,
        "path": str(path.relative_to(CACHE_DIR)) if path.is_relative_to(CACHE_DIR) else str(path),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "content_type": content_type,
    }
    m = _load_manifest()
    m["entries"][name] = entry
    _save_manifest(m)
    return entry


def fetch(
    url: str,
    *,
    name: str,
    source_id: str,
    params: dict | None = None,
    headers: dict | None = None,
    refresh: bool = False,
    timeout: int = 120,
) -> Path:
    """Download ``url`` into the cache (once) and record it in the manifest.

    ``name`` is the cache file name and the manifest key. A cached file is
    reused unless ``refresh`` is set, so a full rebuild is reproducible
    offline once the cache is warm and a ``--refresh`` run re-verifies every
    source's current bytes.
    """
    if source_id not in SOURCES:
        raise KeyError(f"Unregistered source id {source_id!r}; add it to SOURCES")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / _slug(name)
    if path.exists() and not refresh:
        return path
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    resp = requests.get(url, params=params, headers=h, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(resp.content)
    tmp.replace(path)
    record(
        _slug(name),
        source_id=source_id,
        url=resp.url,
        path=path,
        content_type=resp.headers.get("Content-Type", ""),
    )
    return path


def fetch_filtered(
    url: str,
    *,
    name: str,
    source_id: str,
    keep,
    refresh: bool = False,
    timeout: int = 300,
) -> Path:
    """Stream a large text file and cache only the lines ``keep(line)`` accepts.

    For the Census summary files, which carry every geography in the country
    in one 48 MB file per table: the cache keeps the state's rows (a few KB)
    and the manifest records the source URL and the SHA-256 of what was kept,
    together with the SHA-256 of the full stream, so a republished file is
    still detectable.
    """
    if source_id not in SOURCES:
        raise KeyError(f"Unregistered source id {source_id!r}; add it to SOURCES")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / _slug(name)
    if path.exists() and not refresh:
        return path
    full_hash = hashlib.sha256()
    kept: list[str] = []
    with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout, stream=True) as resp:
        resp.raise_for_status()
        for raw in resp.iter_lines(decode_unicode=False):
            full_hash.update(raw)
            full_hash.update(b"\n")
            line = raw.decode("utf-8-sig", errors="replace")
            if keep(line):
                kept.append(line)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text("\n".join(kept) + "\n", encoding="utf-8")
    tmp.replace(path)
    entry = record(_slug(name), source_id=source_id, url=url, path=path, content_type="text/plain")
    m = _load_manifest()
    m["entries"][entry["name"]]["sha256_full_stream"] = full_hash.hexdigest()
    m["entries"][entry["name"]]["lines_kept"] = len(kept)
    _save_manifest(m)
    return path


def sources_table() -> list[dict]:
    """The provenance table the overview document prints."""
    m = _load_manifest()
    rows = []
    for e in sorted(m["entries"].values(), key=lambda e: (e["source"], e["name"])):
        rows.append(dict(e))
    return [asdict(s) for s in SOURCES.values()], rows
