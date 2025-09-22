from __future__ import annotations

from typing import Callable, Tuple, Optional
import numpy as np


def metropolis(
    log_target_density: Callable[[np.ndarray], float],
    x0: np.ndarray | float,
    n_samples: int = 50_000,
    proposal_sd: float = 0.15,
    rng: Optional[np.random.Generator | int] = None,
) -> Tuple[np.ndarray, float]:
    """
    Random-walk Metropolis with Normal(0, proposal_sd^2 I) proposals.

    Parameters
    ----------
    log_target_density : callable
        Function f(x) returning log π(x). Must accept a NumPy array of shape (d,)
        (or scalar for 1-D) and return a finite float where defined.
    x0 : array_like
        Initial state (shape (d,) or scalar).
    n_samples : int, default 50_000
        Number of samples to generate.
    proposal_sd : float, default 0.15
        Standard deviation of isotropic Gaussian proposal.
    rng : np.random.Generator | int | None
        Random generator or seed. If None, a new Generator is created.

    Returns
    -------
    samples : ndarray, shape (n_samples, d)
        The Markov chain states (includes only accepted/current states per step).
    acceptance_rate : float
        Fraction of accepted proposals in [0,1].
    """
    rng = np.random.default_rng(rng)
    x = np.array(x0, dtype=float).reshape(-1)
    d = x.size
    samples = np.empty((n_samples, d))
    log_fx = float(log_target_density(x))
    accepts = 0
    warned_nan = False  # <- warn once if user function returns NaN

    for i in range(n_samples):
        z = x + rng.normal(scale=proposal_sd, size=d)
        log_fz = log_target_density(z)

        if not np.isfinite(log_fz):  # proposal outside support → reject
            accept = False
            if np.isnan(log_fz) and not warned_nan:
                print("Warning: log_target_density returned NaN for a proposal; rejecting such proposals.")
                warned_nan = True
        elif not np.isfinite(log_fx):  # current invalid while proposal finite → accept
            accept = True
        else:
            # standard log-accept rule
            accept = (np.log(rng.uniform()) < (log_fz - log_fx))

        if accept:
            x, log_fx = z, float(log_fz)
            accepts += 1

        samples[i] = x

    return samples, accepts / n_samples