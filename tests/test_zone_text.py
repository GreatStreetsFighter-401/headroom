import pytest

from headroom.build import zone_text as zt


@pytest.mark.parametrize(
    "code, desc, want",
    [
        ("A-12", "Single-Family.  Minimum 12k SF lots", zt.SF_ONLY),
        ("R-1", "Residential 1 One-family", zt.SF_ONLY),
        ("RS12", "Residential Single-Family", zt.SF_ONLY),
        ("RT", "Residential Two-Family", zt.ALLOWS_2PLUS),
        ("R-6", "Residential 6 One, two, three-family", zt.ALLOWS_2PLUS),
        ("RM", "Residential Multifamily", zt.ALLOWS_2PLUS),
        ("MF", "Multi-Family", zt.ALLOWS_2PLUS),
        ("V", "Village Commercial", zt.ALLOWS_2PLUS),
        ("R-20", "Residential", zt.UNKNOWN),
        ("C", "Commercial", zt.UNKNOWN),
    ],
)
def test_classify(code, desc, want):
    r = zt.classify(code, desc)
    assert r.allowed == want
    assert r.evidence


def test_mixed_text_reads_as_allowing_more_than_one_unit():
    assert zt.classify("R-6", "One, two, three-family").allowed == zt.ALLOWS_2PLUS


def test_code_shape_fallback_is_marked_as_weaker_evidence():
    r = zt.classify("RA-80", "")
    assert r.allowed == zt.SF_ONLY and r.confidence == "code"
