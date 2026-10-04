"""The 39 Rhode Island municipalities and the name forms the sources use.

Every source spells towns differently: the Census Building Permits Survey
writes ``Barrington town`` and ``Central Falls``; E-911 writes
``PORTSMOUTH``; RIGIS zoning writes ``Smithfield`` and also carries a
``Quonset`` row for the Quonset Development Corporation, which is not a
municipality. ``canonical()`` maps all of them onto one spelling so joins
cannot silently drop a town.
"""

from __future__ import annotations

import re

RI_MUNICIPALITIES: tuple[str, ...] = (
    "Barrington",
    "Bristol",
    "Burrillville",
    "Central Falls",
    "Charlestown",
    "Coventry",
    "Cranston",
    "Cumberland",
    "East Greenwich",
    "East Providence",
    "Exeter",
    "Foster",
    "Glocester",
    "Hopkinton",
    "Jamestown",
    "Johnston",
    "Lincoln",
    "Little Compton",
    "Middletown",
    "Narragansett",
    "New Shoreham",
    "Newport",
    "North Kingstown",
    "North Providence",
    "North Smithfield",
    "Pawtucket",
    "Portsmouth",
    "Providence",
    "Richmond",
    "Scituate",
    "Smithfield",
    "South Kingstown",
    "Tiverton",
    "Warren",
    "Warwick",
    "West Greenwich",
    "West Warwick",
    "Westerly",
    "Woonsocket",
)

# Census county (3-digit) and county-subdivision / MCD (5-digit) FIPS codes
# for state 44, taken from the Building Permits Survey place file
# (ne2024a.txt columns "County Code" and "FIPS MCD"), not from memory.
COUNTY_MCD_FIPS: dict[str, tuple[str, str]] = {
    "Barrington": ("001", "05140"),
    "Bristol": ("001", "09280"),
    "Warren": ("001", "73760"),
    "Coventry": ("003", "18640"),
    "East Greenwich": ("003", "22240"),
    "Warwick": ("003", "74300"),
    "West Greenwich": ("003", "77720"),
    "West Warwick": ("003", "78440"),
    "Jamestown": ("005", "36820"),
    "Little Compton": ("005", "42400"),
    "Middletown": ("005", "45460"),
    "Newport": ("005", "49960"),
    "Portsmouth": ("005", "57880"),
    "Tiverton": ("005", "70880"),
    "Burrillville": ("007", "11800"),
    "Central Falls": ("007", "14140"),
    "Cranston": ("007", "19180"),
    "Cumberland": ("007", "20080"),
    "East Providence": ("007", "22960"),
    "Foster": ("007", "27460"),
    "Glocester": ("007", "30340"),
    "Johnston": ("007", "37720"),
    "Lincoln": ("007", "41500"),
    "North Providence": ("007", "51760"),
    "North Smithfield": ("007", "52480"),
    "Pawtucket": ("007", "54640"),
    "Providence": ("007", "59000"),
    "Scituate": ("007", "64220"),
    "Smithfield": ("007", "66200"),
    "Woonsocket": ("007", "80780"),
    "Charlestown": ("009", "14500"),
    "Exeter": ("009", "25300"),
    "Hopkinton": ("009", "35380"),
    "Narragansett": ("009", "48340"),
    "New Shoreham": ("009", "50500"),
    "North Kingstown": ("009", "51580"),
    "Richmond": ("009", "61160"),
    "South Kingstown": ("009", "67460"),
    "Westerly": ("009", "77000"),
}

MCD_TO_MUNICIPALITY: dict[str, str] = {mcd: name for name, (_c, mcd) in COUNTY_MCD_FIPS.items()}

_NON_MUNICIPAL = {"quonset", "quonset development corporation", "block island state"}

_ALIASES = {
    "block island": "New Shoreham",
}


def canonical(name: str | None) -> str | None:
    """Return the canonical municipality name, or ``None`` for non-towns.

    Handles ``town``/``city`` suffixes, ``Town of`` prefixes, case, stray
    whitespace and the Block Island alias. Unknown names raise, because a
    silently dropped town is the failure mode this exists to prevent.
    """
    if name is None:
        return None
    s = re.sub(r"\s+", " ", name).strip()
    s = re.sub(r"^(town|city) of ", "", s, flags=re.I)
    s = re.sub(r"\s+(town|city)$", "", s, flags=re.I)
    key = s.lower()
    if key in _NON_MUNICIPAL:
        return None
    if key in _ALIASES:
        return _ALIASES[key]
    for m in RI_MUNICIPALITIES:
        if m.lower() == key:
            return m
    raise KeyError(f"Unknown Rhode Island municipality: {name!r}")
