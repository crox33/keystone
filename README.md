# keystone

Accuracy-first clearing margin & HVaR engine. RepoClear today, EquityClear-ready.
Flat-file (CSV) data now; Snowflake later behind the same ports. Functionality will also extend to quant team's needs for reporting and analysis.

## What it does
- **Daily margin run**: full-revaluation HVaR + composable add-ons (e.g. APC
  procyclicality buffer), one date.
- **10y HVaR backtest**: same core over many dates, 2500 scenarios/date, streamed
  by date for bounded memory.
- **Delta-gamma mode**: PV01/PV02 Taylor approximation for backtest speed —
  gated by a reconciliation harness that measures tail error vs full reval.
- **Reconciliation**: golden-master diff vs production + delta-gamma error report.

## One core, two orchestrators
The margin run and the backtest drive the *same* asset-agnostic scenario engine.
Products plug in via a registry; risk add-ons via an ABC. EquityClear adds
pricers and risk factors, not a new engine.

## Quickstart
```bash
pip install -e .              # numpy, polars, pydantic
PYTHONPATH=src python demo.py # margin run + reconciliation
PYTHONPATH=src pytest -q
mypy src && ruff check src
```

## Architecture
Hexagonal (ports & adapters). See `.claude/skills/keystone-architecture/SKILL.md`
for the full conventions and `CLAUDE.md` for the working guide. Extension recipes
in `docs/`.

Data flows top-to-bottom: thin orchestrators drive one shared calculation core,
which reaches data only through ports. Asset pricers and the data layer are the
two extension seams (EquityClear adds pricers, Snowflake adds an adapter — the
core is untouched in both cases).

```
                    ORCHESTRATORS (thin)
        ┌───────────────────┐      ┌────────────────────────┐
        │  Daily Margin Run │      │  HVaR Backtest (10yr)  │
        │  one date · addons│      │  N dates × 2500 scen.  │
        │  · reporting      │      │  streamed by date      │
        └─────────┬─────────┘      └───────────┬────────────┘
                  │       both drive the same  │
                  └───────────────┬────────────┘
                                  ▼
        ┌─────────────────────────────────────────────────────┐
        │           CALCULATION CORE  (asset-agnostic, PURE)   │
        │  scenario_engine  · portfolio P&L vector / scenario  │
        │  reval modes      · FullReval (ref) | DeltaGamma     │
        │  sensitivities    · PV01 / PV02 (bump full-reval)    │
        │  risk + add-ons   · HVaR/ES · APC buffer (composable)│
        └──────┬───────────────────────────────────┬──────────┘
               │ Pricer protocol (registry)         │ reads via ports
        ┌──────▼───────────┐             ┌──────────▼───────────────┐
        │ ASSET PRICERS     │            │  DATA LAYER (ports)      │
        │ repo (now)        │            │  InstrumentSource        │
        │ equity (later)    │            │  MarketDataSource        │
        │  ↑ vectorised     │            │  CalendarSource          │
        │  pnl_vector       │            │      ▲ implemented by    │
        └───────────────────┘            │  ┌───┴──────────────────┐│
                                         │  │ ADAPTERS             ││
                                         │  │ flat-file/CSV (now)  ││
        ┌────────────────────────────┐   │  │ Snowflake (later)    ││
        │  RECONCILIATION (gate)     │   │  └──────────────────────┘│
        │  golden-master vs prod     │   └──────────────────────────┘
        │  delta-gamma tail error    │
        └────────────────────────────┘   upstream: MarketDataCleaning
                                          → versioned, checksummed snapshots
```

## Layout
```
src/keystone/
  domain/         units (Cash/Rate/PV01/PV02), frozen models, pricer registry
  engine/         scenario engine, reval modes, sensitivities, risk + add-ons
  ports/          data-source Protocols (CSV now, Snowflake later)
  adapters/       flat-file sources + repo pricer
  orchestration/  margin_run, backtest (thin)
  reconciliation/ delta-gamma error + golden-master harness
.claude/
  agents/         code-reviewer, test-writer, documentor,
                  reconciliation-checker, migration-engineer
  skills/         keystone-architecture, market-data-cleaning
```
