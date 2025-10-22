import numpy as np
import scipy as sp
from math import log, sqrt, exp
from scipy.stats import norm

# --- your bm_transform stays exactly as-is ---
def bm_transform(T: float = None, d: int = None, t: np.ndarray = None) -> np.ndarray:
    """
    PCA transform A so that Z @ A.T has the law of (W_{t1},...,W_{td}).
    Supply either (T, d) for uniform t_j = j*T/d, or an explicit increasing 1D t array.
    """
    if t is None:
        if T is None or d is None:
            raise ValueError("Provide either (T, d) or an explicit time grid t.")
        step = T / d
        t = np.arange(1, d + 1, dtype=float) * step
    else:
        t = np.asarray(t, dtype=float)
        if t.ndim != 1 or t.size == 0 or not np.all(np.diff(t) > 0):
            raise ValueError("t must be a 1D strictly increasing array of times > 0.")
        d = t.size
        T = float(t[-1])

    C = np.minimum.outer(t, t)
    vals, vecs = np.linalg.eigh(C)
    vals = np.clip(vals, 0.0, None)
    A = vecs @ np.diag(np.sqrt(vals))
    return A

# --- small helper: shared path + LR construction (no duplication) ---
def _paths_LR_S_from_uniforms(
    X: np.ndarray,
    S0: float, r: float, sigma: float,
    *, T: float = None, t: np.ndarray = None,
    drift=None, A: np.ndarray = None
):
    """
    Given uniforms X (n,d), build:
      - t, dt, T
      - Brownian motion with optional mean shift from constant/per-interval drift
      - likelihood ratio (LR)
      - GBM stock paths S at t1..td
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError("X must have shape (n_paths, d)")
    n_paths, d = X.shape

    # Build time grid and deltas
    if t is None:
        if T is None:
            raise ValueError("Provide T if `t` is not given.")
        step = T / d
        t = np.arange(1, d + 1, dtype=float) * step
    else:
        t = np.asarray(t, dtype=float)
        if t.shape != (d,):
            raise ValueError(f"t must have length d={d}, got {t.shape}")
        T = float(t[-1])

    dt = np.empty(d); dt[0] = t[0]
    if d > 1:
        dt[1:] = np.diff(t)

    # Normals → BM(t) via PCA
    Z = norm.ppf(X)
    if A is None:
        A = bm_transform(t=t)
    BM = Z @ A.T  # (n_paths, d)

    # Importance-sampling drift (constant or per-interval)
    if drift is None:
        theta_k = np.zeros(d)
    elif np.ndim(drift) == 0:
        theta_k = np.full(d, float(drift))
    else:
        theta_k = np.asarray(drift, dtype=float)
        if theta_k.shape != (d,):
            raise ValueError(f"`drift` must be scalar or length-d; got {theta_k.shape}")

    # Mean shift for BM at each monitoring time
    m = np.cumsum(theta_k * dt)                 # (d,)
    BM_shift = BM + m[None, :]

    # Likelihood ratio with your ΔW convention
    dW = np.empty_like(BM)
    dW[:, 0] = BM[:, 0]
    if d > 1:
        dW[:, 1:] = np.diff(BM, axis=1)
    term1 = -(dW @ theta_k)                     # -Σ θ_k ΔW_k
    term2 = -0.5 * float(np.sum((theta_k**2) * dt))  # -½ Σ θ_k^2 Δt_k
    LR = np.exp(term1 + term2)

    # GBM paths
    S = S0 * np.exp((r - 0.5 * sigma**2) * t[None, :] + sigma * BM_shift)
    return S, LR, t, dt, T

def _bs_call_price(S0, K, r, sigma, T):
    if sigma <= 0 or T <= 0:
        return max(S0 - K*exp(-r*T), 0.0)
    s = sigma * sqrt(T)
    d1 = (log(S0/K) + (r + 0.5*sigma**2)*T) / s
    d2 = d1 - s
    return S0*norm.cdf(d1) - K*exp(-r*T)*norm.cdf(d2)

def asian_arith_mean_call_payoff(
    X: np.ndarray,   # (n_paths, d) uniforms in (0,1)
    S0: float,
    r: float,
    sigma: float,
    T: float = None,
    K: float = 0.0,
    *,
    drift=None,            # None | scalar | length-d array  (CONSTANT DRIFT ONLY)
    t: np.ndarray = None,  # optional non-uniform grid; overrides T,d if provided
    A: np.ndarray = None,  # optional precomputed transform compatible with t
    # Optional add-ons:
    compute_euro: bool = False,          # also return (X_euro, C_bs)
    use_control_variate: bool = False,   # return CV-adjusted per-path Z
    return_beta: bool = False,           # if CV, also return beta
):
    """
    Discounted arithmetic-mean Asian call payoff with optional importance sampling (constant/per-interval drift).
    Default behavior (both compute_euro=False and use_control_variate=False): returns Y only.

    If compute_euro=True: returns (Y, X_euro, C_bs)
    If use_control_variate=True: returns Z (or (Z, beta, C_bs) if return_beta=True)
    """
    # Shared paths + LR (constant/per-interval drift only)
    S, LR, t, dt, T = _paths_LR_S_from_uniforms(
        X, S0, r, sigma, T=T, t=t, drift=drift, A=A
    )

    # Trapezoid average on [0,T] for non-uniform grid (branch-free, includes S0)
    n, d = S.shape
    S_left = np.concatenate([np.full((n, 1), S0), S[:, :-1]], axis=1)  # (n,d)
    areas  = 0.5 * (S_left + S) * dt                                   # (n,d)
    mean_S = areas.sum(axis=1) / T

    disc = np.exp(-r * T)
    Y = disc * np.maximum(mean_S - K, 0.0) * LR  # (n,)

    # Legacy fast path
    if not compute_euro and not use_control_variate:
        return Y

    # European pieces only if needed
    ST = S[:, -1]
    X_euro = disc * np.maximum(ST - K, 0.0) * LR
    C_bs = _bs_call_price(S0, K, r, sigma, T)

    if compute_euro and not use_control_variate:
        return Y, X_euro, C_bs

    # Control variate: Z = Y - beta*(X - C_bs)
    V = X_euro - C_bs
    varV = V.var(ddof=1)
    beta = 0.0 if np.isclose(varV, 0.0) else float(np.cov(Y, V, ddof=1)[0, 1] / varV)
    Z = Y - beta * V

    if return_beta:
        return Z, beta, C_bs
    else:
        return Z
    
def price(payoffs: np.ndarray, *, iid: bool = False, ddof: int = 1):
    """Return (estimate, standard_error_or_None).

    - For **IID** sampling, set ``iid=True`` to compute the Monte Carlo standard error.
    - For low-discrepancy (deterministic Sobol/Halton), keep ``iid=False``; we
      return ``(mean, None)``.
    """
    y = np.asarray(payoffs, dtype=float).ravel()
    est = float(np.mean(y))
    if iid:
        se = float(np.std(y, ddof=ddof) / np.sqrt(y.size))
    else:
        se = None
    return est, se


def price_rqmc(payoffs_by_rep: np.ndarray, *, ddof: int = 1):
    """Estimate price and SE from **randomized QMC** with independent replicates.

    Accepts either a 2D array of shape ``(R, n)`` containing per-replicate
    payoffs, or a 1D array of length ``R`` containing per-replicate **means**.

    The standard error is the sample std of replicate means divided by ``sqrt(R)``.
    """
    Y = np.asarray(payoffs_by_rep, dtype=float)
    if Y.ndim == 2:
        rep_means = Y.mean(axis=1)
    elif Y.ndim == 1:
        rep_means = Y
    else:
        raise ValueError("payoffs_by_rep must be 1D or 2D (R or R x n)")
    R = rep_means.size
    if R < 2:
        raise ValueError("At least two replicates are required to estimate an SE")
    est = float(rep_means.mean())
    se = float(rep_means.std(ddof=ddof) / np.sqrt(R))
    return est, se

