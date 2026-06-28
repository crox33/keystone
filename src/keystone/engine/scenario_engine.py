"""Scenario engine — asset-agnostic heart. Assembles the portfolio P&L matrix
(instruments x scenarios) for a single date, then aggregates to a portfolio P&L
vector across scenarios. Streaming by date is the orchestrator's job; this holds
exactly one date's matrix.

Memory: O(n_instruments * n_scenarios) per date — never multiplied by dates.
"""
from __future__ import annotations

import numpy as np

from keystone.domain.models import FloatArray, Instrument, MarketState, ScenarioSet
from keystone.domain.pricers import get_pricer
from keystone.engine.reval import RevalMode


def portfolio_pnl_vector(
    instruments: list[Instrument],
    base: MarketState,
    scenarios: ScenarioSet,
    mode: RevalMode,
) -> FloatArray:
    """Sum instrument P&L vectors into a portfolio P&L vector, shape
    (n_scenarios,). Each instrument routed to its registered pricer; reval mode
    (full vs delta-gamma) selected by caller."""
    total = np.zeros(scenarios.n_scenarios, dtype=np.float64)
    for inst in instruments:
        pricer = get_pricer(inst.product_type)
        total += mode.pnl_vector(pricer, inst, base, scenarios)
    return total
