from headroom.build import transit


def test_state_plane_projection_matches_rigis_vertex():
    # A Jamestown zoning vertex served by RIGIS in both EPSG:4326 and EPSG:3438.
    x, y = transit.to_state_plane(41.5245135455691, -71.3620079790376)
    err = ((x - 365870.146352161) ** 2 + (y - 160778.302975655) ** 2) ** 0.5
    assert err < 10.0  # feet; WGS84 vs NAD83 datum difference is ~1 m here


def test_buffers_use_statutory_distances():
    freq = {
        "service_day": "2026-09-16",
        "stops": {
            "a": {
                "stop_id": "a",
                "stop_name": "frequent",
                "lat": 41.824,
                "lon": -71.413,
                "weekday_departures": 100,
                "peak_departures": 10,
                "peak_hours": 2,
                "routes": ["1"],
            },
            "b": {
                "stop_id": "b",
                "stop_name": "hub",
                "lat": 41.900,
                "lon": -71.500,
                "weekday_departures": 100,
                "peak_departures": 2,
                "peak_hours": 2,
                "routes": [str(i) for i in range(8)],
            },
            "c": {
                "stop_id": "c",
                "stop_name": "quiet",
                "lat": 41.700,
                "lon": -71.600,
                "weekday_departures": 5,
                "peak_departures": 1,
                "peak_hours": 2,
                "routes": ["9"],
            },
        },
    }
    out = transit.buffers(freq, frequent_peak_departures_per_hour=4, hub_min_routes=6)
    assert [s["stop_id"] for s in out["frequent_stops"]] == ["a"]
    assert [s["stop_id"] for s in out["hub_stops"]] == ["b"]
    import math

    assert math.isclose(out["geoms"]["tod_stop"].area, math.pi * 660**2, rel_tol=0.01)
    assert math.isclose(out["geoms"]["tod_hub"].area, math.pi * 1320**2, rel_tol=0.01)
