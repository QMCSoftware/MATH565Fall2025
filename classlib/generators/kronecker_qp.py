## This is the version that ChatGPT helped make that fits the qmcpy discrete distributions
## To use this generator in qmcpy, you can do the following:
#
# import qmcpy as qp
# from classlib.generators import QPKronecker
# qp.Kronecker = QPKronecker

from __future__ import annotations
import numpy as np
import warnings

# --- Try to import qmcpy's LD base; fall back to a shim if not present ----
try:
    # Newer qmcpy layout
    from qmcpy.discrete_distribution._discrete_distribution import \
        LDDiscreteDistribution as _LDBase
except Exception:
    try:
        # Older qmcpy layout
        from qmcpy.abstract_discrete_distribution import \
            AbstractLDDiscreteDistribution as _LDBase
    except Exception:
        class _LDBase:  # minimal shim
            pass

# ---- Fixed prime table and direction choices --------------------------------
_PRIMES = np.array(
    [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,
     101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,
     193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281,283,
     293,307,311,313,317,331,337,347,349,353,359,367,373,379,383,389,397,401,
     409,419,421,431,433,439,443,449,457,461,463,467,479,487,491,499,503,509,
     521,523,541], dtype=float
)
_RICHTMYER = np.sqrt(_PRIMES) % 1.0

_ALPHA_PREFERRED = np.array([
    4.224371872086318813e-01,
    3.605965189622313272e-01,
    3.486721371284548510e-01,
    4.520388055082059653e-01,
    2.550750763977845947e-01,
    2.205289926147350477e-01,
    2.071242872822959824e-01,
    3.049354991086913325e-01,
    3.872168854974577523e-01,
    2.275808872220986823e-01,
    1.773740893160189180e-01,
    1.958399682530986008e-01,
    3.216346950830996643e-01,
], dtype=np.float64)

def _suzuki(d: int) -> np.ndarray:
    # components 2^{i/(d+1)}, i = 1..d
    return 2.0 ** (np.arange(1, d + 1, dtype=float) / (d + 1.0))

def _alpha_from_string(alpha: str | None, d: int) -> np.ndarray:
    if alpha is None or str(alpha).lower() == "preferred":
        base = _ALPHA_PREFERRED
        if d <= base.size:
            return base[:d].copy()
        # d > preferred length: warn and return random alpha
        warnings.warn(
            f"Requested dimension {d} exceeds preferred vector length {base.size}. "
            "Using random alpha for all dimensions.",
            UserWarning,
        )
        return np.random.default_rng().random(d)

    a = alpha.lower()
    if a == "richtmyer":
        if d <= _RICHTMYER.size:
            return _RICHTMYER[:d].copy()
        # extend using next primes if available; otherwise a safe fallback
        try:
            from sympy import nextprime  # optional
            extra = []
            last = int(_PRIMES[-1])
            for _ in range(d - _RICHTMYER.size):
                last = int(nextprime(last))
                extra.append((last ** 0.5) % 1.0)
            return np.concatenate([_RICHTMYER, np.array(extra, dtype=float)])
        except Exception:
            tiled = np.resize(_RICHTMYER, d)
            eps = np.finfo(float).eps
            k = d - _RICHTMYER.size
            if k > 0:
                tiled[-k:] = (tiled[-k:] + np.linspace(eps, 10 * eps, k)) % 1.0
            return tiled

    elif a == "suzuki":
        return _suzuki(d)

    else:
        raise ValueError("alpha must be 'PREFERRED', 'RICHTMYER', 'SUZUKI', or None (or pass an array).")

# ---- qmcpy-compatible Kronecker ---------------------------------------------

class QPKronecker(_LDBase):
    """
    Kronecker (irrational rotation) sequence compatible with qmcpy LD API.

    Parameters
    ----------
    dimension : int
    alpha : {'RICHTMYER','SUZUKI'} or array_like of shape (d,), default "RICHTMYER"
    randomize : bool, default True
        If True, apply Cranley–Patterson shift.
        - seed=None  -> fresh entropy (randomized by default)
        - seed=int   -> reproducible
    seed : int or None, default None
    """
    def __init__(self, dimension=1, alpha="PREFERRED", randomize=True, seed=None, **kwargs):
    
        self.dimension = int(dimension)
        self.d = self.dimension              # alias some code expects
        self.mimics = "StdUniform"
        self.randomize = bool(randomize)
        self.seed = seed

        # Direction vector
        if isinstance(alpha, (str, type(None))):
            self.alpha = _alpha_from_string(alpha, self.dimension)
        else:
            a = np.asarray(alpha, dtype=float).reshape(-1)
            if a.size < self.dimension:
                raise ValueError("alpha too short for dimension")
            self.alpha = a[: self.dimension]

        # Shift (randomized by default; seed controls reproducibility)
        if self.randomize:
            self.rng = np.random.default_rng(seed)  # seed=None -> fresh entropy
            self.shift = self.rng.random(self.dimension)
        else:
            self.rng = None
            self.shift = np.zeros(self.dimension)

        # Some qmcpy code checks this
        self.low_discrepancy = True

    def gen_samples(self, n: int) -> np.ndarray:
        """Return (n, d) samples in [0,1). Rows = samples; cols = coordinates."""
        n = int(n)
        if n <= 0:
            return np.empty((0, self.dimension), dtype=float)
        idx = np.arange(n, dtype=float).reshape(n, 1)  # n = 0..n-1
        pts = self.shift + idx * self.alpha.reshape(1, self.dimension)
        return np.mod(pts, 1.0)

    def spawn(self, n_streams: int):
        """Return a list of independent shifted Kronecker generators."""
        n_streams = int(n_streams)
        if n_streams <= 0:
            return []
        if self.seed is not None:
            seeds = np.random.SeedSequence(self.seed).spawn(n_streams)
            ints = [int(np.random.default_rng(s).integers(2**31 - 1)) for s in seeds]
        else:
            ints = [int(np.random.default_rng().integers(2**31 - 1)) for _ in range(n_streams)]
        return [QPKronecker(self.dimension, alpha=self.alpha.copy(),
                            randomize=True, seed=s) for s in ints]

    def set_seed(self, seed: int | None):
        """Reset RNG/shift according to current randomize flag."""
        self.seed = seed
        if self.randomize:
            self.rng = np.random.default_rng(seed)  # seed=None -> fresh entropy
            self.shift = self.rng.random(self.dimension)
        else:
            self.rng = None
            self.shift = np.zeros(self.dimension)
        return self

__all__ = ["QPKronecker"]