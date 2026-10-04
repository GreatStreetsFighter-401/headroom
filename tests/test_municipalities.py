import pytest

from headroom.municipalities import (
    COUNTY_MCD_FIPS,
    MCD_TO_MUNICIPALITY,
    RI_MUNICIPALITIES,
    canonical,
)


def test_thirty_nine():
    assert len(RI_MUNICIPALITIES) == 39
    assert len(set(RI_MUNICIPALITIES)) == 39
    assert set(COUNTY_MCD_FIPS) == set(RI_MUNICIPALITIES)
    assert len(MCD_TO_MUNICIPALITY) == 39


@pytest.mark.parametrize(
    "raw, want",
    [
        ("Barrington town", "Barrington"),
        ("Central Falls", "Central Falls"),
        ("PORTSMOUTH", "Portsmouth"),
        ("Town of North Kingstown", "North Kingstown"),
        ("  east   providence  ", "East Providence"),
        ("Block Island", "New Shoreham"),
        ("Warwick", "Warwick"),
    ],
)
def test_canonical(raw, want):
    assert canonical(raw) == want


def test_non_municipal_rows_map_to_none():
    assert canonical("Quonset") is None
    assert canonical(None) is None


def test_unknown_name_raises():
    with pytest.raises(KeyError):
        canonical("Springfield")


def test_county_codes_are_the_five_ri_counties():
    assert {c for c, _ in COUNTY_MCD_FIPS.values()} == {"001", "003", "005", "007", "009"}
