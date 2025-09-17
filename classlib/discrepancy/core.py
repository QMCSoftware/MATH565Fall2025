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

__all__ = ["mmd", "AnalyticalMeasure"]

class AnalyticalMeasure:
    """
    Wrap a probability measure using **exact** kernel integrals.

    k_mean(x, K): array (len(x),) with entries E_{Z~P}[k(x_i,Z)]
    k_self(K):   float            with value  E_{Z,Z'~P}[k(Z,Z')]

    If both sides are measures, you must provide a custom cross expectation
    (not implemented here to avoid silent approximations).
    """
    def __init__(self,
                 k_mean: Callable[[np.ndarray, Callable], np.ndarray],
                 k_self: Callable[[Callable], float]):
        self._k_mean = k_mean
        self._k_self = k_self

    def k_mean(self, x: np.ndarray, K: Callable) -> np.ndarray:
        x = np.atleast_2d(np.asarray(x, float))
        return np.asarray(self._k_mean(x, K), float).reshape(-1)

    def k_self(self, K: Callable) -> float:
        return float(self._k_self(K))

def mmd(X, Y, *, kernel: Any = "se", sigma: float = 1.0, nu: float = 1.5,
        biased: bool = True, return_squared: bool = False) -> float:
    """
    Maximum Mean Discrepancy allowing arrays (samples) OR AnalyticalMeasure.

    Parameters
    ----------
    X, Y : array-like (n,d)/(m,d) or AnalyticalMeasure
    kernel : {'sqexp','se','matern','linear'} or callable K(A,B)
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
    from .core import AnalyticalMeasure as AM  # local alias, avoids cycles

    X_is_meas = isinstance(X, AM)
    Y_is_meas = isinstance(Y, AM)

    if not X_is_meas:
        X = np.asarray(X, float)
        if X.ndim == 1: X = X[:, None]
    if not Y_is_meas:
        Y = np.asarray(Y, float)
        if Y.ndim == 1: Y = Y[:, None]

    K = _make_kernel(kernel, sigma, nu=nu)["K"]

    if not X_is_meas and not Y_is_meas:
        n, m = len(X), len(Y)
        Kxx = K(X, X); Kyy = K(Y, Y); Kxy = K(X, Y)
        if biased or n < 2 or m < 2:
            mmd2 = Kxx.mean() + Kyy.mean() - 2.0 * Kxy.mean()
        else:
            mmd2 = (
                (Kxx.sum() - np.trace(Kxx)) / (n * (n - 1)) +
                (Kyy.sum() - np.trace(Kyy)) / (m * (m - 1)) -
                2.0 * Kxy.mean()
            )

    elif not X_is_meas and Y_is_meas:
        n = len(X)
        Kxx = K(X, X)
        Kxx_term = Kxx.mean() if (biased or n < 2) else (Kxx.sum() - np.trace(Kxx)) / (n * (n - 1))
        kYY = Y.k_self(K)
        kYmean_over_x = Y.k_mean(X, K).mean()
        mmd2 = Kxx_term + kYY - 2.0 * kYmean_over_x

    elif X_is_meas and not Y_is_meas:
        m = len(Y)
        Kyy = K(Y, Y)
        Kyy_term = Kyy.mean() if (biased or m < 2) else (Kyy.sum() - np.trace(Kyy)) / (m * (m - 1))
        kXX = X.k_self(K)
        kXmean_over_y = X.k_mean(Y, K).mean()
        mmd2 = kXX + Kyy_term - 2.0 * kXmean_over_y

    else:
        raise NotImplementedError(
            "Analytic measure vs analytic measure requires a provided cross expectation E[k(X,Y)]."
        )

    return mmd2 if return_squared else np.sqrt(max(mmd2, 0.0))