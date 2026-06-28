"""Semantic units. Zero runtime cost; mypy treats them as distinct, so a
rate cannot be passed where cash is expected. Highest-leverage accuracy guard.
"""
from __future__ import annotations

from decimal import Decimal
from typing import NewType

Cash = NewType("Cash", Decimal)          # money / PnL — exact
Rate = NewType("Rate", float)            # market data — float64
BasisPoints = NewType("BasisPoints", float)
PV01 = NewType("PV01", float)            # dPV per 1bp parallel shift
PV02 = NewType("PV02", float)            # d2PV per 1bp^2 (convexity)


def cash(x: str | int | Decimal) -> Cash:
    return Cash(Decimal(x))
