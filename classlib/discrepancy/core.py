"""
Core MMD / Discrepancy engine.

- Accepts either/both sides as finite samples OR an AnalyticalMeasure that
  supplies exact integrals: k_mean(x, K) and k_self(K).
- Estimators:
  * biased=True (default): includes diagonals; always ≥ 0.
  * biased=False: unbiased U-statistic (only when BOTH sides are samples).
- Kernels:
  * Use names "sqexp"/"se" (squared exponential), "matern", "linear", or pass a callable K(A,B).
    NOTE: We avoid the ambiguous name “RBF” (radial basis function is broader).
"""

from __future__ import annotations

from typing import Callable, Any
import numpy as np

from .kernels import _make_kernel  # internal factory

__all__ = ["mmd", "mmd_prefix_against_measure", "AnalyticalMeasure"]


# ---------------------------------------------------------------------------
# Analytical measure adapter (UNIFIED — used by both mmd() and prefix variant)
# ---------------------------------------------------------------------------
class AnalyticalMeasure:
    """
    Wrap a probability measure using **exact** kernel integrals.

    Parameters
    ----------
    k_mean : callable
        k_mean(x, K) -> array (len(x),) with entries E_{Z~P}[k(x_i, Z)].
        - x : (n,d) array (will be np.atleast_2d)
        - K : kernel callable used for compatibility (can be ignored if not needed)

    k_self : callable
        k_self(K) -> float with value E_{Z,Z'~P}[k(Z, Z')].

    Notes
    -----
    If both sides are measures, a cross expectation E[k(X, Y)] is required
    (not implemented here to avoid silent approximations).
    """

    def __init__(
        self,
        k_mean: Callable[[np.ndarray, Callable], np.ndarray],
        k_self: Callable[[Callable], float],
    ):
        self._k_mean = k_mean
        self._k_self = k_self

    def k_mean(self, x: np.ndarray, K: Callable) -> np.ndarray:
        x = np.atleast_2d(np.asarray(x, float))
        out = self._k_mean(x, K)
        return np.asarray(out, float).reshape(-1)

    def k_self(self, K: Callable) -> float:
        return float(self._k_self(K))


# ---------------------------------------------------------------------------
# MMD (works for samples, sample-vs-measure, measure-vs-sample)
# ---------------------------------------------------------------------------
def mmd(
    X,
    Y,
    *,
    kernel: Any = "se",
    sigma: float = 1.0,
    nu: float = 1.5,
    biased: bool = True,
    return_squared: bool = False,
) -> float:
    """
    Maximum Mean Discrepancy allowing arrays (samples) OR AnalyticalMeasure.

    Parameters
    ----------
    X, Y : array-like (n,d)/(m,d) or AnalyticalMeasure
    kernel : {'sqexp','se','matern','linear'} or callable K(A,B)
        - If a string, a batched kernel K(A,B) returning a (len(A), len(B)) Gram matrix.
        - If a callable, it may be batched (matrix) or pointwise (scalar).
    sigma : float   (length-scale for sqexp/matern; ignored for linear/callable)
    nu    : float   (Matérn smoothness if kernel='matern')
    biased : bool   (True=biased includes diagonals; False=unbiased U-statistic
                     only when both sides are samples)
    return_squared : bool  (True → MMD^2; False → sqrt(max(MMD^2,0)))

    Notes
    -----
    - “sqexp”/“se” denotes the Squared Exponential kernel
      k(x,y) = exp(-||x-y||^2/(2 sigma^2)). Some ML sources call this “RBF”,
      but we avoid that term because many radial kernels exist.
    - If either side is an AnalyticalMeasure, its exact integrals are used.
      ‘unbiased’ then only applies to any sample side.
    - Measure-vs-measure (both analytic) cross term is not provided here.
    """
    AM = AnalyticalMeasure  # alias for isinstance checks

    X_is_meas = isinstance(X, AM)
    Y_is_meas = isinstance(Y, AM)

    # Normalize arrays
    if not X_is_meas:
        X = np.asarray(X, float)
        if X.ndim == 1:
            X = X[:, None]
    if not Y_is_meas:
        Y = np.asarray(Y, float)
        if Y.ndim == 1:
            Y = Y[:, None]

    # Kernel factory: if string, build batched K(A,B); if callable, use as-is
    if isinstance(kernel, str):
        K = _make_kernel(kernel, sigma, nu=nu)["K"]
    else:
        K = kernel

    # ---- both samples
    if not X_is_meas and not Y_is_meas:
        n, m = len(X), len(Y)
        Kxx = K(X, X)
        Kyy = K(Y, Y)
        Kxy = K(X, Y)
        if biased or n < 2 or m < 2:
            mmd2 = Kxx.mean() + Kyy.mean() - 2.0 * Kxy.mean()
        else:
            mmd2 = (
                (Kxx.sum() - np.trace(Kxx)) / (n * (n - 1))
                + (Kyy.sum() - np.trace(Kyy)) / (m * (m - 1))
                - 2.0 * Kxy.mean()
            )

    # ---- sample vs measure
    elif not X_is_meas and Y_is_meas:
        n = len(X)
        Kxx = K(X, X)
        Kxx_term = (
            Kxx.mean()
            if (biased or n < 2)
            else (Kxx.sum() - np.trace(Kxx)) / (n * (n - 1))
        )
        kYY = Y.k_self(K)
        kY_mean_over_x = Y.k_mean(X, K).mean()
        mmd2 = Kxx_term + kYY - 2.0 * kY_mean_over_x

    # ---- measure vs sample
    elif X_is_meas and not Y_is_meas:
        m = len(Y)
        Kyy = K(Y, Y)
        Kyy_term = (
            Kyy.mean()
            if (biased or m < 2)
            else (Kyy.sum() - np.trace(Kyy)) / (m * (m - 1))
        )
        kXX = X.k_self(K)
        kX_mean_over_y = X.k_mean(Y, K).mean()
        mmd2 = kXX + Kyy_term - 2.0 * kX_mean_over_y

    else:
        raise NotImplementedError(
            "Analytic measure vs analytic measure requires a provided cross expectation E[k(X,Y)]."
        )

    return mmd2 if return_squared else np.sqrt(max(mmd2, 0.0))


