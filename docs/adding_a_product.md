# Adding a new product (pricer)

Zero core edits. Steps:

1. Create `src/keystone/adapters/<product>_pricer.py`.
2. Implement a class with two methods and register it:

```python
import numpy as np
from typing import cast
from keystone.domain.models import FloatArray, Instrument, MarketState, ScenarioSet
from keystone.domain.pricers import register_pricer

@register_pricer("my_product")
class MyProductPricer:
    def price(self, inst: Instrument, mkt: MarketState) -> float:
        """Single reference full-reval PV at one market state."""
        ...

    def pnl_vector(
        self, inst: Instrument, base: MarketState, scenarios: ScenarioSet
    ) -> FloatArray:
        """P&L for ALL scenarios at once. Vectorise — no loop over scenarios."""
        ...
        return cast(FloatArray, result.astype(np.float64))
```

3. (Optional, enables delta-gamma) ensure the pricer is smooth enough that
   PV01/PV02 bumping is meaningful. Sensitivities are computed generically by
   `engine.sensitivities.compute_pv01_pv02` against your `price`.

4. Add tests (invoke `test-writer`): pnl_vector shape (n_scenarios,) float64;
   any product invariants; golden-master vs a known figure.

5. Reconcile (invoke `reconciliation-checker`) before using in a margin run.

The engine picks up the pricer automatically via `product_type` -> registry. No
engine or orchestrator change required.
