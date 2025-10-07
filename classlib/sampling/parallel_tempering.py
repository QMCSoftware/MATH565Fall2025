from __future__ import annotations
from typing import Sequence, Tuple, Dict, Any, List
import numpy as np
from .metropolis import metropolis


def parallel_tempering(
    base_log_density,
    x0_list: Sequence[np.ndarray],
    betas: Sequence[float],
    n_outer: int = 400,
    block_len: int = 100,
    proposal_sd: float | Sequence[float] = 0.30,
    swap_neighbors: bool = True,
    rng=None,
) -> Tuple[np.ndarray, List[np.ndarray], Dict[str, Any]]:
    """
    Parallel tempering (replica exchange) for an unnormalized log-density.

    Parameters
    ----------
    base_log_density : callable
        f(x) -> log target (unnormalized).
    x0_list : sequence of ndarray
        Initial state for each replica r = 0..R-1 (all same dimension).
    betas : sequence of float
        Inverse temperatures for each replica (0 < beta <= 1). Largest beta is "cold".
    n_outer : int
        Number of exchange rounds.
    block_len : int
        Metropolis steps per replica per round.
    proposal_sd : float or sequence of float (len R)
        Proposal standard deviation(s). Scalar applies to all replicas; a sequence
        specifies per-replica values.
    swap_neighbors : bool
        If True, attempt neighbor swaps with even/odd alternation each round.
    rng : None | int | np.random.Generator
        Random generator. If None, creates default_rng(); if int, used as seed.

    Returns
    -------
    trace_cold : ndarray
        Concatenation of the cold replica's samples across all rounds.
        Shape (n_outer*block_len,) for 1D; (n_outer*block_len, d) otherwise.
    finals : list[ndarray]
        Final state of each replica.
    stats : dict
        {
          'betas'            : (R,) array
          'acceptance_rates' : (R,) array of overall MH acceptance (0..1)
          'acc_cold_hist'    : (n_outer,) array of cold acceptance per round
          'swap_attempts'    : int
          'swap_accepts'     : int
          'swap_rate'        : float
          'swap_try_edge'    : (R-1,) int array
          'swap_acc_edge'    : (R-1,) int array
          'swap_rate_edge'   : (R-1,) float array
        }
    """
    # RNG normalize
    if rng is None or isinstance(rng, (int, np.integer)):
        rng = np.random.default_rng(rng)

    # Replicas & shapes
    x_list = [np.asarray(x0, dtype=float).copy() for x0 in x0_list]
    R = len(x_list)
    if R < 2:
        raise ValueError("Need at least 2 replicas for parallel tempering.")
    betas = np.asarray(betas, dtype=float)
    if betas.shape != (R,):
        raise ValueError(f"'betas' must have length {R}, got shape {betas.shape}")

    # proposal_sd -> per-replica list of floats
    if np.ndim(proposal_sd) == 0:
        prop_sds = [float(proposal_sd)] * R
    else:
        prop_sds = [float(s) for s in proposal_sd]
        if len(prop_sds) != R:
            raise ValueError(f"'proposal_sd' must be scalar or length {R}, got {len(prop_sds)}")

    # Tempered log-densities
    tempered = [ (lambda f, b: (lambda z, _f=f, _b=b: _b * _f(z)))(base_log_density, b) for b in betas ]

    # Cold replica is defined by temperature, not by which state sits there
    cold_idx = int(np.argmax(betas))

    # Book-keeping
    acc_sums = np.zeros(R, dtype=float)          # accepted steps count (sum over blocks)
    acc_cold_hist: List[float] = []
    cold_blocks: List[np.ndarray] = []

    swap_try_edge = np.zeros(R - 1, dtype=int)
    swap_acc_edge = np.zeros(R - 1, dtype=int)
    swap_attempts = 0
    swap_accepts  = 0

    # Cache current log f(x) for swaps
    logf_curr = np.array([base_log_density(x) for x in x_list], dtype=float)

    for k in range(n_outer):
        # 1) Advance each replica (one MH block); capture the cold block's samples
        round_acc = np.zeros(R, dtype=float)
        round_samples: List[np.ndarray] = [None] * R  # type: ignore

        for r in range(R):
            samples, acc = metropolis(
                log_target_density=tempered[r],
                x0=x_list[r],
                n_samples=block_len,
                proposal_sd=prop_sds[r],   # scalar per replica
                rng=rng,
            )
            x_list[r] = samples[-1]
            logf_curr[r] = base_log_density(x_list[r])

            # Convert acc (fraction) to accepted count for robust averaging
            acc_sums[r] += acc * block_len
            round_acc[r] = acc
            round_samples[r] = samples

        acc_cold_hist.append(round_acc[cold_idx])
        cold_blocks.append(round_samples[cold_idx])

        # 2) Neighbor swaps with even/odd alternation
        if swap_neighbors:
            start = k % 2  # even rounds: (0,1), (2,3), ... ; odd: (1,2), (3,4), ...
            for i in range(start, R - 1, 2):
                j = i + 1
                swap_attempts += 1
                swap_try_edge[i] += 1

                # MH acceptance on exchange
                delta = (betas[i] - betas[j]) * (logf_curr[j] - logf_curr[i])
                if np.log(rng.random()) < min(0.0, delta):
                    # accept: swap states & cached log f
                    x_list[i], x_list[j] = x_list[j], x_list[i]
                    logf_curr[i], logf_curr[j] = logf_curr[j], logf_curr[i]
                    swap_accepts += 1
                    swap_acc_edge[i] += 1
                # Note: cold_idx never changes; it is defined by beta, not by state position.

    # Final per-replica acceptance (as fraction over total steps)
    total_steps = n_outer * block_len
    acceptance_rates = acc_sums / total_steps

    # Cold trace concatenation
    trace_cold = np.concatenate(cold_blocks, axis=0)
    if trace_cold.ndim == 2 and trace_cold.shape[1] == 1:
        trace_cold = trace_cold[:, 0]

    finals = [np.asarray(x).copy() for x in x_list]

    # Swap rates
    swap_rate = (swap_accepts / swap_attempts) if swap_attempts > 0 else np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        swap_rate_edge = np.where(swap_try_edge > 0, swap_acc_edge / swap_try_edge, np.nan)

    stats: Dict[str, Any] = dict(
        betas=betas.copy(),
        acceptance_rates=acceptance_rates,
        acc_cold_hist=np.asarray(acc_cold_hist, dtype=float),
        swap_attempts=int(swap_attempts),
        swap_accepts=int(swap_accepts),
        swap_rate=float(swap_rate),
        swap_try_edge=swap_try_edge,
        swap_acc_edge=swap_acc_edge,
        swap_rate_edge=swap_rate_edge,
    )

    return trace_cold, finals, stats