"""Flat-file adapters (and in-memory doubles for tests). The CSV reader and a
future SnowflakeSource implement the same ports; swapping them touches no core
code. Demonstrated here with lightweight in-memory doubles so the skeleton runs
without sample files; the CSV variants show the real shape.
"""
from __future__ import annotations

import numpy as np
import polars as pl

from keystone.domain.models import Instrument, MarketState, ScenarioSet


class InMemoryInstrumentSource:
    def __init__(self, instruments: list[Instrument]) -> None:
        self._instruments = instruments

    def load_portfolio(self, as_of: str) -> list[Instrument]:
        return self._instruments


class InMemoryMarketDataSource:
    def __init__(self, base: MarketState, scenarios: ScenarioSet) -> None:
        self._base = base
        self._scenarios = scenarios

    def base_state(self, as_of: str) -> MarketState:
        return self._base

    def scenario_set(self, as_of: str) -> ScenarioSet:
        return self._scenarios


class CsvInstrumentSource:
    """Real shape: read instrument CSV(s) into validated Instrument models.
    Validation happens HERE (boundary), not in the engine."""

    def __init__(self, path: str) -> None:
        self._path = path

    def load_portfolio(self, as_of: str) -> list[Instrument]:
        df = pl.read_csv(self._path)
        return [Instrument(**row) for row in df.iter_rows(named=True)]


class CsvMarketDataSource:
    """Real shape: base curve CSV + a scenario shock CSV (n_scenarios x n_tenors,
    bp). Returns hot numpy-backed domain objects."""

    def __init__(self, curve_path: str, scenarios_path: str) -> None:
        self._curve_path = curve_path
        self._scenarios_path = scenarios_path

    def base_state(self, as_of: str) -> MarketState:
        df = pl.read_csv(self._curve_path)
        return MarketState(
            tenors=df["tenor"].to_numpy().astype(np.float64),
            zero_rates=df["zero_rate"].to_numpy().astype(np.float64),
        )

    def scenario_set(self, as_of: str) -> ScenarioSet:
        df = pl.read_csv(self._scenarios_path)
        return ScenarioSet(shocks_bp=df.to_numpy().astype(np.float64))
