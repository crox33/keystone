"""RevalMode: how an instrument's P&L vector across scenarios is produced.

Two implementations behind one interface:
  • FullReval     — reference. Calls the pricer per scenario batch (vectorised).
  • DeltaGamma     — approximation. PnL ~= PV01*dy + 0.5*PV02*dy^2, all 2500
                     scenarios in two array ops. Fast; MUST be validated against
                     FullReval via the reconciliation harness before trusting it
                     in the tail.

The engine selects a mode; the margin run uses FullReval (production reference),
the backtest may use DeltaGamma for speed once reconciled within tolerance.
"""
from __future__ import annotations

from typing import Protocol, cast

import numpy as np

from keystone.domain.models import FloatArray, Instrument, MarketState, ScenarioSet
from keystone.domain.pricers import Pricer
from keystone.engine.sensitivities import compute_pv01_pv02


class RevalMode(Protocol):
    name: str

    def pnl_vector(
        self,
        pricer: Pricer,
        inst: Instrument,
        base: MarketState,
        scenarios: ScenarioSet,
    ) -> FloatArray: ...


class FullReval:
    name = "full_reval"

    def pnl_vector(
        self,
        pricer: Pricer,
        inst: Instrument,
        base: MarketState,
        scenarios: ScenarioSet,
    ) -> FloatArray:
        # Delegate to the pricer's vectorised batch pricing (the reference path).
        return pricer.pnl_vector(inst, base, scenarios)


class DeltaGamma:
    """Taylor delta-gamma. Uses the parallel component of each scenario shock as
    `dy` (in bp). For a full multi-tenor treatment you'd carry a PV01 vector per
    pillar; this demo uses a single parallel PV01/PV02, which is the standard
    first cut and exactly what reconciliation will stress-test."""

    name = "delta_gamma"

    def pnl_vector(
        self,
        pricer: Pricer,
        inst: Instrument,
        base: MarketState,
        scenarios: ScenarioSet,
    ) -> FloatArray:
        pv01, pv02 = compute_pv01_pv02(pricer, inst, base)
        # parallel shock per scenario = mean shift across tenors (bp)
        dy = scenarios.shocks_bp.mean(axis=1)            # (n_scenarios,)
        result = pv01 * dy + 0.5 * pv02 * dy * dy
        return cast(FloatArray, result.astype(np.float64))
