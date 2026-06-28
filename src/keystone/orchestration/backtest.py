"""HVaR backtest orchestrator — THIN, streams by date (bounded memory). Drives
the SAME core as the margin run. `mode` selects FullReval (reference) or
DeltaGamma (fast, only after reconciliation validates tail error). Yields one
result per date so the caller controls materialisation / writes to Parquet.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from keystone.engine.reval import FullReval, RevalMode
from keystone.engine.risk import MarginAddon, MarginResult, compute_margin
from keystone.engine.scenario_engine import portfolio_pnl_vector
from keystone.ports.data import CalendarSource, InstrumentSource, MarketDataSource


@dataclass(frozen=True, slots=True)
class BacktestPoint:
    as_of: str
    mode: str
    result: MarginResult


def run_backtest(
    instruments_src: InstrumentSource,
    market_src: MarketDataSource,
    calendar: CalendarSource,
    start: str,
    end: str,
    confidence: float,
    addons: list[MarginAddon],
    mode: RevalMode | None = None,
) -> Iterator[BacktestPoint]:
    mode = mode or FullReval()
    for as_of in calendar.backtest_dates(start, end):
        instruments = instruments_src.load_portfolio(as_of)
        base = market_src.base_state(as_of)
        scenarios = market_src.scenario_set(as_of)
        pnl = portfolio_pnl_vector(instruments, base, scenarios, mode)
        yield BacktestPoint(
            as_of=as_of, mode=mode.name,
            result=compute_margin(pnl, confidence, addons),
        )
