"""Municipal tables from the State's 2025 Integrated Housing Report.

The Executive Office of Housing publishes, under R.I.G.L. § 42-167-4(4), a
report whose municipal tables are the State's own record of 2025 permits
and certificates of occupancy (its February–March 2026 municipal survey)
and ACS-derived stock by municipality. The PDF is the authoritative
publication; this module downloads it and reads the ruled tables with
pdfplumber.

The host sometimes refuses automated clients with HTTP 403. The parser
therefore also accepts a path to a locally saved copy
(``HEADROOM_EOH_PDF``), and the manifest records whichever was used.

Figures read (page numbers as printed):
  1.1  total / occupied / vacant units (ACS 2024 5-yr B25002, B25004)   pp. 4–5
  1.4  units by building type (ACS 2024 5-yr B25024)                      pp. 8–10
  2.1  2025 residential permits by size class (EOH survey)                pp. 16–17
  2.4  2025 certificates of occupancy by size class (EOH survey)          pp. 20–21
  3.12 2024 LMIH chart                                                     pp. 27–28
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pdfplumber

from headroom.acquire.base import fetch, record
from headroom.municipalities import RI_MUNICIPALITIES, canonical

URL = "https://housing.ri.gov/sites/g/files/xkgbur401/files/2026-04/2025%20Integrated%20Housing%20Report.pdf"

_NUM = re.compile(r"^-?[\d,]+(\.\d+)?%?$")
_TOWN_WORDS = {w for m in RI_MUNICIPALITIES for w in m.split()}


def get_pdf(*, refresh: bool = False) -> Path:
    local = os.environ.get("HEADROOM_EOH_PDF")
    if local and Path(local).exists():
        p = Path(local)
        record("eoh_integrated_2025.pdf", source_id="eoh_integrated_2025", url=URL, path=p)
        return p
    return fetch(
        URL,
        name="eoh_integrated_2025.pdf",
        source_id="eoh_integrated_2025",
        headers={"Accept": "application/pdf"},
        refresh=refresh,
    )


def _clean(cell) -> str:
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()


def _compress(row: list) -> list[str]:
    return [c for c in (_clean(x) for x in row) if c != ""]


def _is_num(s: str) -> bool:
    return bool(_NUM.match(s))


def _num(s: str) -> float | int:
    s = s.replace(",", "")
    if s.endswith("%"):
        return float(s[:-1]) / 100.0
    return float(s) if "." in s else int(s)


def _rows_from_tables(pages: list) -> list[list[str]]:
    """Flatten ruled tables into compressed rows, re-joining split rows.

    pdfplumber sometimes emits a two-line municipality name as its own row
    with only the trailing total, followed by a row of the numbers with no
    name (page 17 of the 2025 report). The merge rule below re-joins them.
    """
    out: list[list[str]] = []
    for page in pages:
        for table in page.extract_tables():
            pending: list[str] | None = None
            for raw in table:
                row = _compress(raw)
                if not row:
                    continue
                if pending is not None:
                    if not _is_num(row[0]):
                        out.append(pending)
                        pending = None
                    else:
                        # name [+ trailing total] followed by the number row
                        name, *tail = pending
                        out.append([name, *row, *tail])
                        pending = None
                        continue
                nums = [c for c in row[1:] if _is_num(c)]
                if not _is_num(row[0]) and len(nums) <= 1 and len(row) <= 2:
                    pending = row
                    continue
                out.append(row)
            if pending is not None:
                out.append(pending)
    # A two-word municipality can also arrive as its numbers on the first
    # word's row and the second word alone on the next ("East" … / "Greenwich").
    merged: list[list[str]] = []
    for row in out:
        if (
            len(row) == 1
            and not _is_num(row[0])
            and merged
            and not _is_num(merged[-1][0])
            and f"{merged[-1][0]} {row[0]}".split()[-1] in _TOWN_WORDS
        ):
            candidate = f"{merged[-1][0]} {row[0]}"
            try:
                if canonical(candidate):
                    merged[-1][0] = candidate
                    continue
            except KeyError:
                pass
        merged.append(row)
    return merged


def _repair_one_short(vals: list, names: list[str]) -> list | None:
    """Place the one blank cell in a size-class table where the arithmetic says.

    The printed tables leave a cell blank occasionally (North Smithfield's
    5+-unit buildings on the 2025 certificate-of-occupancy table). The row
    then carries n−1 numbers and the blank's position is ambiguous. The
    size-class tables satisfy units_total = units_1 + units_2 + units_3_4 +
    units_5plus, so we try every insertion point and keep the only one that
    makes the identity hold; if none or several do, the row is rejected.
    """
    if "units_total" not in names:
        return None

    def consistent(rec: dict) -> bool:
        parts = [rec.get(k) for k in ("units_1", "units_2", "units_3_4", "units_5plus")]
        if rec.get("units_total") is None or any(p is None for p in parts):
            return False
        if sum(parts) != rec["units_total"]:
            return False
        # Buildings and units must agree with the size class where both are known.
        b1, b2, b34, b5 = (rec.get(k) for k in ("bldgs_1", "bldgs_2", "bldgs_3_4", "bldgs_5plus"))
        u1, u2, u34, u5 = parts
        if b1 is not None and u1 < b1:
            return False
        if b2 is not None and u2 != 2 * b2:
            return False
        if b34 is not None and not (3 * b34 <= u34 <= 4 * b34):
            return False
        if b5 is not None and (u5 < 5 * b5 or (b5 == 0 and u5 != 0)):
            return False
        return True

    hits = []
    for pos in range(len(vals) + 1):
        trial = vals[:pos] + [None] + vals[pos:]
        if consistent(dict(zip(names, trial, strict=True))):
            hits.append(trial)
    return hits[0] if len(hits) == 1 else None


def _municipal_rows(rows: list[list[str]], n_numbers: int, names: list[str]) -> dict[str, list]:
    """Keep rows whose first cell is a municipality and that carry n numbers."""
    found: dict[str, list] = {}
    for row in rows:
        name = row[0]
        if name.lower().startswith("statewide"):
            continue
        try:
            muni = canonical(name)
        except KeyError:
            continue
        if muni is None:
            continue
        vals = [_num(c) for c in row[1:] if _is_num(c)]
        if len(vals) >= n_numbers:
            found[muni] = vals[:n_numbers]
        elif len(vals) == n_numbers - 1:
            repaired = _repair_one_short(vals, names)
            if repaired is not None:
                found[muni] = repaired
    return found


def _statewide(rows: list[list[str]], n_numbers: int) -> list | None:
    for row in rows:
        if row[0].lower().startswith("statewide"):
            vals = [c for c in row[1:] if _is_num(c)]
            if len(vals) >= n_numbers:
                return [_num(v) for v in vals[:n_numbers]]
    return None


def _figure(pdf, pages: tuple[int, ...], n: int, names: list[str]) -> tuple[dict, dict | None]:
    rows = _rows_from_tables([pdf.pages[p - 1] for p in pages])
    muni = _municipal_rows(rows, n, names)
    missing = [m for m in RI_MUNICIPALITIES if m not in muni]
    if missing:
        raise ValueError(f"EOH figure on pages {pages}: missing {missing}")
    table = {m: dict(zip(names, vals, strict=True)) for m, vals in muni.items()}
    sw = _statewide(rows, n)
    return table, (dict(zip(names, sw, strict=True)) if sw else None)


def read_report(pdf_path: Path | None = None) -> dict:
    """All municipal tables, each a dict municipality → fields, plus totals."""
    path = pdf_path or get_pdf()
    with pdfplumber.open(path) as pdf:
        permits_2025, permits_sw = _figure(
            pdf,
            (16, 17),
            9,
            [
                "bldgs_1",
                "units_1",
                "bldgs_2",
                "units_2",
                "bldgs_3_4",
                "units_3_4",
                "bldgs_5plus",
                "units_5plus",
                "units_total",
            ],
        )
        co_2025, co_sw = _figure(
            pdf,
            (20, 21),
            9,
            [
                "bldgs_1",
                "units_1",
                "bldgs_2",
                "units_2",
                "bldgs_3_4",
                "units_3_4",
                "bldgs_5plus",
                "units_5plus",
                "units_total",
            ],
        )
        stock, stock_sw = _figure(
            pdf,
            (4, 5),
            7,
            [
                "units_total",
                "occupied",
                "vacant",
                "for_sale_or_rent",
                "occupancy_rate",
                "vacancy_rate",
                "for_sale_or_rent_rate",
            ],
        )
        by_type, by_type_sw = _figure(
            pdf,
            (8, 9, 10),
            7,
            [
                "units_total",
                "units_1",
                "units_2",
                "units_3_4",
                "units_5plus",
                "units_mobile",
                "units_other",
            ],
        )
        lmih, lmih_sw = _figure(
            pdf,
            (27, 28),
            3,
            ["lmih_units", "year_round_units_2020", "lmih_share"],
        )
    # Internal consistency: each municipal table sums to its printed statewide row.
    checks = {}
    for key, table, sw, field in (
        ("permits_2025", permits_2025, permits_sw, "units_total"),
        ("co_2025", co_2025, co_sw, "units_total"),
        ("stock", stock, stock_sw, "units_total"),
        ("by_type", by_type, by_type_sw, "units_total"),
        ("lmih", lmih, lmih_sw, "lmih_units"),
    ):
        total = sum(v[field] for v in table.values() if v[field] is not None)
        printed = sw[field] if sw else None
        checks[key] = {
            "sum_of_municipalities": total,
            "printed_statewide": printed,
            "agrees": (printed is not None and total == printed),
        }
    return {
        "source": "eoh_integrated_2025",
        "pdf": str(path),
        "permits_2025": permits_2025,
        "co_2025": co_2025,
        "stock_acs2024": stock,
        "units_by_type_acs2024": by_type,
        "lmih_2024": lmih,
        "statewide": {
            "permits_2025": permits_sw,
            "co_2025": co_sw,
            "stock_acs2024": stock_sw,
            "units_by_type_acs2024": by_type_sw,
            "lmih_2024": lmih_sw,
        },
        "checks": checks,
    }


# Figures 1.3 and 2.2 are transcribed because they are not municipal
# tables: household growth 2025→2030/2035 under four projection methods,
# and the statewide permit series the report prints as a chart.
HOUSEHOLD_GROWTH_2025_2030 = {
    "moodys": 354,
    "cagr_population_moodys_hh_size": 11287,
    "moodys_by_age_cagr_formation": 5274,
    "cagr_population_and_formation": 26726,
}
HOUSEHOLD_GROWTH_2025_2035 = {
    "moodys": 2467,
    "cagr_population_moodys_hh_size": 23563,
    "moodys_by_age_cagr_formation": 9733,
    "cagr_population_and_formation": 59660,
}
HOUSING_2030_PERMIT_GOAL = 15000  # statewide, 2026–2030, per Housing 2030
