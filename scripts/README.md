# scripts/

Runnable entry points. **No terminal required** — open any script in PyCharm or
VSCode and press the ▶ / Debug button (run/debug configs are committed in
`.idea/runConfigurations/` and `.vscode/launch.json`).

```
scripts/
  periodic/     monthly_run.py · quarterly_run.py · yearly_run.py
  playground/   throwaway scratch files to test ideas
  _common.py    shared source-builder + Parquet writer (keeps scripts thin)
```

## Running
- **IDE (preferred):** pick a config from the Run/Debug dropdown, or use
  "Run current file" on any open script. Breakpoints just work.
- **Terminal (optional):** from the repo root, e.g.
  `python -m scripts.periodic.monthly_run --as-of 2024-01-31`

Every script runs against a built-in **in-memory demo** when no `--data-dir` is
given, so they execute immediately with nothing wired. Pass `--data-dir` to use
real CSV flat files. Output is written under `output/` (git-ignored) as Parquet.

## Periodic vs playground
- **periodic/** — production cadence runs. Thin drivers over the shared core;
  period-specific analytics (quarterly sensitivities, yearly procyclicality) plug
  in at the marked extension points.
- **playground/** — scratch only. Promote anything that works into
  `src/keystone/` with tests + reconciliation; never import playground from src.
