"""Quarterly margin run.

One-click runnable from PyCharm/VSCode (▶ / Debug), or:
    python -m scripts.periodic.quarterly_run --as-of 2024-03-31

Same shared core as the monthly/yearly runs. Quarter-end is also the natural
cadence for sensitivity reporting — wire that at the marked extension point.
"""
from __future__ import annotations

import argparse

from keystone.config import load_constants
from keystone.engine.risk import ProcyclicalityBuffer
from keystone.orchestration.margin_run import run_daily_margin
from scripts._common import build_sources, write_parquet


def main() -> None:
    k = load_constants()
    parser = argparse.ArgumentParser(description="Quarterly margin run")
    parser.add_argument("--as-of", required=True, help="Quarter-end date, e.g. 2024-03-31")
    parser.add_argument("--data-dir", default=None, help="CSV flat-file dir (else demo)")
    parser.add_argument("--out", default="output/quarterly", help="Output dir for Parquet")
    args = parser.parse_args()

    instruments_src, market_src = build_sources(args.data_dir)
    result = run_daily_margin(
        instruments_src, market_src, args.as_of, k.confidence,
        [ProcyclicalityBuffer(k.apc_buffer_weight)],
    )
    # Extension point: emit quarter-end sensitivities here (same core, no new pricing).

    out = write_parquet(
        [{"as_of": args.as_of, "base_var": result.base_var, "total": result.total,
          **result.addons}],
        f"{args.out}/margin_{args.as_of}.parquet",
    )
    print(f"Quarterly run {args.as_of}: total margin {result.total:,.2f}  ->  {out}")


if __name__ == "__main__":
    main()
