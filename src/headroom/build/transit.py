"""Transit buffers for the transit-oriented scenario.

R.I.G.L. § 45-24-33(a)(28) (2026-H 8005A, effective on passage, June 2026)
bars a parking mandate above one space per multifamily unit within a
quarter mile of a regional mobility hub or an eighth of a mile of a
frequent transit stop, both "as defined in the 2020 Rhode Island transit
master plan or its successor document". The statute fixes the two
distances; the master plan's service definition is applied through two
ledger parameters (peak departures per hour for "frequent"; distinct routes
for "hub") so a reader can see and move them.
"""

from __future__ import annotations

import math

from shapely.geometry import Point
from shapely.ops import unary_union

QUARTER_MILE_FT = 1320.0
EIGHTH_MILE_FT = 660.0

# NAD83 / Rhode Island (ftUS), EPSG:3438: Transverse Mercator parameters.
_LAT0 = math.radians(41.08333333333334)
_LON0 = math.radians(-71.5)
_K0 = 0.99999375
_FE = 328083.3333  # false easting, ft
_FN = 0.0
_A = 20925646.325  # GRS80 semi-major axis in US survey feet
_F = 1 / 298.257222101
_E2 = 2 * _F - _F * _F


def _merid(lat: float) -> float:
    e2 = _E2
    e4, e6 = e2 * e2, e2 * e2 * e2
    return _A * (
        (1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * lat
        - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * math.sin(2 * lat)
        + (15 * e4 / 256 + 45 * e6 / 1024) * math.sin(4 * lat)
        - (35 * e6 / 3072) * math.sin(6 * lat)
    )


def to_state_plane(lat_deg: float, lon_deg: float) -> tuple[float, float]:
    """WGS84/NAD83 lat-lon → EPSG:3438 (ft). Standard TM series, ~cm accuracy.

    Implemented inline so the project needs no PROJ installation; the test
    suite checks it against known control points.
    """
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    e2 = _E2
    ep2 = e2 / (1 - e2)
    n = _A / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    t = math.tan(lat) ** 2
    c = ep2 * math.cos(lat) ** 2
    a = (lon - _LON0) * math.cos(lat)
    m = _merid(lat)
    m0 = _merid(_LAT0)
    x = _FE + _K0 * n * (
        a + (1 - t + c) * a**3 / 6 + (5 - 18 * t + t * t + 72 * c - 58 * ep2) * a**5 / 120
    )
    y = _FN + _K0 * (
        m
        - m0
        + n
        * math.tan(lat)
        * (
            a * a / 2
            + (5 - t + 9 * c + 4 * c * c) * a**4 / 24
            + (61 - 58 * t + t * t + 600 * c - 330 * ep2) * a**6 / 720
        )
    )
    return x, y


def buffers(
    freq: dict,
    *,
    frequent_peak_departures_per_hour: float,
    hub_min_routes: int,
    named_hubs: list[dict] | None = None,
) -> dict:
    """Union buffers: ``tod_stop`` (⅛ mi around frequent stops) and
    ``tod_hub`` (¼ mi around hub stops), in State Plane feet.

    Returns the geometries plus the list of qualifying stops so the choice
    is auditable.
    """
    stop_pts, hub_pts = [], []
    freq_stops, hub_stops = [], []
    for s in freq["stops"].values():
        per_hour = s["peak_departures"] / max(1, s["peak_hours"])
        x, y = to_state_plane(s["lat"], s["lon"])
        if per_hour >= frequent_peak_departures_per_hour:
            stop_pts.append(Point(x, y).buffer(EIGHTH_MILE_FT))
            freq_stops.append({**s, "peak_departures_per_hour": round(per_hour, 2)})
        if named_hubs is None and len(s["routes"]) >= hub_min_routes:
            hub_pts.append(Point(x, y).buffer(QUARTER_MILE_FT))
            hub_stops.append(s)
    if named_hubs is not None:
        # The plan's own list wins over the route-count proxy.
        for hub in named_hubs:
            x, y = to_state_plane(float(hub["lat"]), float(hub["lon"]))
            hub_pts.append(Point(x, y).buffer(QUARTER_MILE_FT))
            hub_stops.append({"stop_id": "", "stop_name": hub["name"], "lat": hub["lat"], "lon": hub["lon"],
                              "routes": [], "named": True, "source": hub.get("source", "")})
    geoms = {
        "tod_stop": unary_union(stop_pts) if stop_pts else Point(0, 0).buffer(0),
        "tod_hub": unary_union(hub_pts) if hub_pts else Point(0, 0).buffer(0),
    }
    geoms["tod_any"] = unary_union([geoms["tod_stop"], geoms["tod_hub"]])
    return {
        "geoms": geoms,
        "frequent_stops": freq_stops,
        "hub_stops": hub_stops,
        "hub_definition": "named list" if named_hubs is not None else f"stops with ≥ {hub_min_routes} routes",
        "service_day": freq["service_day"],
    }


def load_named_hubs(path) -> list[dict] | None:
    """Read a hub list CSV (name, municipality, lat, lon, ...); None when absent."""
    import csv
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        return None
    with open(p, newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("lat") and r.get("lon")]
