"""The assumption ledger: one registry that the model, the UI and the
Model and Assumptions Overview all read.

``assumptions.yaml`` holds every Stage 2 parameter — behaviour, cost,
feasibility, baseline shape — as a record with a default, a range, a
sampling distribution, a status (statutory / verified / prior /
placeholder), a source and a justification. The Monte Carlo samples from
this file; the CLI's ``explain`` prints from it; the overview's assumption
chapter is generated from it. Nothing in the model is allowed to carry a
behavioural constant that is not here, and ``tests/test_ledger.py`` greps
the model package to enforce that.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import yaml

from headroom import LEDGER_PATH

STATUSES = ("statutory", "verified", "prior", "placeholder", "design")
DISTRIBUTIONS = ("fixed", "uniform", "triangular", "lognormal")


@dataclass
class Parameter:
    id: str
    label: str
    scenarios: list[str]
    stage: int
    unit: str
    default: float
    low: float | None
    high: float | None
    distribution: str
    status: str
    source: str
    justification: str
    ri_calibration: str = ""
    what_it_cannot_say: str = ""
    sensitivity: bool = True
    tags: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errs = []
        if self.status not in STATUSES:
            errs.append(f"{self.id}: status {self.status!r} not in {STATUSES}")
        if self.distribution not in DISTRIBUTIONS:
            errs.append(f"{self.id}: distribution {self.distribution!r}")
        if self.distribution != "fixed":
            if self.low is None or self.high is None:
                errs.append(f"{self.id}: non-fixed parameter needs low and high")
            elif not (self.low <= self.default <= self.high):
                errs.append(f"{self.id}: default {self.default} outside [{self.low}, {self.high}]")
            elif self.distribution == "lognormal" and self.low <= 0:
                errs.append(f"{self.id}: lognormal needs low > 0")
        if not self.source.strip():
            errs.append(f"{self.id}: source is empty")
        if not self.justification.strip():
            errs.append(f"{self.id}: justification is empty")
        return errs

    def sample(self, rng: np.random.Generator, n: int) -> np.ndarray:
        """Draw n values. The range is read as a 90% interval for lognormal."""
        d = self.distribution
        if d == "fixed":
            return np.full(n, float(self.default))
        lo, hi, mode = float(self.low), float(self.high), float(self.default)
        if d == "uniform":
            return rng.uniform(lo, hi, n)
        if d == "triangular":
            if not (lo < mode < hi):
                # degenerate: mode on an edge
                mode = min(max(mode, lo + 1e-12), hi - 1e-12)
            return rng.triangular(lo, mode, hi, n)
        if d == "lognormal":
            sigma = (math.log(hi) - math.log(lo)) / (2 * 1.6449)
            x = rng.lognormal(math.log(mode), sigma, n)
            return np.clip(x, lo, hi)
        raise ValueError(d)


@dataclass
class Scenario:
    id: str
    label: str
    handbook_definition: str
    modelled_as: str
    ri_law_today: str = ""
    what_it_cannot_say: str = ""


@dataclass
class Ledger:
    meta: dict
    scenarios: dict[str, Scenario]
    parameters: dict[str, Parameter]

    def validate(self) -> list[str]:
        errs = []
        for p in self.parameters.values():
            errs.extend(p.validate())
            for s in p.scenarios:
                if s not in self.scenarios and s != "all":
                    errs.append(f"{p.id}: unknown scenario {s!r}")
        return errs

    def for_scenario(self, scenario: str) -> list[Parameter]:
        return [p for p in self.parameters.values() if scenario in p.scenarios or "all" in p.scenarios]

    def sample(self, rng: np.random.Generator, n: int) -> dict[str, np.ndarray]:
        return {pid: p.sample(rng, n) for pid, p in self.parameters.items()}

    def defaults(self) -> dict[str, float]:
        return {pid: float(p.default) for pid, p in self.parameters.items()}

    def explain(self, pid: str) -> str:
        p = self.parameters[pid]
        rng = "fixed" if p.distribution == "fixed" else f"{p.low} – {p.high} ({p.distribution})"
        lines = [
            f"# {p.label}",
            f"id: `{p.id}`   stage {p.stage}   scenarios: {', '.join(p.scenarios)}",
            f"default: **{p.default} {p.unit}**   range: {rng}   status: **{p.status}**",
            "",
            f"**Source.** {p.source}",
            "",
            f"**Why this value.** {p.justification}",
        ]
        if p.ri_calibration:
            lines += ["", f"**Rhode Island calibration.** {p.ri_calibration}"]
        if p.what_it_cannot_say:
            lines += ["", f"**What it cannot tell you.** {p.what_it_cannot_say}"]
        return "\n".join(lines)


def load(path=None) -> Ledger:
    raw = yaml.safe_load(open(path or LEDGER_PATH))
    scenarios = {k: Scenario(id=k, **v) for k, v in raw["scenarios"].items()}
    params = {}
    for k, v in raw["parameters"].items():
        v = dict(v)
        params[k] = Parameter(
            id=k,
            label=v["label"],
            scenarios=list(v["scenarios"]),
            stage=int(v.get("stage", 2)),
            unit=v.get("unit", ""),
            default=float(v["default"]),
            low=None if v.get("low") is None else float(v["low"]),
            high=None if v.get("high") is None else float(v["high"]),
            distribution=v.get("distribution", "triangular"),
            status=v["status"],
            source=v.get("source", ""),
            justification=v.get("justification", ""),
            ri_calibration=v.get("ri_calibration", ""),
            what_it_cannot_say=v.get("what_it_cannot_say", ""),
            sensitivity=bool(v.get("sensitivity", True)),
            tags=list(v.get("tags", [])),
        )
    ledger = Ledger(meta=raw.get("meta", {}), scenarios=scenarios, parameters=params)
    errs = ledger.validate()
    if errs:
        raise ValueError("assumptions.yaml is invalid:\n  " + "\n  ".join(errs))
    return ledger
