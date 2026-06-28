"""Daily margin run orchestrator — THIN. Loads one date, drives the shared core
in FullReval mode (production reference), applies add-ons, returns the margin
result. The backtest orchestrator drives the SAME core; they must never own
separate pricing logic.
"""
from __future__ import annotations

from keystone.engine.reval import FullReval
from keystone.engine.risk import MarginAddon, MarginResult, compute_margin
from keystone.engine.scenario_engine import portfolio_pnl_vector
from keystone.ports.data import InstrumentSource, MarketDataSource


def run_daily_margin(
    instruments_src: InstrumentSource,
    market_src: MarketDataSource,
    as_of: str,
    confidence: float,
    addons: list[MarginAddon],
) -> MarginResult:
    instruments = instruments_src.load_portfolio(as_of)
    base = market_src.base_state(as_of)
    scenarios = market_src.scenario_set(as_of)
    pnl = portfolio_pnl_vector(instruments, base, scenarios, FullReval())
    return compute_margin(pnl, confidence, addons)
