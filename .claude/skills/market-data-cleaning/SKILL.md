---
name: market-data-cleaning
description: Conventions for the upstream market-data cleaning stage in keystone — statistical outlier/stale detection, gap handling, and producing versioned, checksummed clean snapshots. Use when building or modifying any data-cleaning, validation, or market-data-ingestion code. Keeps cleaning OUT of the pricing core.
---

# market-data cleaning — bounded context

Cleaning is a SEPARATE upstream stage. The pricing/risk core consumes only
already-clean, immutable, versioned snapshots. Cleaning logic must never live in
or be called from `engine/`.

## Why separate
If cleaning thresholds (winsorisation, stale-quote rules) can change pricing
inputs implicitly, then "the VaR moved" becomes unattributable. Isolating
cleaning makes every margin number reproducible from a named data version.

## Pipeline shape
1. INGEST raw flat files (CSV) -> validate schema at the boundary (Pydantic
   strict; reject, don't coerce).
2. DETECT issues with explicit statistical tests, each independently togglable
   and logged:
   - stale quotes: unchanged value across N consecutive observations.
   - outliers / jumps: robust z-score on returns (median + MAD, not mean+std),
     flag |z| > k (k a documented parameter).
   - cross-sectional sanity: monotonicity / no-arbitrage checks on curves where
     applicable.
3. TREAT: flag-and-fill per a documented policy (e.g. forward-fill stale,
   interpolate gaps, winsorise extreme returns). Every treatment recorded.
4. EMIT a clean snapshot + MANIFEST: checksum of the clean data, the data
   version/as-of, parameters used, and a per-point flag log (what was changed and
   why).

## Hard rules
- Every detection/treatment decision is **quantifiable** — driven by an explicit
  statistical test with a documented threshold, never ad hoc judgement.
- Robust statistics (median/MAD) over mean/std for detection — risk data has fat
  tails and a single outlier poisons mean/std.
- Cleaning is deterministic given (raw input, parameter set, version). Same
  inputs -> identical snapshot + checksum.
- Never silently drop data. Flag, record, treat per policy.
- Output is IMMUTABLE. A re-clean produces a new version, never an in-place edit.
- The treatment parameters are themselves versioned config, reconcilable and
  reviewable — a parameter change is a model change.

## Interface to the core
The core reads snapshots through a `MarketDataSource` port keyed by data version.
The engine takes a version id; it never sees raw data or cleaning code. Emit
snapshots as Parquet (Polars/Arrow), never pandas.

Versioned, checksummed snapshots are also what make periodic reporting (monthly
sensitivities, procyclicality of IM) reproducible: each report cites the data
version it ran on.
