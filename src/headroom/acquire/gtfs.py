"""RIPTA GTFS: stops and weekday service frequency.

The transit-oriented scenario needs "frequent transit stops" and "regional
mobility hubs" in the sense of R.I.G.L. § 45-24-33(a)(28). Frequency is computed
from the schedule itself: for each stop, the number of scheduled weekday
departures in the service day and in the peak window. The thresholds that
turn a count into "frequent" are ledger parameters, not constants here.
"""

from __future__ import annotations

import csv
import io
import zipfile
from collections import Counter, defaultdict
from datetime import date, timedelta

from headroom.acquire.base import fetch

URL = "https://ripta.com/RIPTA-GTFS.zip"


def get_feed(*, refresh: bool = False):
    path = fetch(URL, name="ripta_gtfs.zip", source_id="ripta_gtfs", refresh=refresh)
    return zipfile.ZipFile(path)


def _read(z: zipfile.ZipFile, name: str) -> list[dict]:
    with z.open(name) as f:
        return list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")))


def _weekday_services(z: zipfile.ZipFile) -> tuple[set[str], str]:
    """Service ids active on a representative weekday.

    RIPTA's feed has no calendar.txt; every service is enumerated in
    calendar_dates.txt. We pick the first Wednesday inside the feed window
    that is not an exception-removed day and return the services added on it.
    """
    names = set(z.namelist())
    info = _read(z, "feed_info.txt")[0] if "feed_info.txt" in names else {}
    start = info.get("feed_start_date")
    d = date(int(start[:4]), int(start[4:6]), int(start[6:8])) if start else date.today()
    while d.weekday() != 2:  # Wednesday
        d += timedelta(days=1)
    added: set[str] = set()
    if "calendar_dates.txt" in names:
        key = d.strftime("%Y%m%d")
        for r in _read(z, "calendar_dates.txt"):
            if r["date"] == key and r["exception_type"] == "1":
                added.add(r["service_id"])
    if "calendar.txt" in names:
        for r in _read(z, "calendar.txt"):
            if r.get("wednesday") == "1" and r["start_date"] <= d.strftime("%Y%m%d") <= r["end_date"]:
                added.add(r["service_id"])
    return added, d.isoformat()


def stop_frequencies(*, peak=(7, 9), refresh: bool = False) -> dict:
    """Per-stop weekday departures: all-day and within the peak hours."""
    z = get_feed(refresh=refresh)
    services, day = _weekday_services(z)
    trips = {r["trip_id"]: r for r in _read(z, "trips.txt") if r["service_id"] in services}
    stops = {r["stop_id"]: r for r in _read(z, "stops.txt")}
    all_day: Counter = Counter()
    peak_cnt: Counter = Counter()
    routes_by_stop: dict[str, set] = defaultdict(set)
    for r in _read(z, "stop_times.txt"):
        t = trips.get(r["trip_id"])
        if t is None:
            continue
        sid = r["stop_id"]
        all_day[sid] += 1
        routes_by_stop[sid].add(t["route_id"])
        dep = r.get("departure_time") or r.get("arrival_time") or ""
        try:
            hour = int(dep.split(":")[0])
        except ValueError:
            continue
        if peak[0] <= hour < peak[1]:
            peak_cnt[sid] += 1
    out = {}
    for sid, s in stops.items():
        if s.get("location_type") not in ("", "0", None):
            continue
        out[sid] = {
            "stop_id": sid,
            "stop_name": s.get("stop_name", ""),
            "lat": float(s["stop_lat"]),
            "lon": float(s["stop_lon"]),
            "weekday_departures": all_day.get(sid, 0),
            "peak_departures": peak_cnt.get(sid, 0),
            "peak_hours": peak[1] - peak[0],
            "routes": sorted(routes_by_stop.get(sid, ())),
        }
    return {"service_day": day, "services": sorted(services), "stops": out}
