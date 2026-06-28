"""Typed application constants, loaded and validated from config/constants.json.

JSON (stdlib `json`) over YAML by design: zero extra dependencies (keeps the
runtime footprint minimal), universal tooling, and strict — no implicit typing.
Validated through Pydantic so a malformed or incomplete file fails loudly at
load instead of producing a silently wrong margin number.

BOUNDARY util: the pure core (`domain/`, `engine/`) must NEVER import this.
Orchestration and scripts load constants here and pass the values in.
"""
from __future__ import annotations

from functools import cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONSTANTS_PATH = _REPO_ROOT / "config" / "constants.json"


class ReconciliationTolerances(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    var_rel_tol: float
    tail_abs_tol: float


class Constants(BaseModel):
    """Immutable, fully-typed constants. `extra="forbid"` catches typo'd keys."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    confidence: float
    n_scenarios: int
    hvar_lookback_years: int
    procyclicality_window_months: int
    apc_buffer_weight: float
    reconciliation: ReconciliationTolerances


@cache
def load_constants(path: str | Path | None = None) -> Constants:
    """Load + validate constants. Cached; pass an explicit path for overrides."""
    p = Path(path) if path is not None else DEFAULT_CONSTANTS_PATH
    return Constants.model_validate_json(p.read_text(encoding="utf-8"))
