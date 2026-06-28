from __future__ import annotations

import numpy as np

import keystone.adapters.repo_pricer  # noqa: F401  registers "repo"
from keystone.adapters.flat_file import (
    InMemoryInstrumentSource,
    InMemoryMarketDataSource,
)
from keystone.domain.models import Instrument, MarketState, ScenarioSet
from keystone.engine.reval import FullReval
from keystone.engine.risk import ProcyclicalityBuffer, compute_margin, historical_var
from keystone.engine.scenario_engine import portfolio_pnl_vector
from keystone.orchestration.margin_run import run_daily_margin
from keystone.reconciliation.harness import delta_gamma_error, golden_master_diff


def _fixture(n_scen: int = 2500):
    tenors = np.array([1.0, 2.0, 5.0, 10.0])
    rates = np.array([0.02, 0.025, 0.03, 0.035])
    base = MarketState(tenors=tenors, zero_rates=rates)
    rng = np.random.default_rng(42)
    shocks = rng.normal(0.0, 5.0, size=(n_scen, tenors.size))  # bp
    scenarios = ScenarioSet(shocks_bp=shocks)
    instruments = [
        Instrument(instrument_id="R1", product_type="repo", notional=1e7, maturity_years=2.0),
        Instrument(instrument_id="R2", product_type="repo", notional=5e6, maturity_years=5.0),
    ]
    return instruments, base, scenarios


def test_pnl_vector_shape() -> None:
    instruments, base, scenarios = _fixture()
    pnl = portfolio_pnl_vector(instruments, base, scenarios, FullReval())
    assert pnl.shape == (2500,)


def test_margin_with_addon() -> None:
    instruments, base, scenarios = _fixture()
    pnl = portfolio_pnl_vector(instruments, base, scenarios, FullReval())
    res = compute_margin(pnl, 0.997, [ProcyclicalityBuffer(0.25)])
    assert res.base_var > 0
    assert res.addons["apc_buffer"] == 0.25 * res.base_var
    assert res.total == res.base_var + res.addons["apc_buffer"]


def test_daily_margin_run() -> None:
    instruments, base, scenarios = _fixture()
    isrc = InMemoryInstrumentSource(instruments)
    msrc = InMemoryMarketDataSource(base, scenarios)
    res = run_daily_margin(isrc, msrc, "2024-01-02", 0.997, [ProcyclicalityBuffer()])
    assert res.total > res.base_var


def test_delta_gamma_close_to_full_in_tail() -> None:
    """For modest moves, delta-gamma should track full reval well — this is the
    validation the harness exists to perform."""
    instruments, base, scenarios = _fixture()
    report = delta_gamma_error(instruments, base, scenarios, 0.997, var_tol=0.05)
    assert report.var_rel_error < 0.05
    assert report.within_tolerance


def test_golden_master_diff() -> None:
    assert golden_master_diff(100.0, 100.0)
    assert golden_master_diff(100.0, 100.000001)
    assert not golden_master_diff(100.0, 110.0)


def test_var_positive() -> None:
    pnl = np.linspace(-100, 100, 1000)
    assert historical_var(pnl, 0.99) > 0