# ---------------------------------------------------------------------------
# Prefix MMD^2 for sample vs analytical measure: k = 1..n
# ---------------------------------------------------------------------------
def mmd_prefix_against_measure(
    X: np.ndarray,
    kernel: Callable[[np.ndarray, np.ndarray], float]
    | Callable[[np.ndarray, np.ndarray], np.ndarray],
    measure: AnalyticalMeasure,
    return_sqrt: bool = False,
) -> np.ndarray:
    """
    Compute prefix MMD^2 between the empirical sample X[0:k] and a continuous
    distribution P for k = 1..n, using:

        MMD^2 = (1/k^2) * sum_{i,j<=k} k(x_i,x_j)
                - (2/k)   * sum_{i<=k} E[k(x_i, Z)]
                + E[k(Z,Z')]

    Parameters
    ----------
    X : (n, d) array of sample points
    kernel : callable
        May be batched (returns Gram matrices) or pointwise (returns scalars).
    measure : AnalyticalMeasure
        Provides exact expectations via k_mean(x, K) and k_self(K).
    return_sqrt : bool, default False
        If True, return prefix MMD (sqrt); else MMD^2.

    Returns
    -------
    mmd_prefix : (n,) array
        Prefix MMD^2 (or MMD if return_sqrt=True) for k=1..n.
    """
    X = np.atleast_2d(np.asarray(X, float))
    n = X.shape[0]

    # Adapt kernel to a scalar evaluator (works whether kernel is batched or scalar)
    def _k_scalar(a: np.ndarray, b: np.ndarray) -> float:
        A = np.atleast_2d(a)
        B = np.atleast_2d(b)
        val = kernel(A, B)
        arr = np.asarray(val)
        if arr.ndim == 0:
            return float(arr)
        # expect (1,1) for scalar pairs when batched
        return float(arr.reshape(-1)[0])

    # Exact expectations with THIS kernel
    mu_vals = measure.k_mean(X, kernel)  # shape (n,)
    cumsum_mu = np.cumsum(mu_vals)

    # Stream S_k = sum_{i<=k}\sum_{j<=k} k(x_i, x_j)
    S = np.zeros(n, dtype=float)
    for k in range(n):
        if k == 0:
            S[k] = _k_scalar(X[0], X[0])
        else:
            xk = X[k]
            cross = 0.0
            for i in range(k):
                cross += _k_scalar(X[i], xk)
            S[k] = S[k - 1] + 2.0 * cross + _k_scalar(xk, xk)

    kappa = measure.k_self(kernel)

    ks = np.arange(1, n + 1, dtype=float)
    mmd2_prefix = (S / (ks**2)) - (2.0 * cumsum_mu / ks) + kappa

    if return_sqrt:
        return np.sqrt(np.clip(mmd2_prefix, 0.0, None))
    return mmd2_prefix