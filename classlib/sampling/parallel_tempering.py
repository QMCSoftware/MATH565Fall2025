from __future__ import annotations

from typing import Callable, Iterable, Optional, Tuple, Dict, List
import numpy as np
from .metropolis import metropolis


def _make_tempered_log_density(
    log_density: Callable[[np.ndarray], float],
    beta: float,
) -> Callable[[np.ndarray], float]:
    """
    Default tempering: scale the *entire* log density, log π_beta(x) = beta * log π(x).

    This is a pragmatic choice that preserves the mode structure and is sufficient
    for demonstration/teaching. If you want the exact tempered posterior with
    likelihood^beta * prior, pass a custom log_density that already encodes beta.
    """
    if beta == 1.0:
        return log_density

    def f(x: np.ndarray) -> float:
        return beta * float(log_density(x))

    return f


def parallel_tempering(
    base_log_density: Callable[[np.ndarray], float],
    x0_list: Iterable[np.ndarray | float],
    betas: Iterable[float] = (1.0, 0.6, 0.3),
    *,
    n_outer: int = 400,
    block_len: int = 100,
    proposal_sd: float = 0.30,
    swap_neighbors: str = "adjacent",
    rng: Optional[np.random.Generator | int] = None,
) -> Tuple[np.ndarray, List[np.ndarray], Dict[str, np.ndarray | float]]:
    """
    Parallel tempering (replica exchange) **reusing** the provided Metropolis kernel.

    Strategy
    --------
    Run R replicas at inverse temperatures `betas`. Each outer iteration:
      1) For each replica r, take `block_len` Metropolis steps targeting π_beta_r.
      2) Attempt swaps of states between chains (adjacent by default).

    Parameters
    ----------
    base_log_density : callable
        The target log density for β=1 (cold chain).
    x0_list : iterable of array_like
        Initial states for each replica; length must equal len(betas).
    betas : iterable of float
        Inverse temperatures (β_1=1.0 ≥ β_2 ≥ ... > 0). Order is respected.
    n_outer : int
        Number of exchange rounds. Each chain runs `n_outer * block_len` MH steps.
    block_len : int
        Number of MH steps per replica between exchange attempts.
    proposal_sd : float
        RW proposal SD passed into the Metropolis kernel.
    swap_neighbors : {"adjacent"}
        Currently only adjacent swaps are supported.
    rng : np.random.Generator | int | None
        RNG or seed.

    Returns
    -------
    trace_cold : ndarray, shape (n_outer, d)
        Trace of the cold chain (β=1) at the end of each outer block.
    final_states : list of ndarray
        Final states of all replicas in the order of `betas`.
    stats : dict
        - "acceptance_rates": ndarray shape (R,) average per-replica acceptance.
        - "swap_attempts": int total number of swap attempts.
        - "swap_accepts": int number of accepted swaps.
        - "swap_rate": float accepted / attempted.
        - "betas": ndarray of betas used.

    Notes
    -----
    If you want *exact* tempered posteriors of the form likelihood^β * prior,
    construct custom callables `log_density_beta_r` and pass this function
    with those betas one-at-a-time; or fork this function to supply a pair
    (log_likelihood, log_prior).
    """
    rng = np.random.default_rng(rng)
    betas = np.array(list(betas), dtype=float)
    R = len(betas)
    x_list = [np.array(x0, float).reshape(-1) for x0 in x0_list]
    assert len(x_list) == R, "x0_list must have the same length as betas"

    # Build tempered targets from the base
    tempered = [_make_tempered_log_density(base_log_density, beta) for beta in betas]

    # Book-keeping
    d = x_list[0].size
    trace_cold = np.empty((n_outer, d))
    acc_sums = np.zeros(R, float)
    total_steps = 0
    swap_attempts = 0
    swap_accepts = 0

    for k in range(n_outer):
        # 1) Advance each replica using YOUR Metropolis kernel
        for r in range(R):
            samples, acc = metropolis(
                tempered[r],
                x_list[r],
                n_samples=block_len,
                proposal_sd=proposal_sd,
                rng=rng,
            )
            x_list[r] = samples[-1]
            acc_sums[r] += acc * block_len
        total_steps += block_len

        # Record cold chain (β=1.0 assumed to be first)
        trace_cold[k] = x_list[0]

        # 2) Swaps—adjacent pairs only
        if swap_neighbors != "adjacent":
            raise NotImplementedError("Only adjacent swaps are supported.")
        for r in range(R - 1):
            xr, xs = x_list[r], x_list[r + 1]
            br, bs = betas[r], betas[r + 1]
            # Replica-exchange MH log ratio: Δ = (β_r - β_s) [log π(x_s) - log π(x_r)]
            delta = (br - bs) * (float(base_log_density(xs)) - float(base_log_density(xr)))
            swap_attempts += 1
            if np.log(rng.uniform()) < delta:
                x_list[r], x_list[r + 1] = xs, xr
                swap_accepts += 1

    stats = {
        "acceptance_rates": acc_sums / total_steps,
        "swap_attempts": swap_attempts,
        "swap_accepts": swap_accepts,
        "swap_rate": (swap_accepts / swap_attempts) if swap_attempts else 0.0,
        "betas": betas.copy(),
    }
    return trace_cold, x_list, stats