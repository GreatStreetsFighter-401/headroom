"""Out-of-sample check of the baseline: fit on 2018–2023, predict 2024–2025.

The baseline is the only part of the model with a time series to test it
against, so it is the part that gets an out-of-sample test. Both sides are
the Census series at its own level (no State-survey scaling), so the test
is of the trend-and-mean blend and the noise band, not of the undercount
ratio. Reported: mean absolute error, the statewide error, and how often
the observed value fell inside the P10–P90 band — which is what a reader
should check before trusting the bands on the forecast.
"""

from __future__ import annotations

import numpy as np

from headroom.ledger import Ledger
from headroom.model.core import _trend_forecast, level_noise


def hindcast(ledger: Ledger, towns: dict, *, fit_through: int = 2023, draws: int = 2000) -> dict:
    rng = np.random.default_rng(int(ledger.meta["seed"]))
    p = ledger.sample(rng, draws)
    recent_n = int(ledger.meta["baseline_recent_years"])
    rows = []
    abs_err, obs_sum, pred_sum, inside, n = 0.0, 0.0, 0.0, 0, 0
    for name, t in towns["towns"].items():
        hist = {int(k): v for k, v in t["permits_bps"].items()}
        fit_years = [y for y in sorted(hist) if y <= fit_through]
        test_years = [y for y in sorted(hist) if y > fit_through]
        if len(fit_years) < 3 or not test_years:
            continue
        trend, recent = _trend_forecast([hist[y] for y in fit_years], fit_years, test_years, recent_n)
        w = p["baseline_trend_weight"][:, None]
        expected = w * trend[None, :] + (1 - w) * recent
        pred = expected * level_noise(expected, p["baseline_noise_cv"], rng)
        p10, p50, p90 = np.percentile(pred, [10, 50, 90], axis=0)
        for i, y in enumerate(test_years):
            obs = hist[y]
            rows.append(
                {
                    "municipality": name,
                    "year": y,
                    "observed": obs,
                    "p10": round(float(p10[i]), 1),
                    "p50": round(float(p50[i]), 1),
                    "p90": round(float(p90[i]), 1),
                    "inside_band": bool(p10[i] <= obs <= p90[i]),
                }
            )
            abs_err += abs(float(p50[i]) - obs)
            obs_sum += obs
            pred_sum += float(p50[i])
            inside += int(p10[i] <= obs <= p90[i])
            n += 1
    return {
        "fit_through": fit_through,
        "test_years": sorted({r["year"] for r in rows}),
        "n_town_years": n,
        "mean_absolute_error_p50": round(abs_err / max(1, n), 1),
        "statewide_observed": obs_sum,
        "statewide_p50": round(pred_sum, 1),
        "statewide_error_pct": round(100 * (pred_sum - obs_sum) / max(1, obs_sum), 1),
        "share_inside_p10_p90": round(inside / max(1, n), 3),
        "rows": rows,
    }
