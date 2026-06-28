# keystone — project guide for Claude Code

Accuracy-first clearing margin & HVaR engine. This repo is the robust, immutable,
extensible **boilerplate** for three LSEG clearing services on one shared core:
**RepoClear**, **EquityClear**, and **CaLM** (Collateral & Liquidity Management).
Built to absorb new markets, new models, and new additional margins at the seams
without forking the core. Primary users: **quant risk analysts and managers**.

Flat-file focused (Parquet/CSV) now; Snowflake later behind the same ports.
Functionality also extends to the quant team's reporting and analysis needs
(e.g. periodic monthly sensitivities, procyclicality — change of IM over the
trailing 18 months).

## Priorities (non-negotiable order)
accuracy > extensibility-at-seams > readability > bounded memory. Speed comes
from vectorisation + streaming, never from compromising the above.

## Read first
- `.claude/skills/keystone-architecture/SKILL.md` — the conventions. Follow them.
- `.claude/skills/market-data-cleaning/SKILL.md` — for any ingestion/cleaning work.

## Layout
- `src/keystone/domain` — units, frozen models, pricer protocol + registry (PURE)
- `src/keystone/engine` — scenario engine, reval modes, sensitivities, risk/addons (PURE)
- `src/keystone/ports` — data-source Protocols
- `src/keystone/adapters` — CSV (Snowflake later) + asset pricers
- `src/keystone/orchestration` — thin margin-run and backtest drivers
- `src/keystone/reconciliation` — golden-master + delta-gamma error harness
- `src/keystone/config.py` — typed loader for `config/constants.json` (boundary; core never imports it)
- `config/` — JSON constants (single source; a change here is a model change)
- `scripts/periodic` — monthly/quarterly/yearly runs; `scripts/playground` — scratch

## Golden rules
- Margin run and backtest drive the SAME core. No duplicated pricing.
- Money = Decimal (`Cash`); market data = float64. Never mix.
- `pnl_vector` is vectorised across all scenarios; no per-scenario Python loops.
- Scale via vectorisation + multiprocessing, never Python loops.
- Dataframes = **Polars** (+ Arrow + Parquet), never pandas. Raw numpy arrays are
  fine for hot numeric paths.
- FullReval is the reference; DeltaGamma is a validated approximation only.
- A margin-affecting change is not done until reconciled within tolerance.
- Runtime deps stay minimal (numpy, polars, pydantic); justify any addition, dev tools go in the `[dev]` extra.
- Cross-platform (Windows-first): `pathlib` only, no shell-specific calls.
- Constants live in `config/constants.json` via `keystone.config`; no magic numbers in scripts.

## Local dev
- Work in a `.venv`; `pip install -e ".[dev]"` makes `keystone` importable everywhere. See `CONTRIBUTING.md`.
- Scripts are one-click runnable/debuggable in PyCharm & VSCode (committed run configs); no terminal needed.
- PRs to the default branch require 1 approving review. See `docs/branch-protection.md`.

## Quality gates (run before declaring done)
```
ruff check src tests
mypy src
pytest -q
```

## Subagents (delegate proactively)
- `code-reviewer` after non-trivial edits
- `test-writer` for new invariants / fixtures
- `reconciliation-checker` before merging margin-affecting changes
- `migration-engineer` when porting legacy library logic
- `documentor` when seams or methodology change
