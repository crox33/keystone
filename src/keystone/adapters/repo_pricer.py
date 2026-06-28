"""Example repo pricer. Demonstrates the vectorised contract: pnl_vector prices
all scenarios at once via numpy. Toy pricing (PV = notional * discount factor at
maturity) — replace with your real repo full-reval logic when you migrate the
existing library. The INTERFACE is what matters here, not the toy math.
"""
from __future__ import annotations

from typing import cast

import numpy as np

from keystone.domain.models import FloatArray, Instrument, MarketState, ScenarioSet
from keystone.domain.pricers import register_pricer


def _zero_at(mkt: MarketState, maturity: float) -> float:
    return float(np.interp(maturity, mkt.tenors, mkt.zero_rates))


@register_pricer("repo")
class RepoPricer:
    def price(self, inst: Instrument, mkt: MarketState) -> float:
        r = _zero_at(mkt, inst.maturity_years)
        df = float(np.exp(-r * inst.maturity_years))
        return inst.notional * df

    def pnl_vector(
        self, inst: Instrument, base: MarketState, scenarios: ScenarioSet
    ) -> FloatArray:
        base_pv = self.price(inst, base)
        # parallel-shift each scenario, vectorised across all scenarios at once
        shift = scenarios.shocks_bp.mean(axis=1) * 1e-4          # (n_scen,) in rate
        r0 = _zero_at(base, inst.maturity_years)
        r_shocked = r0 + shift                                    # (n_scen,)
        df_shocked = np.exp(-r_shocked * inst.maturity_years)     # (n_scen,)
        pv_shocked = inst.notional * df_shocked
        result = pv_shocked - base_pv
        return cast(FloatArray, result.astype(np.float64))
