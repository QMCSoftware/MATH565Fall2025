"""
Analytic measures (provide exact kernel integrals) compatible with AnalyticalMeasure:

- k_mean(x, K): vector of E[k(x_i, Z)]
- k_self(K):   scalar E[k(Z, Z')]

Currently implemented:
- Uniform([0,1]^d) for the CENTERED discrepancy kernel:
    K(t, x) = ∏_j [ 1 + (γ_j^2/2)(|t_j-1/2| + |x_j-1/2| - |t_j - x_j|) ].

Closed-form expectations:
    μ(x)  = E_T[K(T,x)] = ∏_j [ 1 + (γ_j^2/2)(|x_j-1/2| + x_j - x_j^2 - 1/4) ],
    κ     = E[K(T,T')]  = ∏_j [ 1 + γ_j^2/12 ].
"""

from __future__ import annotations

from typing import Callable, Optional
import numpy as np

from .core import AnalyticalMeasure

__all__ = ["CDUniformMeasure", "cd_uniform_k_mean", "cd_uniform_k_self"]


# ---------------------------------------------------------------------------
# Class: Uniform([0,1]^d) for the centered discrepancy kernel
# ---------------------------------------------------------------------------
class CDUniformMeasure(AnalyticalMeasure):
    """
    Uniform([0,1]^d) analytic measure for the CENTERED discrepancy kernel.

    Parameters
    ----------
    d : int
        Dimension.
    gamma : float or array-like of shape (d,)
        Coordinate weights (scalar broadcasted to all coordinates is allowed).

    Notes
    -----
    This class supplies the exact expectations μ(x) and κ required by
    AnalyticalMeasure: k_mean(x, K) and k_self(K). The kernel K is not used
    inside these formulas, but is accepted to satisfy the interface.
    """

    def __init__(self, d: int, gamma):
        g = np.asarray(gamma, float)
        if g.ndim == 0:
            g = np.full(d, float(g))
        if g.size != d:
            raise ValueError(f"gamma must be scalar or length {d}, got {g.size}")
        self._g = g

        def _k_mean(X: np.ndarray, K_unused: Callable) -> np.ndarray:
            X = np.atleast_2d(np.asarray(X, float))  # (n, d)
            g2 = self._g ** 2
            # Per-dim factor: 1 + 0.5*γ_j^2 * ( |x_j-1/2| + x_j - x_j^2 - 1/4 )
            per = 1.0 + 0.5 * g2 * (np.abs(X - 0.5) + X - X**2 - 0.25)
            return np.prod(per, axis=1)  # (n,)

        def _k_self(K_unused: Callable) -> float:
            return float(np.prod(1.0 + (self._g ** 2) / 12.0))

        super().__init__(k_mean=_k_mean, k_self=_k_self)


# ---------------------------------------------------------------------------
# Optional factories: return callables matching AnalyticalMeasure's signature
# ---------------------------------------------------------------------------
def cd_uniform_k_mean(weights):
    """
    Factory returning k_mean(x, K) for Uniform([0,1]^d) under the centered discrepancy kernel.

    Parameters
    ----------
    weights : float or array-like of shape (d,)
        Coordinate weights (scalar allowed; broadcast happens at call time using x's d).

    Returns
    -------
    k_mean : Callable[[np.ndarray, Callable], np.ndarray]
        Function that maps (x, K) -> vector of μ(x_i).
    """
    w = np.asarray(weights, float).reshape(-1)

    def k_mean(x: np.ndarray, K_unused: Callable) -> np.ndarray:
        x = np.atleast_2d(np.asarray(x, float))   # (n, d)
        n, d = x.shape
        if w.size not in (1, d):
            raise ValueError(f"weights must be scalar or length d={d}; got {w.size}.")
        gam = np.full(d, float(w[0])) if w.size == 1 else w  # (d,)
        abs_center = np.abs(x - 0.5)
        poly = (x - x**2 - 0.25)
        per = 1.0 + 0.5 * (gam**2) * (abs_center + poly)     # (n, d) via broadcast
        return per.prod(axis=1)                               # (n,)

    return k_mean


def cd_uniform_k_self(weights, d: Optional[int] = None):
    """
    Factory returning k_self(K) for Uniform([0,1]^d) under the centered discrepancy kernel.

    Parameters
    ----------
    weights : float or array-like of shape (d,)
        Coordinate weights. If scalar, you MUST provide `d` (the dimension).
    d : int, optional
        Dimension (required if `weights` is scalar).

    Returns
    -------
    k_self : Callable[[Callable], float]
        Function that maps (K) -> κ.
    """
    w = np.asarray(weights, float).reshape(-1)
    if w.size == 1:
        if d is None:
            raise ValueError("cd_uniform_k_self: when weights is scalar, supply d to compute the d-fold product.")
        gam = np.full(d, float(w[0]))
    else:
        gam = w

    def k_self(K_unused: Callable) -> float:
        return float(np.prod(1.0 + (gam**2) / 12.0))

    return k_self