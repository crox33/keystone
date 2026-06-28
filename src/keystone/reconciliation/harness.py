"""Reconciliation harness — a FIRST-CLASS deliverable, not a test.

Two jobs:
  1. delta_gamma_error: measure approximation error of DeltaGamma vs FullReval
     across the scenario set, with explicit focus on the TAIL (where HVaR lives
     and where gamma approximation breaks down). If tail error exceeds tolerance,
     delta-gamma is NOT safe for that book — the whole point of the check.
  2. golden_master_diff: compare any computed margin against a frozen production
     figure within tolerance — your defence that the replacement matches prod.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from keystone.domain.models import Instrument, MarketState, ScenarioSet
from keystone.engine.reval import DeltaGamma, FullReval
from keystone.engine.risk import historical_var
from keystone.engine.scenario_engine import portfolio_pnl_vector


@dataclass(frozen=True, slots=True)
class ReconReport:
    max_abs_error: float
    rms_error: float
    tail_max_abs_error: float       # error within the loss tail only
    var_full: float
    var_dg: float
    var_rel_error: float
    within_tolerance: bool


def delta_gamma_error(
    instruments: list[Instrument],
    base: MarketState,
    scenarios: ScenarioSet,
    confidence: float,
    tail_pct: float = 0.05,
    var_tol: float = 0.01,
) -> ReconReport:
    """Compare DeltaGamma vs FullReval. `var_tol` is the max acceptable relative
    error on the headline VaR (e.g. 1%). Tail error is reported on the worst
    `tail_pct` of scenarios — the region that actually drives margin."""
    full = portfolio_pnl_vector(instruments, base, scenarios, FullReval())
    dg = portfolio_pnl_vector(instruments, base, scenarios, DeltaGamma())
    err = dg - full

    # tail = most negative full-reval P&L (largest losses)
    k = max(1, int(scenarios.n_scenarios * tail_pct))
    tail_idx = np.argsort(full)[:k]
    tail_err = err[tail_idx]

    var_full = historical_var(full, confidence)
    var_dg = historical_var(dg, confidence)
    rel = abs(var_dg - var_full) / var_full if var_full != 0 else float("inf")

    return ReconReport(
        max_abs_error=float(np.max(np.abs(err))),
        rms_error=float(np.sqrt(np.mean(err**2))),
        tail_max_abs_error=float(np.max(np.abs(tail_err))),
        var_full=var_full,
        var_dg=var_dg,
        var_rel_error=rel,
        within_tolerance=rel <= var_tol,
    )


def golden_master_diff(
    computed: float, production: float, tol_abs: float = 1e-6, tol_rel: float = 1e-4
) -> bool:
    """True if `computed` matches a frozen `production` figure within tolerance.
    Use per layer: one instrument, portfolio, each add-on, each backtest date."""
    if abs(computed - production) <= tol_abs:
        return True
    denom = abs(production) if production != 0 else 1.0
    return abs(computed - production) / denom <= tol_rel
