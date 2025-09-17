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