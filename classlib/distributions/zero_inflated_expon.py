"""
zero_inflated_expon distribution
--------------------------------

Zero-inflated exponential:
P(X=0) = p_zero;  for x>0, X|X>0 ~ Exponential(rate) with mean = 1/rate.

This extends `scipy.stats.rv_continuous` so you can use all the usual
methods: `.rvs()`, `.cdf()`, `.ppf()`, etc.

Example
-------
>>> from classlib.distributions.zero_inflated_expon import make_zie
>>> zie = make_zie(p_zero=0.2, mean_pos=10.0)
>>> zie.rvs(size=5, random_state=np.random.default_rng(123))
array([...])
"""

import numpy as np
from scipy import stats


class zero_inflated_expon(stats.rv_continuous):
    """
    Zero-inflated exponential distribution.

    Parameters
    ----------
    p_zero : float in [0,1)
        Probability of zero wait time (atom at 0).
    rate : float > 0
        Exponential rate for the positive part (1/mean of positive waits).
    """

    def __init__(self, p_zero=0.2, rate=0.1, *args, **kwargs):
        super().__init__(a=0.0, name="zero_inflated_expon", *args, **kwargs)
        if not (0.0 <= p_zero < 1.0):
            raise ValueError("p_zero must be in [0,1).")
        if rate <= 0:
            raise ValueError("rate must be > 0.")
        self.p_zero = float(p_zero)
        self.rate = float(rate)

    # Public CDF (right-continuous): F(0) = p_zero
    def cdf(self, x, *args, **kwargs):
        p0, lam = self.p_zero, self.rate
        x = np.asarray(x, dtype=float)
        # For x < 0: 0; for x >= 0: p0 + (1-p0)*(1 - e^{-lam x})
        return np.where(x < 0.0, 0.0, p0 + (1.0 - p0) * (1.0 - np.exp(-lam * x)))

    # Closed-form PPF (quantile)
    def _ppf(self, q):
        p0, lam = self.p_zero, self.rate
        q = np.asarray(q, dtype=float)
        out = np.zeros_like(q)
        mask = (q > p0) & (q < 1.0)
        t = (q[mask] - p0) / (1.0 - p0)
        out[mask] = -np.log1p(-t) / lam
        out = np.where(q >= 1.0, np.inf, out)
        out = np.where(q < 0.0, np.nan, out)
        return out

    # Vectorized RNG compatible with SciPy’s machinery
    def _rvs(self, size=None, random_state=None):
        p0, lam = self.p_zero, self.rate
        u = random_state.random(size)
        x = np.zeros(size, dtype=float)
        mask = u >= p0
        x[mask] = random_state.exponential(scale=1.0/lam, size=np.sum(mask))
        return x


# --- Convenience constructor ---
def make_zie(p_zero: float, mean_pos: float):
    """
    Convenience constructor: return a zero_inflated_expon
    with atom at 0 (prob = p_zero) and mean wait time = mean_pos for positive values.
    """
    return zero_inflated_expon(p_zero=p_zero, rate=1.0/mean_pos)