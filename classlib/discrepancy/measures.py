"""
Analytic measures (provide exact kernel integrals).

Implementations should return functions compatible with AnalyticalMeasure:
- k_mean(x, K): vector of E[k(x_i, Z)]
- k_self(K):   scalar E[k(Z,Z')]

Add: Uniform[0,1]^d with centered-discrepancy kernel, Gaussian on R^d, etc.
"""

from __future__ import annotations
from typing import Callable
import numpy as np

# Example template for Uniform([0,1]^d) with your centered discrepancy kernel.
# Replace the NotImplementedError with your 1998 formulas when ready.

def uniform_unit_cube_k_mean(weights=None):
    def k_mean(x: np.ndarray, K: Callable):
        # TODO: implement analytic E_U[k(x, U)] under your CD kernel
        raise NotImplementedError("uniform k_mean: add your centered-discrepancy formula here.")
    return k_mean

def uniform_unit_cube_k_self(weights=None):
    def k_self(K: Callable) -> float:
        # TODO: implement analytic E_{U,U'}[k(U,U')] under your CD kernel
        raise NotImplementedError("uniform k_self: add your centered-discrepancy formula here.")
    return k_self

# --- Uniform([0,1]^d) analytic integrals for the centered discrepancy kernel ---

def cd_uniform_k_mean(weights):
    """
    Return k_mean(x, K) for Uniform([0,1]^d) under the centered discrepancy kernel
    with coordinate weights 'weights'. This ignores K and uses the closed form.
    """
    w = np.asarray(weights, float).reshape(-1)
    def k_mean(x: np.ndarray, K_callable_unused):
        x = np.atleast_2d(np.asarray(x, float))
        n, d = x.shape
        if w.size not in (1, d):
            raise ValueError(f"weights must be scalar or length d={d}; got {w.size}.")
        gam = (np.repeat(w, d) if w.size == 1 else w)
        # 1D factor per coordinate and row
        # f_j(t_j) = 1 + 0.5*γ_j^2 * ( |t_j-1/2| - t_j^2 + t_j - 1/4 )
        abs_center = np.abs(x - 0.5)
        poly = (-x**2 + x - 0.25)
        factors = 1.0 + 0.5 * (gam**2) * (abs_center + poly)  # broadcast (n,d)
        return factors.prod(axis=1)
    return k_mean

def cd_uniform_k_self(weights):
    """
    Return k_self(K) for Uniform([0,1]^d) under centered discrepancy kernel
    with coordinate weights 'weights'. Ignores K and uses the closed form.
    """
    w = np.asarray(weights, float).reshape(-1)
    def k_self(K_callable_unused) -> float:
        if w.size == 0:
            return 1.0
        return float(np.prod(1.0 + (w**2)/12.0))
    return k_self