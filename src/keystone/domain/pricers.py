"""Pricer seam. THE critical performance decision lives here: a pricer prices
across a whole scenario batch and returns a P&L *vector*, using numpy — never a
Python loop over 2500 scenarios. Full reval and delta-gamma both satisfy the
same protocol, so the engine is agnostic to which is in use.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from keystone.domain.models import FloatArray, Instrument, MarketState, ScenarioSet
from keystone.domain.units import PV01, PV02


@runtime_checkable
class Pricer(Protocol):
    """Asset-specific. Implementations registered by product_type."""

    def price(self, inst: Instrument, mkt: MarketState) -> float:
        """Single full-reval PV at one market state (the reference price)."""
        ...

    def pnl_vector(
        self, inst: Instrument, base: MarketState, scenarios: ScenarioSet
    ) -> FloatArray:
        """P&L for every scenario, shape (n_scenarios,). Must be vectorised."""
        ...


@runtime_checkable
class Sensitivities(Protocol):
    """Optional capability: instruments whose pricer can supply PV01/PV02 enable
    delta-gamma mode. Computed by bumping the SAME full-reval pricer so the
    approximation is anchored to the reference model."""

    def pv01(self, inst: Instrument, base: MarketState) -> PV01: ...
    def pv02(self, inst: Instrument, base: MarketState) -> PV02: ...


PRICER_REGISTRY: dict[str, Pricer] = {}


def register_pricer(name: str) -> Callable[[type], type]:
    def deco(cls: type) -> type:
        impl = cls()
        if not isinstance(impl, Pricer):
            raise TypeError(f"{cls.__name__} does not satisfy Pricer protocol")
        if name in PRICER_REGISTRY:
            raise ValueError(f"pricer {name!r} already registered")
        PRICER_REGISTRY[name] = impl
        return cls

    return deco


def get_pricer(name: str) -> Pricer:
    try:
        return PRICER_REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"no pricer {name!r}; registered: {sorted(PRICER_REGISTRY)}"
        ) from None
