"""Paged reads from ArcGIS REST feature services (RIGIS).

RIGIS distributes its layers through ArcGIS Online feature services with a
2,000-record page limit. :func:`query_all` walks ``resultOffset`` pages,
asks for GeoJSON in Rhode Island State Plane feet (EPSG:3438, so distances
and areas are in feet without a projection step), and caches the whole
layer as one file so a rebuild never re-walks the service.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import requests

from headroom import CACHE_DIR
from headroom.acquire.base import SOURCES, USER_AGENT, record

RI_STATE_PLANE_FT = 3438  # NAD83 / Rhode Island (ftUS)

RIGIS = {
    "rigis_zoning": ("https://services2.arcgis.com/S8zZg9pg23JUEexQ/arcgis/rest/services/RI_Zoning/FeatureServer/1"),
    "rigis_overlays": ("https://services2.arcgis.com/S8zZg9pg23JUEexQ/arcgis/rest/services/RI_Zoning/FeatureServer/0"),
    "rigis_e911_points": (
        "https://services2.arcgis.com/S8zZg9pg23JUEexQ/arcgis/rest/services/"
        "FACILITY_AddressPoints_E911domains/FeatureServer/5"
    ),
    "rigis_sewered": (
        "https://services2.arcgis.com/S8zZg9pg23JUEexQ/arcgis/rest/services/UTILITY_Sewered_Areas_spf/FeatureServer/0"
    ),
}


def _page(
    layer_url: str,
    *,
    where: str,
    out_fields: str,
    geometry: bool,
    offset: int,
    page_size: int,
    out_sr: int,
    max_allowable_offset: float | None,
    timeout: int,
) -> dict:
    params = {
        "where": where,
        "outFields": out_fields,
        "returnGeometry": "true" if geometry else "false",
        "outSR": out_sr,
        "resultOffset": offset,
        "resultRecordCount": page_size,
        "orderByFields": "OBJECTID",
        "f": "geojson",
    }
    if max_allowable_offset:
        params["maxAllowableOffset"] = max_allowable_offset
    for attempt in range(5):
        try:
            r = requests.get(
                f"{layer_url}/query",
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
            )
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(f"ArcGIS error: {data['error']}")
            return data
        except (requests.RequestException, ValueError, RuntimeError):
            if attempt == 4:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def query_all(
    source_id: str,
    *,
    where: str = "1=1",
    out_fields: str = "*",
    geometry: bool = True,
    page_size: int = 2000,
    out_sr: int = RI_STATE_PLANE_FT,
    max_allowable_offset: float | None = None,
    refresh: bool = False,
    timeout: int = 180,
    cache_tag: str = "",
) -> Path:
    """Fetch every feature of a RIGIS layer into one cached GeoJSON file.

    Returns the cache path. The manifest records the service URL and the
    SHA-256 of the assembled file, so a later ``--refresh`` run shows whether
    the State has republished the layer.
    """
    layer_url = RIGIS[source_id]
    tag = cache_tag or f"{where}|{out_fields}|{int(geometry)}|{out_sr}|{max_allowable_offset}"
    # A stable digest, not hash(): Python salts str hashes per process.
    name = f"{source_id}__{hashlib.sha1(tag.encode()).hexdigest()[:10]}.geojson"
    path = CACHE_DIR / name
    if path.exists() and not refresh:
        return path
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    features: list[dict] = []
    offset = 0
    while True:
        data = _page(
            layer_url,
            where=where,
            out_fields=out_fields,
            geometry=geometry,
            offset=offset,
            page_size=page_size,
            out_sr=out_sr,
            max_allowable_offset=max_allowable_offset,
            timeout=timeout,
        )
        batch = data.get("features", [])
        features.extend(batch)
        exceeded = data.get("properties", {}).get("exceededTransferLimit") or data.get("exceededTransferLimit")
        if len(batch) < page_size and not exceeded:
            break
        if not batch:
            break
        offset += len(batch)
    out = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": f"EPSG:{out_sr}"}},
        "query": {"layer": layer_url, "where": where, "outFields": out_fields},
        "features": features,
    }
    tmp = path.with_suffix(".part")
    tmp.write_text(json.dumps(out))
    tmp.replace(path)
    record(
        name,
        source_id=source_id,
        url=f"{layer_url}/query?where={where}",
        path=path,
        content_type="application/geo+json",
    )
    return path


def load_features(path: Path) -> list[dict]:
    return json.loads(path.read_text())["features"]


def describe(source_id: str) -> dict:
    """Layer metadata (fields, record count) for the provenance appendix."""
    layer_url = RIGIS[source_id]
    meta = requests.get(f"{layer_url}?f=json", headers={"User-Agent": USER_AGENT}, timeout=60)
    meta.raise_for_status()
    m = meta.json()
    count = requests.get(
        f"{layer_url}/query",
        params={"where": "1=1", "returnCountOnly": "true", "f": "json"},
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    ).json()
    return {
        "source": SOURCES[source_id].title,
        "layer": m.get("name"),
        "fields": [f["name"] for f in m.get("fields", [])],
        "count": count.get("count"),
        "max_record_count": m.get("maxRecordCount"),
    }
