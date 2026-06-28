# config/

Constants live in **`constants.json`** and are loaded + validated by
[`keystone.config`](../src/keystone/config.py) into a frozen, typed `Constants`
object.

**Why JSON, not YAML:** JSON parses with the stdlib (no extra dependency — see
the minimal-deps rule), is strict, and is universally tooled. Pydantic gives the
type-safety and comments-as-keys that JSON lacks. (If we ever outgrow flat
constants, TOML — also stdlib via `tomllib` — is the next step, not YAML.)

## Rules
- Add a key here **and** a typed field in `Constants` — `extra="forbid"` rejects
  unknown keys, so they must stay in sync.
- These are model/methodology parameters: a change here is a **model change** —
  review it and reconcile margin-affecting edits.
- The pure core never reads this file; orchestration/scripts pass values in.
