---
description: Architectural conventions and invariants for the keystone clearing-risk library — hexagonal seams, units discipline, vectorisation, the margin/backtest single-core rule. Apply when writing, reviewing, or extending keystone code.
applyTo: "src/keystone/**/*.py,scripts/**/*.py,tests/**/*.py"
---

# keystone architecture conventions

This repo is the immutable, extensible **boilerplate** for three LSEG clearing
services on one shared core — **RepoClear**, **EquityClear**, **CaLM**
(Collateral & Liquidity Management). Primary users are quant risk analysts and
managers. New markets, models, and additional margins must slot in at the seams
without forking the core.

Priority order, non-negotiable: **accuracy > extensibility-at-seams >
readability > bounded memory**. Speed is achieved via vectorisation + streaming,
not by sacrificing the above.

## Layering (hexagonal)
- `domain/` and `engine/` = the calculation core. PURE. No imports of adapters,
  no file/DB/network I/O. Unit-testable in isolation.
- `ports/` = Protocols describing data sources. No implementation.
- `adapters/` = I/O implementations (flat-file now, Snowflake later) and
  asset-specific pricers. Implement ports/protocols; never imported BY the core.
- `orchestration/` = thin drivers (margin run, backtest). Wire adapters -> core.
- `reconciliation/` = the accuracy gate (golden-master + delta-gamma error).

Rule: if core code needs to import an adapter, the abstraction is wrong — add a
port instead.

## The single-core rule
The daily margin run and the HVaR backtest MUST drive the same calculation core.
They differ only in orchestration (one date vs many) and reval mode. Never let
them grow separate pricing logic — that is how margin and backtest silently
diverge.

## Units discipline
- Money / PnL = `Cash` (NewType over Decimal). Exact.
- Market data (rates, shocks) = float64 (`Rate`, `BasisPoints`, numpy arrays).
- Never mix. Mixing is a type error by construction; keep it that way.

## Extension seams
- New product = a Pricer registered via `@register_pricer`. Must implement BOTH
  `price` (single reference PV) and `pnl_vector` (vectorised across scenarios).
- New margin add-on = subclass `MarginAddon` (ABC), implement `increment`.
- New data source = implement the relevant port; drop it in `adapters/`.
- New service (RepoClear / EquityClear / CaLM) = compose the same core via
  orchestration + adapters; do not fork engine/ or domain/.
- Reporting/analysis (e.g. monthly sensitivities, procyclicality — IM change over
  the trailing 18 months) consumes engine outputs; it is a thin layer over the
  core, never new pricing logic.

## Data stack
- Dataframes = **Polars**; storage/interchange = **Parquet + Arrow**. Do NOT use
  pandas. Raw **numpy** arrays are fine for hot numeric paths.
- Flat-file focused now; Snowflake later behind the same ports.

## Vectorisation rule
`pnl_vector` MUST price all scenarios in numpy array ops — never a Python loop
over the (e.g. 2500) scenarios. The engine sums instrument vectors; do not loop
scenarios at the engine level either. Scale with vectorisation +
multiprocessing, never Python loops.

## Reval modes
- `FullReval` is the reference and what the margin run uses.
- `DeltaGamma` (PV01/PV02 Taylor) is a speed approximation for backtesting,
  valid ONLY for books where the reconciliation harness shows tail/VaR error
  within tolerance. Never make delta-gamma the reference.

## Memory
Stream the backtest by date. Hold at most one date's
(instruments x scenarios) matrix in memory; write results to Parquet and move on.

## Definition of done for any core change
ruff clean, `mypy --strict` clean, property test(s) for new invariants, and a
reconciliation result if a margin number is touched.
