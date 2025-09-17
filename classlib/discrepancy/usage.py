"""
Notebook usage card so students see concise instructions (not raw source).
"""

__all__ = ["show_mmd_usage", "MMD_USAGE"]

MMD_USAGE = r"""
### MMD / Discrepancy Quick Guide

- **Kernels**:
  - `"se"` / `"sqexp"`: Squared Exponential kernel  
    *(sometimes called "RBF" in ML, but we avoid that ambiguous term).*
  - `"matern"`: Matérn family (ν = 0.5, 1.5, 2.5, or general with SciPy).  
  - `"linear"`: Linear kernel.  
  - `make_cd_kernel(weights)`: Centered discrepancy kernel on [0,1]^d with coordinate weights γ_j.

- **Domain**:
  - $\mathbb{R}^d$ (default): e.g. `kernel="se"` or `make_kernel("se", sigma)`
  - $[0,1]^d$ (strict): e.g. `K = make_kernel("se", sigma, domain="unit")`  
    or `K = make_cd_kernel(weights, domain="unit")`

- **Estimator**:
  - `biased=True` (default): includes diagonals, always nonnegative.
  - `biased=False`: unbiased U-statistic (only when both sides are samples).

- **Analytic distributions**:
  - Wrap as `AnalyticalMeasure(k_mean, k_self)` providing exact integrals.
  - For Uniform[0,1]^d with centered discrepancy:  
    ```python
    from classlib.discrepancy import cd_uniform_k_mean, cd_uniform_k_self, AnalyticalMeasure
    U01 = AnalyticalMeasure(k_mean=cd_uniform_k_mean(weights),
                            k_self=cd_uniform_k_self(weights))
    ```

**Examples**
```python
from classlib.discrepancy import (
    mmd, make_kernel, make_cd_kernel,
    AnalyticalMeasure, cd_uniform_k_mean, cd_uniform_k_self
)

# Sample vs sample on [0,1]^d with strict domain (squared exponential kernel)
K = make_kernel("se", sigma=0.25, domain="unit")
val = mmd(X, Y, kernel=K, biased=True, return_squared=True)

# Sample vs analytic Uniform[0,1]^d using centered discrepancy kernel
weights = 1.0   # or np.array([...]) for coordinate weights
K_cd = make_cd_kernel(weights, domain="unit")
U01 = AnalyticalMeasure(k_mean=cd_uniform_k_mean(weights),
                        k_self=cd_uniform_k_self(weights))
val2 = mmd(X, U01, kernel=K_cd, biased=True, return_squared=True)
```
"""

def show_mmd_usage() -> None:
    """Render a concise usage card in a notebook, or print if IPython is unavailable."""
    try:
        from IPython.display import display, Markdown  # type: ignore
        display(Markdown(MMD_USAGE))
    except Exception:
        print(MMD_USAGE)
