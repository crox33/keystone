"""Risk measures and margin add-ons. Base HVaR + composable add-ons (each takes
the portfolio P&L distribution and returns an increment). Add-ons are individually
testable and individually reconcilable against production — the key to trusting a
replacement margin system.

Sign convention: P&L losses are negative; margin figures are positive loss
magnitudes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from keystone.domain.models import FloatArray


def historical_var(pnl: FloatArray, confidence: float) -> float:
    """HVaR at `confidence` (e.g. 0.997). Loss not exceeded with that prob,
    returned as a positive magnitude."""
    if pnl.size == 0:
        raise ValueError("empty pnl")
    q = float(np.quantile(pnl, 1.0 - confidence, method="lower"))
    return -q


def expected_shortfall(pnl: FloatArray, confidence: float) -> float:
    if pnl.size == 0:
        raise ValueError("empty pnl")
    threshold = np.quantile(pnl, 1.0 - confidence, method="lower")
    tail = pnl[pnl <= threshold]
    if tail.size == 0:
        return -float(threshold)
    return -float(tail.mean())


class MarginAddon(ABC):
    name: str

    @abstractmethod
    def increment(self, pnl: FloatArray, base_margin: float) -> float:
        """Additional margin on top of base, given the P&L distribution."""
        ...


class ProcyclicalityBuffer(MarginAddon):
    """EMIR-style anti-procyclicality buffer: hold an extra `buffer_pct` of base
    margin that can be drawn down in stress, dampening margin spikes. Simplest of
    the three EMIR APC tools; the floor and stress-weighting variants slot in the
    same way."""

    name = "apc_buffer"

    def __init__(self, buffer_pct: float = 0.25) -> None:
        if buffer_pct < 0:
            raise ValueError("buffer_pct must be >= 0")
        self.buffer_pct = buffer_pct

    def increment(self, pnl: FloatArray, base_margin: float) -> float:
        return self.buffer_pct * base_margin


@dataclass(frozen=True, slots=True)
class MarginResult:
    base_var: float
    addons: dict[str, float]

    @property
    def total(self) -> float:
        return self.base_var + sum(self.addons.values())


def compute_margin(
    pnl: FloatArray, confidence: float, addons: list[MarginAddon]
) -> MarginResult:
    base = historical_var(pnl, confidence)
    increments = {a.name: a.increment(pnl, base) for a in addons}
    return MarginResult(base_var=base, addons=increments)
