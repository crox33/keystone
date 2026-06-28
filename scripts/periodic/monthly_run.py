"""Monthly margin run.

One-click runnable: open in PyCharm or VSCode and press the ▶ / Debug button —
no terminal needed. Or from the repo root:
    python -m scripts.periodic.monthly_run --as-of 2024-01-31

`--data-dir` points at real CSV flat files; omit it to run the in-memory demo so
you can step through with the debugger immediately.
"""
from __future__ import annotations

import argparse

from keystone.config import load_constants
from keystone.engine.risk import ProcyclicalityBuffer
from keystone.orchestration.margin_run import run_daily_margin
from scripts._common import build_sources, write_parquet


def main() -> None:
    k = load_constants()
    parser = argparse.ArgumentParser(description="Monthly margin run")
    parser.add_argument("--as-of", required=True, help="Month-end date, e.g. 2024-01-31")
    parser.add_argument("--data-dir", default=None, help="CSV flat-file dir (else demo)")
    parser.add_argument("--out", default="output/monthly", help="Output dir for Parquet")
    args = parser.parse_args()

    instruments_src, market_src = build_sources(args.data_dir)
    result = run_daily_margin(
        instruments_src, market_src, args.as_of, k.confidence,
        [ProcyclicalityBuffer(k.apc_buffer_weight)],
    )

    out = write_parquet(
        [{"as_of": args.as_of, "base_var": result.base_var, "total": result.total,
          **result.addons}],
        f"{args.out}/margin_{args.as_of}.parquet",
    )
    print(f"Monthly run {args.as_of}: total margin {result.total:,.2f}  ->  {out}")


if __name__ == "__main__":
    main()
