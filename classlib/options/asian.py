"""Asian arithmetic-mean call payoff (simple PCA BM + optional IS drift).

- Brownian motion at t_j = j*T/d is constructed by PCA / symmetric eigendecomposition
  of the covariance matrix C_{ij} = min(t_i, t_j).
- Input `X` are uniforms in (0,1) (PRNG or Sobol via qmcpy). We map them to
  standard normals with `norm.ppf` and then to BM via the PCA transform.
- Optional importance-sampling drift is supported via a per-interval drift θ_k
  and the corresponding Girsanov likelihood ratio.

This version intentionally keeps things *simple* (no endpoint clipping, etc.).
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import scipy as sp

__all__ = ["bm_transform", "asian_arith_mean_call_payoff"]


def bm_transform(T: float, d: int) -> np.ndarray:
    """Return matrix A so that Z @ A.T ~ (W_{t_1},...,W_{t_d}). Uses PCA.

    t_j = j*T/d, C_{ij} = min(t_i, t_j), and C = Q diag(λ) Q^T ⇒ A = Q diag(√λ).
    """
    if d <= 0:
        raise ValueError("d must be positive")
    step = T / d
    t = np.arange(1, d + 1, dtype=float) * step
    C = np.minimum.outer(t, t)
    vals, vecs = np.linalg.eigh(C)
    vals = np.clip(vals, 0.0, None)  # light guard for numerical tiny negatives
    A = vecs @ np.diag(np.sqrt(vals))
    return A


def _likelihood_ratio(BM_paths: np.ndarray, theta_k: np.ndarray, step: float) -> np.ndarray:
    """Girsanov LR for piecewise-constant drift θ_k on intervals of length step.

    L = exp( -Σ θ_k ΔW_k - 0.5 Σ θ_k^2 Δt ).
    """
    dW = np.empty_like(BM_paths)
    dW[:, 0] = BM_paths[:, 0]
    if BM_paths.shape[1] > 1:
        dW[:, 1:] = np.diff(BM_paths, axis=1)
    term1 = -(dW @ theta_k)                 # shape (n_paths,)
    term2 = -0.5 * step * float(np.sum(theta_k**2))
    return np.exp(term1 + term2)


def asian_arith_mean_call_payoff(
    X: np.ndarray,   # (n_paths, d) uniforms in (0,1)
    S0: float,
    r: float,
    sigma: float,
    T: float,
    K: float,
    drift: Optional[Iterable[float]] = None,  # None | scalar | length-d array
    A: Optional[np.ndarray] = None,           # optional precomputed bm_transform(T,d)
) -> np.ndarray:
    """Discounted arithmetic-mean Asian **call** payoff with optional IS drift.

    Returns an array of shape (n_paths,) containing the likelihood-ratio–weighted
    discounted payoffs (i.e., unbiased per-path contributions).
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError("X must have shape (n_paths, d)")
    n_paths, d = X.shape

    step = T / d
    t = np.arange(1, d + 1, dtype=float) * step

    # Standard normals then Brownian motion via PCA transform
    Z = sp.stats.norm.ppf(X)
    if A is None:
        A = bm_transform(T, d)
    BM = Z @ A.T  # (n_paths, d)

    # Optional importance-sampling drift
    if drift is None:
        theta_k = np.zeros(d)
        LR = np.ones(n_paths)
        BM_shift = BM
    else:
        if np.ndim(drift) == 0:
            theta_k = np.full(d, float(drift))
        else:
            theta_k = np.asarray(drift, dtype=float)
            if theta_k.shape != (d,):
                raise ValueError(f"drift must be scalar or length-d; got {theta_k.shape}")
        m = np.cumsum(theta_k * step)  # mean shift at each t_j
        BM_shift = BM + m[None, :]
        LR = _likelihood_ratio(BM, theta_k, step)

    # Stock paths and payoff
    S = S0 * np.exp((r - 0.5 * sigma**2) * t[None, :] + sigma * BM_shift)

    # Arithmetic mean over [0,T] with trapezoidal rule including S(0)
    mean_S = (0.5 * S0 + S[:, :-1].sum(axis=1) + 0.5 * S[:, -1]) * (step / T)

    payoff = np.maximum(mean_S - K, 0.0) * np.exp(-r * T)
    return payoff * LR
