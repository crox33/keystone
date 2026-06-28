# Contributing to keystone

## Setup — use a virtual environment (required)

Keystone is **flat-file focused** and **Windows-first** (most users run Windows,
not Linux). Always work inside a per-clone `.venv`.

**Windows (PowerShell):**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

**macOS / Linux:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

`pip install -e ".[dev]"` installs keystone **editable** (so `import keystone`
works everywhere — IDE, terminal, tests — with no `PYTHONPATH` fiddling) plus the
dev tools. Point your IDE interpreter at `.venv`.

## Running scripts — no terminal needed

Open any script in **PyCharm** or **VSCode** and press ▶ / **Debug**:
- PyCharm: pick a config (`monthly_run`, `quarterly_run`, …) from the Run dropdown.
- VSCode: pick from the Run & Debug panel, or use **"Run current file"** on any
  open script (great for `scripts/playground/`).

Configs are committed (`.idea/runConfigurations/`, `.vscode/launch.json`). See
[scripts/README.md](scripts/README.md).

## Conventions that keep this repo healthy

- **Minimal dependencies.** Runtime deps are `numpy`, `polars`, `pydantic` only.
  Adding one needs a justification in the PR — prefer the stdlib. Dev tools live
  under the `dev` extra, never in runtime deps.
- **Cross-platform.** Use `pathlib.Path`, never hardcoded `/` or `\` paths or
  shell-specific calls. Code must run identically on Windows and Linux.
- **Polars + Parquet + Arrow**, never pandas. Raw numpy is fine for hot paths.
- **Constants live in `config/constants.json`**, loaded via `keystone.config`.
  No magic numbers in scripts.

## Quality gates (before opening a PR)
```
ruff check src tests
mypy src
pytest -q
```

## Pull requests
The default branch requires a green CI and **at least one approving review**
before merge (see [docs/branch-protection.md](docs/branch-protection.md)). Push a
branch, open a PR, get one reviewer — no direct pushes to the default branch.
