"""Ports: the seams where data lives. CSV now, Snowflake later — same protocol,
engine never knows which. Define them as if Snowflake already exists so no
flat-file assumption leaks into the core.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from keystone.domain.models import Instrument, MarketState, ScenarioSet


@runtime_checkable
class InstrumentSource(Protocol):
    def load_portfolio(self, as_of: str) -> list[Instrument]: ...


@runtime_checkable
class MarketDataSource(Protocol):
    def base_state(self, as_of: str) -> MarketState: ...
    def scenario_set(self, as_of: str) -> ScenarioSet: ...


@runtime_checkable
class CalendarSource(Protocol):
    def backtest_dates(self, start: str, end: str) -> list[str]: ...
