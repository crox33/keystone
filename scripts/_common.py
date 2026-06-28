"""Shared helpers that keep the run scripts thin and identical in shape.

`build_sources` returns real CSV flat-file sources when given a data dir, else a
small in-memory demo so any script runs / debugs out of the box with no data
wired. `write_parquet` is the single output path (Polars + Parquet, never pandas).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

import keystone.adapters.repo_pricer  # noqa: F401  side-effect: registers "repo"
from keystone.adapters.flat_file import (
    CsvInstrumentSource,
    CsvMarketDataSource,
    InMemoryInstrumentSource,
    InMemoryMarketDataSource,
)
from keystone.domain.models import Instrument, MarketState, ScenarioSet
from keystone.ports.data import InstrumentSource, MarketDataSource


def build_sources(data_dir: str | None) -> tuple[InstrumentSource, MarketDataSource]:
    """Real CSV sources under `data_dir`, or an in-memory demo when None."""
    if data_dir is not None:
        d = Path(data_dir)
        return (
            CsvInstrumentSource(str(d / "instruments.csv")),
            CsvMarketDataSource(str(d / "curve.csv"), str(d / "scenarios.csv")),
        )
    base = MarketState(
        tenors=np.array([1.0, 2.0, 5.0, 10.0]),
        zero_rates=np.array([0.02, 0.025, 0.03, 0.035]),
    )
    scenarios = ScenarioSet(shocks_bp=np.random.default_rng(7).normal(0, 5, size=(2500, 4)))
    instruments = [
        Instrument(instrument_id="R1", product_type="repo", notional=1e7, maturity_years=2.0),
        Instrument(instrument_id="R2", product_type="repo", notional=5e6, maturity_years=5.0),
    ]
    return InMemoryInstrumentSource(instruments), InMemoryMarketDataSource(base, scenarios)


def write_parquet(rows: list[dict[str, object]], out_path: str | Path) -> Path:
    """Write rows to Parquet, creating parent dirs. Returns the path written."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_parquet(out)
    return out
