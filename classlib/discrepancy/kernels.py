"""
Kernel builders and helpers.

Public:
- make_kernel(kernel="se", sigma=1.0, nu=1.5, domain=None)
- restrict_to_unit_cube(K)

Internal:
- _make_kernel(name_or_callable, sigma, nu)
"""

from __future__ import annotations
from typing import Callable, Any
import numpy as np

__all__ = ["make_kernel", "restrict_to_unit_cube", "_make_kernel"]

# ------- core math helpers -------

def _pairwise_sq_dists(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    A = np.atleast_2d(np.asarray(A, float))
    B = np.atleast_2d(np.asarray(B, float))
    A2 = np.sum(A*A, axis=1, keepdims=True)
    B2 = np.sum(B*B, axis=1, keepdims=True).T
    return A2 + B2 - 2.0 * (A @ B.T)

# ------- kernel factories -------

def _make_kernel(name_or_callable: Any, sigma: float, nu: float = 1.5) -> dict:
    """
    Return {'K': K} where K(A,B)->Gram(n,m).
    name_or_callable ∈ {"sqexp","se","matern","linear"} or a callable.
    """
    if callable(name_or_callable):
        return {"K": name_or_callable}

    name = (name_or_callable or "sqexp").lower()

    if name in ("sqexp", "se"):  # squared exponential
        two_sig2 = 2.0 * (sigma * sigma)
        def K(A, B):
            return np.exp(-_pairwise_sq_dists(A, B) / two_sig2)
        return {"K": K}

    if name == "matern":
        def K(A, B):
            D2 = _pairwise_sq_dists(A, B)
            r = np.sqrt(np.maximum(D2, 0.0))
            ell = float(sigma)
            if np.isclose(nu, 0.5):  # exponential
                return np.exp(-r / ell)
            elif np.isclose(nu, 1.5):  # ν=3/2
                s = np.sqrt(3.0) * r / ell
                return (1.0 + s) * np.exp(-s)
            elif np.isclose(nu, 2.5):  # ν=5/2
                s = np.sqrt(5.0) * r / ell
                return (1.0 + s + (5.0 * r * r) / (3.0 * ell * ell)) * np.exp(-s)
            else:
                from scipy.special import kv, gamma  # general ν
                s = np.sqrt(2.0 * nu) * r / ell
                out = np.empty_like(s)
                mask = s > 0
                c = (2.0**(1.0 - nu)) / gamma(nu)
                out[mask] = c * (s[mask]**nu) * kv(nu, s[mask]); out[~mask] = 1.0
                return out
        return {"K": K}

    if name == "linear":
        return {"K": (lambda A, B: np.atleast_2d(A) @ np.atleast_2d(B).T)}

    raise ValueError("Unknown kernel. Use 'sqexp','se','matern','linear', or a callable.")

# ------- domain enforcement for [0,1]^d -------

def _in_unit_cube(A: np.ndarray) -> bool:
    A = np.asarray(A, float)
    return np.all((A >= 0.0) & (A <= 1.0))

def restrict_to_unit_cube(K: Callable[[np.ndarray, np.ndarray], np.ndarray]):
    """
    Wrap a kernel K(A,B) so it raises ValueError if any row of A or B lies
    outside [0,1]^d. (Strict domain enforcement.)
    """
    def K_restricted(A, B):
        A = np.atleast_2d(np.asarray(A, float))
        B = np.atleast_2d(np.asarray(B, float))
        if not _in_unit_cube(A):
            bad_i = np.where(~((A >= 0.0) & (A <= 1.0)).all(axis=1))[0][0]
            raise ValueError(f"Kernel domain violation: A[{bad_i}]={A[bad_i]} not in [0,1]^d.")
        if not _in_unit_cube(B):
            bad_j = np.where(~((B >= 0.0) & (B <= 1.0)).all(axis=1))[0][0]
            raise ValueError(f"Kernel domain violation: B[{bad_j}]={B[bad_j]} not in [0,1]^d.")
        return K(A, B)
    return K_restricted

def make_kernel(kernel: Any = "se", sigma: float = 1.0, nu: float = 1.5, domain: str | None = None):
    """
    Build a kernel callable for passing to mmd(..., kernel=<callable>).

    domain:
      None    → no domain check (R^d).
      "unit"  → strictly enforce inputs in [0,1]^d (raise if violated).
    """
    K = _make_kernel(kernel, sigma, nu=nu)["K"]
    if domain == "unit":
        K = restrict_to_unit_cube(K)
    return K

# --- Centered Discrepancy kernel (product form on [0,1]^d) ---

def _cd_term_1d(a: np.ndarray, b: np.ndarray, g: float) -> np.ndarray:
    """Return the 1D matrix: 1 + (g^2/2)(|a-1/2| + |b-1/2| - |a-b|)."""
    return 1.0 + 0.5*(g*g)*(np.abs(a - 0.5) + np.abs(b - 0.5) - np.abs(a - b))

import numpy as np

def make_cd_kernel(d: int, gamma):
    """
    Centered-discrepancy kernel on [0,1]^d with per-coordinate weights gamma:

        K(t, x) = ∏_{j=1}^d [ 1 + (γ_j^2 / 2) ( |t_j - 1/2| + |x_j - 1/2| - |t_j - x_j| ) ].

    Notes
    -----
    - If gamma is scalar, it is broadcast to all d coordinates.
    - With gamma = 0, K ≡ 1.
    """
    g = np.asarray(gamma, float)
    if g.ndim == 0:
        g = np.full(d, float(g))
    if g.size != d:
        raise ValueError(f"gamma must be scalar or length {d}, got {g.size}")
    g2 = (g ** 2)

    def K(A, B):
        A = np.atleast_2d(np.asarray(A, float))
        B = np.atleast_2d(np.asarray(B, float))
        a = A[:, None, :]                  # (nA, 1, d)
        b = B[None, :, :]                  # (1, nB, d)
        term = 1.0 + 0.5 * g2 * (np.abs(a - 0.5) + np.abs(b - 0.5) - np.abs(a - b))
        return np.prod(term, axis=-1)      # (nA, nB)

    return K