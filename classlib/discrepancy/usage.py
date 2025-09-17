"""
Notebook usage card so students see concise instructions (not raw source).
"""

__all__ = ["show_mmd_usage", "MMD_USAGE"]

MMD_USAGE = r"""
### MMD / Discrepancy Quick Guide

- **Kernel**: `"se"`/`"sqexp"` (squared exponential), `"matern"`, `"linear"`, or a callable `K(A,B)`.
  *We avoid the ambiguous name “RBF”; ‘radial basis function’ is more general.*
- **Domain**:
  - $\mathbb{R}^d$ (default): `kernel="se"` or `make_kernel("se", sigma)`
  - $[0,1]^d$ (strict): `K = make_kernel("se", sigma, domain="unit")` then `mmd(..., kernel=K)`
- **Estimator**:
  - `biased=True` (default): includes diagonals, always nonnegative.
  - `biased=False`: unbiased U-statistic (only when both sides are samples).
- **Analytic distribution**:
  - Wrap as `AnalyticalMeasure(k_mean, k_self)` providing exact integrals.
  - (Stubs for Uniform[0,1]^d are in `classlib.discrepancy.measures`.)

**Examples**
```python
from classlib.discrepancy import mmd, make_kernel, AnalyticalMeasure

# Sample vs sample on [0,1]^d with strict domain
K = make_kernel("se", sigma=0.25, domain="unit")
val = mmd(X, Y, kernel=K, biased=True, return_squared=True)

# Sample vs analytic measure (e.g., Uniform[0,1]^d with your CD kernel)
from classlib.discrepancy.measures import uniform_unit_cube_k_mean, uniform_unit_cube_k_self
U01 = AnalyticalMeasure(k_mean=uniform_unit_cube_k_mean(), k_self=uniform_unit_cube_k_self())
val2 = mmd(X, U01, kernel="se", sigma=0.25, biased=True)
```
"""

def show_mmd_usage() -> None:
    """Render a concise usage card in a notebook, or print if IPython is unavailable."""
    try:
        from IPython.display import display, Markdown  # type: ignore
        display(Markdown(MMD_USAGE))
    except Exception:
        print(MMD_USAGE)
