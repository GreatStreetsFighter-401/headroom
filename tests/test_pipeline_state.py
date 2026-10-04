"""The any-state tier-C build, on synthetic Census inputs."""

import json

from headroom.build import pipeline


def test_build_state_tier_c_assembles_towns_from_census_only(tmp_path, monkeypatch):
    subs = {
        "0600000US2501741690": {"geo_id": "0600000US2501741690", "name": "Melrose", "county": "017", "mcd": "41690"},
        "0600000US2500945000": {"geo_id": "0600000US2500945000", "name": "Lincoln", "county": "009", "mcd": "45000"},
        "0600000US2501745001": {"geo_id": "0600000US2501745001", "name": "Lincoln", "county": "017", "mcd": "45001"},
    }
    monkeypatch.setattr(pipeline.geos, "county_subdivisions", lambda *a, **k: subs)

    def fake_bps(years, *, refresh=False, state_fips="44", mcd_to_name=None):
        assert state_fips == "25" and mcd_to_name is not None
        rows = []
        for y in years:
            rows.append(
                {
                    "year": y,
                    "municipality": mcd_to_name["41690"],
                    "months_reported": 12,
                    "units_1": 10,
                    "units_2": 2,
                    "units_3_4": 0,
                    "units_5plus": 20,
                    "units_total": 32,
                }
            )
        return rows

    monkeypatch.setattr(pipeline.bps, "fetch_years", fake_bps)
    monkeypatch.setattr(
        pipeline.acs,
        "fetch_summary_stock",
        lambda *a, **k: {
            "0600000US2501741690": {
                "units_total": 12000,
                "units_1": 6500,
                "units_2": 2000,
                "units_3_4": 1500,
                "units_5plus": 2000,
                "units_mobile": 0,
                "occupied": 11500,
                "vacant": 500,
            },
        },
    )
    out = pipeline.build_state_tier_c("25", "MA", out_path=tmp_path / "towns.json")
    towns = out["towns"]
    # Duplicate names across counties are disambiguated, never merged.
    assert {"Melrose", "Lincoln (009)", "Lincoln (017)"} == set(towns)
    m = towns["Melrose"]
    assert m["permits_bps"][2025] == 32 and m["mf_share_2018_2025"] == round(22 / 32, 4)
    assert m["stock"]["units_1"] == 6500
    assert m["n_R1"] is None and m["tier"] == "C"
    assert out["permit_undercount"]["eoh_to_bps_ratio_2025"] == 1.0
    assert out["n_with_permit_series"] == 1
    assert json.loads((tmp_path / "towns.json").read_text())["state"] == "MA"
