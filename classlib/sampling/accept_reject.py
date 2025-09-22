import numpy as np
import time

def accept_reject(
    log_target_density,        # log f(x): array (n,d) -> array (n,)
    proposal_sampler,          # proposal_sampler(n, rng) -> array (n,d)
    log_prop_density=None,     # log g(x): array (n,d) -> array (n,). Optional.
    M=None,                    # constant >= sup_x f/g (required if log_prop_density is given)
    n_samples=1000,            # number of accepted samples requested
    pilot_n=100,               # pilot proposals to estimate acceptance rate
    batch_max=50_000,          # upper bound per batch to avoid memory spikes
    max_proposals=None,        # hard cap on total proposals (optional)
    rng=None
):
    """
    Acceptance–Rejection (vectorized).

    Modes
    -----
    1) General AR (log_prop_density and M provided):
         accept if log U <= log f(x) - log g(x) - log M.
    2) Unit-peak mode (log_prop_density is None, no M):
         assumes 0 <= f(x) <= 1 (i.e., log f(x) <= 0); accept if log U <= log f(x).

    Returns
    -------
    samples : (n_samples, d) ndarray
    info    : dict with keys: proposed, accepted, pilot_accept_rate,
              final_accept_rate, batches, mode, M, elapsed_time
    """
    rng = np.random.default_rng(rng)

    unit_peak_mode = (log_prop_density is None)
    if unit_peak_mode:
        if M is not None:
            raise ValueError("Do not provide M in unit-peak mode.")
        mode = "unit-peak"
    else:
        if M is None or not np.isfinite(M) or M <= 0:
            raise ValueError("Must provide positive finite M in general AR mode.")
        mode = "general"
        logM = float(np.log(M))

    accepted_chunks = []
    proposed_total = 0
    batches = 0

    def _check_vec(name, arr, n_prop):
        arr = np.asarray(arr)
        if arr.ndim != 1 or arr.shape[0] != n_prop:
            raise ValueError(f"{name} must return shape ({n_prop},), got {arr.shape}.")
        return arr

    def propose_and_accept(n_prop):
        """Draw proposals and return (x, accept_mask)."""
        x = proposal_sampler(n_prop, rng)   # expect (n_prop, d)
        x = np.asarray(x, float)
        if x.ndim != 2:
            raise ValueError("proposal_sampler must return a 2D array of shape (n, d).")
        # log densities (vectorized)
        lp = _check_vec("log_target_density(x)", log_target_density(x), n_prop)

        if unit_peak_mode:
            # accept iff log U <= min(0, lp)
            log_thresh = np.minimum(0.0, lp)
        else:
            lq = _check_vec("log_prop_density(x)", log_prop_density(x), n_prop)
            log_thresh = np.minimum(0.0, (lp - lq - logM))

        # robust log-domain test
        log_u = np.log(rng.random(size=n_prop))
        acc = (log_u <= log_thresh)
        return x, acc

    t0 = time.perf_counter()

    # --- Pilot run ---
    pilot_n = int(max(0, pilot_n))
    if pilot_n > 0:
        x_pilot, acc_pilot = propose_and_accept(pilot_n)
        pilot_acc_rate = float(acc_pilot.mean())
        accepted_chunks.append(x_pilot[acc_pilot])
        proposed_total += pilot_n
        batches += 1
    else:
        pilot_acc_rate = 0.0

    # Early exit if pilot already satisfied the quota
    have = sum(chunk.shape[0] for chunk in accepted_chunks)
    if have >= n_samples:
        out = np.concatenate(accepted_chunks, axis=0)[:n_samples]
        info = dict(
            proposed=proposed_total,
            accepted=n_samples,
            pilot_accept_rate=pilot_acc_rate,
            final_accept_rate=n_samples / proposed_total if proposed_total else 0.0,
            batches=batches,
            mode=mode,
            M=(None if unit_peak_mode else float(M)),
            elapsed_time=time.perf_counter() - t0,
        )
        return out, info

    remaining = n_samples - have
    use_estimate = pilot_acc_rate > 0

    # --- Main loop ---
    while remaining > 0:
        if use_estimate:
            # propose ~ (remaining / acc_rate) with a small overshoot
            n_prop = int(np.ceil(1.10 * remaining / pilot_acc_rate))
        else:
            n_prop = int(batch_max)

        n_prop = max(1, min(n_prop, int(batch_max)))

        if (max_proposals is not None) and (proposed_total + n_prop > max_proposals):
            n_prop = int(max(0, max_proposals - proposed_total))
            if n_prop == 0:
                break

        x_batch, acc_batch = propose_and_accept(n_prop)
        accepted_chunks.append(x_batch[acc_batch])
        proposed_total += n_prop
        batches += 1
        remaining = n_samples - sum(chunk.shape[0] for chunk in accepted_chunks)

    got = sum(chunk.shape[0] for chunk in accepted_chunks)
    if got == 0:
        raise RuntimeError(
            "No samples were accepted. In general AR mode, check that M bounds f/g. "
            "In unit-peak mode, ensure log_target_density(x) <= 0 (i.e., f(x) ≤ 1) on the support."
        )

    samples = np.concatenate(accepted_chunks, axis=0)
    if samples.shape[0] >= n_samples:
        samples = samples[:n_samples]

    info = dict(
        proposed=proposed_total,
        accepted=samples.shape[0],
        pilot_accept_rate=pilot_acc_rate,
        final_accept_rate=(samples.shape[0] / proposed_total) if proposed_total else 0.0,
        batches=batches,
        mode=mode,
        M=(None if unit_peak_mode else float(M)),
        elapsed_time=time.perf_counter() - t0,
    )
    return samples, info