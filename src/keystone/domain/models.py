"""Boundary + core domain models. Pydantic for *boundary* validation (data
entering from CSV/Snowflake); plain frozen dataclasses + numpy arrays for the
*hot* in-engine objects where Pydantic overhead is unwanted.

Design note: MarketState carries curves as numpy arrays, not Decimals. Money is
Decimal; market data is float64. Scenarios are expressed as additive/relative
shocks applied to a base MarketState.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from pydantic import BaseModel, ConfigDict

FloatArray = npt.NDArray[np.float64]


class _Boundary(BaseModel):
    """External data crossing into the typed core: strict, immutable."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class Instrument(_Boundary):
    instrument_id: str
    product_type: str          # registry key: "repo", "bond", "equity"...
    notional: float
    # minimal repo-ish fields for the demo; real version richer
    maturity_years: float


@dataclass(frozen=True, slots=True)
class MarketState:
    """A single market snapshot. `tenors` are pillar points (years);
    `zero_rates` aligned zero rates. Hot path -> dataclass+arrays, not Pydantic.
    """
    tenors: FloatArray
    zero_rates: FloatArray

    def bumped(self, bp: float) -> MarketState:
        """Parallel shift of `bp` basis points. Used by PV01/PV02 bumping and
        by scenario application for the parallel component."""
        return MarketState(self.tenors, self.zero_rates + bp * 1e-4)


@dataclass(frozen=True, slots=True)
class ScenarioSet:
    """A batch of historical scenarios for HVaR. `shocks_bp` has shape
    (n_scenarios, n_tenors): per-scenario shift (bp) at each pillar. For repo
    HVaR this is typically 2500 scenarios (10y of daily moves)."""
    shocks_bp: FloatArray   # (n_scenarios, n_tenors)

    @property
    def n_scenarios(self) -> int:
        return int(self.shocks_bp.shape[0])
