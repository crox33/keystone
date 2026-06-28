"""End-to-end demo: margin run + backtest + reconciliation.
Run: PYTHONPATH=src python demo.py
"""
from __future__ import annotations

import numpy as np

import keystone.adapters.repo_pricer  # noqa: F401  registers "repo"
from keystone.adapters.flat_file import (
    InMemoryInstrumentSource,
    InMemoryMarketDataSource,
)
from keystone.domain.models import Instrument, MarketState, ScenarioSet
from keystone.engine.risk import ProcyclicalityBuffer
from keystone.orchestration.margin_run import run_daily_margin
from keystone.reconciliation.harness import delta_gamma_error


class _Calendar:
    def backtest_dates(self, start: str, end: str) -> list[str]:
        return ["2024-01-02", "2024-01-03", "2024-01-04"]


def main() -> None:
    tenors = np.array([1.0, 2.0, 5.0, 10.0])
    rates = np.array([0.02, 0.025, 0.03, 0.035])
    base = MarketState(tenors=tenors, zero_rates=rates)
    rng = np.random.default_rng(7)
    scenarios = ScenarioSet(shocks_bp=rng.normal(0, 5, size=(2500, 4)))
    instruments = [
        Instrument(instrument_id="R1", product_type="repo", notional=1e7, maturity_years=2.0),
        Instrument(instrument_id="R2", product_type="repo", notional=5e6, maturity_years=5.0),
    ]
    isrc = InMemoryInstrumentSource(instruments)
    msrc = InMemoryMarketDataSource(base, scenarios)

    res = run_daily_margin(isrc, msrc, "2024-01-02", 0.997, [ProcyclicalityBuffer(0.25)])
    print("=== Daily margin run (full reval) ===")
    print(f"  base VaR  : {res.base_var:,.2f}")
    print(f"  APC buffer: {res.addons['apc_buffer']:,.2f}")
    print(f"  TOTAL     : {res.total:,.2f}")

    print("\n=== Delta-gamma vs full-reval reconciliation ===")
    rep = delta_gamma_error(instruments, base, scenarios, 0.997, var_tol=0.01)
    print(f"  VaR full      : {rep.var_full:,.2f}")
    print(f"  VaR delta-gamma: {rep.var_dg:,.2f}")
    print(f"  VaR rel error : {rep.var_rel_error:.4%}")
    print(f"  tail max error: {rep.tail_max_abs_error:,.2f}")
    print(f"  within tol    : {rep.within_tolerance}")


if __name__ == "__main__":
    main()
