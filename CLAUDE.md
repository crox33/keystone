# keystone — project guide for Claude Code

Accuracy-first clearing margin & HVaR engine for RepoClear, designed to extend to
EquityClear. Flat-file (CSV) data now; Snowflake later behind the same ports.

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

## Golden rules
- Margin run and backtest drive the SAME core. No duplicated pricing.
- Money = Decimal (`Cash`); market data = float64. Never mix.
- `pnl_vector` is vectorised across all scenarios; no per-scenario Python loops.
- FullReval is the reference; DeltaGamma is a validated approximation only.
- A margin-affecting change is not done until reconciled within tolerance.

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
