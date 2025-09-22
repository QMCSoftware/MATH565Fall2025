def accept_reject(
    log_target_density,        # log of unnormalized target density, takes array (n,d) → array (n,)
    proposal_sampler,          # proposal sampler, proposal_sampler(n, rng) → array (n,d)
    log_prop_density=None,     # log proposal density, same vectorization as log_target_density. Optional.
    M=None,                    # constant ≥ sup_x target_density(x)/q(x). Required if log_prop_density is given.
    n_samples=1000,            # number of samples requested
    pilot_n=100,               # number of pilot samples to estimate acceptance rate
    batch_max=50000,           # maximum batch size, do not want to run out of memory
    max_proposals=None,        # maxmum number of proposals
    rng=None
):
    """
    Generic accept–reject sampling with batch sizing based on a pilot run.

    Modes:
    1) General AR (log_prop_density and M provided):
         Accept with prob = exp(log_target_density(x) - log_prop_density(x)) / M.
    2) Unit-peak mode (log_prop_density=None, M=None):
         Assumes 0 <= exp(log_target_density(x)) <= 1 and proposal is uniform on its support.
         Accept with prob = exp(log_target_density(x)).
    """
    rng = np.random.default_rng(rng)

    unit_peak_mode = (log_prop_density is None)
    if unit_peak_mode:
        if M is not None:
            raise ValueError("Do not provide M in unit-peak mode.")
        mode = "unit-peak"
    else:
        if M is None or M <= 0:
            raise ValueError("Must provide positive M in general AR mode.")
        mode = "general"

    accepted = []
    proposed_total = 0
    batches = 0

    def propose_and_accept(n_prop):
        """Draw proposals and apply accept–reject test."""
        x = proposal_sampler(n_prop, rng)   # shape (n_prop, d)
        if x.ndim != 2:
            raise ValueError("proposal_sampler must return a 2D array of shape (n, d).")

        lp = log_target_density(x)

        if unit_peak_mode:
            # acceptance prob = exp(log_target_density(x)), assumed in [0,1]
            a = np.exp(np.minimum(lp, 0.0))
        else:
            lq = log_prop_density(x)
            a = np.exp(lp - lq) / M
            a = np.minimum(a, 1.0)

        # Safety: zero-out non-finite probabilities
        a = np.where(np.isfinite(a) & (a >= 0), a, 0.0)

        u = rng.random(size=n_prop)
        acc = (u < a)
        return x, acc

    # --- Pilot run ---
    t0 = time.perf_counter()
    x_pilot, acc_pilot = propose_and_accept(pilot_n)
    pilot_acc_rate = float(acc_pilot.mean()) if pilot_n > 0 else 0.0
    accepted.append(x_pilot[acc_pilot])
    proposed_total += pilot_n
    batches += 1

    # Early exit if pilot already gave enough
    have = sum(chunk.shape[0] for chunk in accepted)
    if have >= n_samples:
        out = np.concatenate(accepted, axis=0)[:n_samples]
        info = dict(
            proposed=proposed_total,
            accepted=n_samples,
            pilot_accept_rate=pilot_acc_rate,
            final_accept_rate=n_samples / proposed_total,
            batches=batches,
            mode=mode,
            M=(None if unit_peak_mode else float(M)),
        )
        return out, info

    remaining = n_samples - have
    use_estimate = pilot_acc_rate > 0

    # --- Main loop ---
    while remaining > 0:
        if use_estimate:
            # overshoot by 10% for safety
            n_prop = int(np.ceil(1.10 * remaining / pilot_acc_rate))
        else:
            n_prop = batch_max

        n_prop = min(n_prop, batch_max)
        if (max_proposals is not None) and (proposed_total + n_prop > max_proposals):
            n_prop = max(0, max_proposals - proposed_total)
            if n_prop == 0:
                break

        x_batch, acc_batch = propose_and_accept(n_prop)
        accepted.append(x_batch[acc_batch])
        proposed_total += n_prop
        batches += 1
        remaining = n_samples - sum(chunk.shape[0] for chunk in accepted)

    got = sum(chunk.shape[0] for chunk in accepted)
    if got == 0:
        raise RuntimeError(
            "No samples were accepted. In general AR mode, check that your bound constant M is large enough. "
            "In unit-peak mode, check that your unnormalized density is between 0 and 1."
        )

    samples = np.concatenate(accepted, axis=0)
    if samples.shape[0] >= n_samples:
        samples = samples[:n_samples]

    info = dict(
        proposed=proposed_total,
        accepted=samples.shape[0],
        pilot_accept_rate=pilot_acc_rate,
        final_accept_rate=samples.shape[0] / proposed_total if proposed_total > 0 else 0.0,
        batches=batches,
        mode=mode,
        M=(None if unit_peak_mode else float(M)),
        elapsed_time = time.perf_counter() - t0
    )
    return samples, info