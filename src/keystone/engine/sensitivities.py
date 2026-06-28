"""PV01/PV02 by finite-difference bumping the SAME full-reval pricer.

Anchoring to the reference pricer (rather than a separate analytic formula) is
deliberate: it guarantees the delta-gamma approximation is a Taylor expansion of
*your* model, so reconciliation error reflects only truncation, not model drift.

Central difference:
    PV01 ~= (P(+h) - P(-h)) / (2h)          per 1bp
    PV02 ~= (P(+h) - 2P(0) + P(-h)) / h^2    per 1bp^2
with h = 1bp expressed in the bump unit.
"""
from __future__ import annotations

from keystone.domain.models import Instrument, MarketState
from keystone.domain.pricers import Pricer
from keystone.domain.units import PV01, PV02


def compute_pv01_pv02(
    pricer: Pricer, inst: Instrument, base: MarketState, h_bp: float = 1.0
) -> tuple[PV01, PV02]:
    p0 = pricer.price(inst, base)
    p_up = pricer.price(inst, base.bumped(+h_bp))
    p_dn = pricer.price(inst, base.bumped(-h_bp))
    pv01 = (p_up - p_dn) / (2.0 * h_bp)
    pv02 = (p_up - 2.0 * p0 + p_dn) / (h_bp * h_bp)
    return PV01(pv01), PV02(pv02)
