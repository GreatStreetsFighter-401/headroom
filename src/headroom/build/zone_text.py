"""Read what a zoning district allows from the State layer's description text.

The State zoning layer's ``DENSITY`` field is a lot-size band (verified:
LOW ⇔ 2+ acre lots, HIGH ⇔ 5,000 sq ft–¼ acre, and so on), not a statement
of which unit types a district permits. The only text the layer carries
about allowed uses is ``ZONE_DESC``, which some towns fill informatively
("Single-Family. Minimum 12k SF lots", "Residential Two-Family",
"Residential 6 One, two, three-family") and others do not ("Residential").

This classifier turns that text into one of three readings and *always*
reports how it decided, because at tier B this is the weakest link in the
chain and the overview has to say so. Tier A (ordinance-derived allowed
uses from MuniAnchor's use tables) overrides it wherever present.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SF_ONLY = "single_family_only"
ALLOWS_2PLUS = "allows_2plus"
UNKNOWN = "unknown"

_SF_PATTERNS = (
    r"\bsingle[\s-]*family\b",
    r"\bone[\s-]*family\b",
    r"\b1[\s-]*family\b",
    r"\bsingle[\s-]*household\b",
    r"\bdetached\b",
    r"\bR[\s-]?1\b",  # a bare R-1 is single-family in most RI codes, weak evidence
)
_MULTI_PATTERNS = (
    r"\btwo[\s-]*family\b",
    r"\b2[\s-]*family\b",
    r"\bthree[\s-]*family\b",
    r"\bmulti[\s-]*family\b",
    r"\bmultifamily\b",
    r"\bmulti[\s-]*household\b",
    r"\bduplex\b",
    r"\bapartment\b",
    r"\bgeneral residen",
    r"\bvillage\b",
    r"\bmixed[\s-]*use\b",
    r"\bdowntown\b",
    r"\bhigh[\s-]*density\b",
    r"\bRM\b",
    r"\bRT\b",
    r"\bMF\b",
)


@dataclass(frozen=True)
class Reading:
    allowed: str  # SF_ONLY | ALLOWS_2PLUS | UNKNOWN
    evidence: str  # which rule fired, for the audit trail
    confidence: str  # "text" | "code" | "none"


def classify(zone_code: str | None, zone_desc: str | None) -> Reading:
    desc = (zone_desc or "").strip()
    code = (zone_code or "").strip()
    text = f"{desc}"
    multi = [p for p in _MULTI_PATTERNS if re.search(p, text, re.I)]
    sf = [p for p in _SF_PATTERNS if re.search(p, text, re.I)]
    # "One, two, three-family" mentions both; the multi reading wins because
    # the question is whether anything beyond one unit is allowed.
    if multi:
        return Reading(ALLOWS_2PLUS, f"desc matches {multi[0]}", "text")
    if sf:
        return Reading(SF_ONLY, f"desc matches {sf[0]}", "text")
    # Fall back to the code's shape. RS/RA/R-xx with a number ≥ 10 (thousand
    # sq ft) or an acreage suffix reads as a large-lot single-family district
    # in most RI codes; anything else stays unknown.
    if re.match(r"^(RS|RA|RR|RE|RL|AR|A)[\s-]?\d*$", code, re.I):
        return Reading(SF_ONLY, f"code shape {code}", "code")
    if re.match(r"^(RM|RG|RT|MF|R-?[4-9])$", code, re.I):
        return Reading(ALLOWS_2PLUS, f"code shape {code}", "code")
    return Reading(UNKNOWN, "no usable text", "none")
