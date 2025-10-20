import numpy as np
import scipy as sp

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

def asian_arith_mean_call_payoff(
    X: np.ndarray,   # (n_paths, d) uniforms in (0,1)
    S0: float,
    r: float,
    sigma: float,
    T: float = None,
    K: float = 0.0,
    *,
    # Choose ONE of the drift specifications:
    drift=None,            # None | scalar | length-d array (per-interval drift per unit time)
    theta_slope=None,      # float for theta(t) = theta_slope * t
    t: np.ndarray = None,  # optional non-uniform grid; overrides T,d if provided
    A: np.ndarray = None,  # optional precomputed transform compatible with t
) -> np.ndarray:
    """
    Discounted arithmetic-mean Asian call payoff with optional importance-sampling drift.

    - If `t` is given, it must be strictly increasing and its last value is T.
    - If `theta_slope` is provided, we use theta(t) = theta_slope * t (linear drift in time).
      Mean shift is exact: m_j = ∫_0^{t_j} theta(s) ds = 0.5 * theta_slope * t_j^2.
      Likelihood ratio uses piecewise-constant integrand at left endpoints: theta_k = theta_slope * t_{k-1}.
    - Otherwise, `drift` behaves as before (scalar or length-d, per-interval drift per unit time),
      with m_j = Σ_{k≤j} drift_k * Δt_k.
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError("X must have shape (n_paths, d)")
    n_paths, d = X.shape

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
    dt = np.empty(d)
    dt[0] = t[0]
    if d > 1:
        dt[1:] = np.diff(t)
    t_left = np.empty(d)
    t_left[0] = 0.0
    if d > 1:
        t_left[1:] = t[:-1]

    # normals -> BM(t)
    Z = sp.stats.norm.ppf(X)
    if A is None:
        A = bm_transform(t=t)
    BM = Z @ A.T  # (n_paths, d)

    # choose drift, compute mean shift and LR
    if theta_slope is not None:
        theta_k = theta_slope * t_left              # piecewise-constant at left endpoints
        m = 0.5 * theta_slope * (t ** 2)            # exact cumulative mean shift at each t_j
    elif drift is None:
        theta_k = np.zeros(d)
        m = np.zeros(d)
    else:
        if np.ndim(drift) == 0:
            theta_k = np.full(d, float(drift))
        else:
            theta_k = np.asarray(drift, dtype=float)
            if theta_k.shape != (d,):
                raise ValueError(f"`drift` must be scalar or length-d; got {theta_k.shape}")
        m = np.cumsum(theta_k * dt)

    BM_shift = BM + m[None, :]

    # Likelihood ratio: L = exp( -Σ θ_k ΔW_k - 0.5 Σ θ_k^2 Δt_k )
    dW = np.empty_like(BM)
    dW[:, 0] = BM[:, 0]
    if d > 1:
        dW[:, 1:] = np.diff(BM, axis=1)
    term1 = -(dW @ theta_k)
    term2 = -0.5 * float(np.sum((theta_k ** 2) * dt))
    LR = np.exp(term1 + term2)

    # Stock paths and payoff
    S = S0 * np.exp((r - 0.5 * sigma**2) * t[None, :] + sigma * BM_shift)

    # Arithmetic mean over [0,T] with trapezoidal weights including S(0)
    # ⇒ ∫_0^T S(t) dt ≈ 0.5*S0*dt1 + Σ_{k=2..d} 0.5*(S_{k-1}+S_k)*dt_k
    # Implemented compactly via telescoping form below:
    # First handle the first interval explicitly:
    mean_S = 0.5 * S0 * dt[0]
    if d == 1:
        mean_S += 0.5 * S[:, 0] * dt[0]
    else:
        # 0.5*(S_{k-1}+S_k)*dt_k for k=2..d
        mean_S = mean_S + (0.5 * (S[:, :-1] + S[:, 1:]) * dt[1:]).sum(axis=1)
        # plus the 0.5*S[:,0]*dt[0] term to complete the first trapezoid
        mean_S = mean_S + 0.5 * S[:, 0] * dt[0]
    mean_S = mean_S / T

    payoff = np.maximum(mean_S - K, 0.0) * np.exp(-r * T)
    return payoff * LR

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
