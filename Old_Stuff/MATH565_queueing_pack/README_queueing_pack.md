
# Queueing Simulation Pack (MATH 565)

This folder adds a reusable module and a demo notebook:

- `classlib/queuesim.py` — event-based queueing simulators (BaseSim, SingleServerEU1, DriveThruBlocking, step_plot)
- `notebooks/queueing/queuesim_quick_start.ipynb` — minimal examples that import `queuesim`

## Drop-in steps

1. Copy `classlib/queuesim.py` into your repo (e.g., `<repo>/classlib/queuesim.py`).
2. Copy the notebook into `<repo>/notebooks/queueing/queuesim_quick_start.ipynb` (or any location you prefer).
3. Make sure your notebook's first code cell adds the repo root to `sys.path` **or** place `classlib/` on `PYTHONPATH`.

Example notebook bootstrap (first cell):

```python
import sys, os
# If this notebook lives at <repo>/notebooks/queueing/..., add repo root:
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from classlib.queuesim import A_Config, B_Config, SingleServerEU1, DriveThruBlocking, step_plot
```

Alternatively, set `PYTHONPATH` once for your environment to include the repo root.

