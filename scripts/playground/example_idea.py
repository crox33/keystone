"""Playground — scratch space to try ideas against the real engine.

Nothing here is production. Copy this file, hack freely, press ▶ / Debug (the
"Run current file" config works on any file here). Anything that proves out gets
promoted into src/keystone/ with tests + a reconciliation check.
"""
from __future__ import annotations

from keystone.config import load_constants
from keystone.engine.risk import ProcyclicalityBuffer
from keystone.orchestration.margin_run import run_daily_margin
from scripts._common import build_sources


def main() -> None:
    k = load_constants()
    instruments_src, market_src = build_sources(None)  # in-memory demo
    result = run_daily_margin(
        instruments_src, market_src, "2024-01-02", k.confidence,
        [ProcyclicalityBuffer(k.apc_buffer_weight)],
    )
    print(f"base VaR : {result.base_var:,.2f}")
    print(f"total    : {result.total:,.2f}")
    # ↑ Try things: tweak confidence, add an addon, swap reval mode, plot a vector.


if __name__ == "__main__":
    main()
