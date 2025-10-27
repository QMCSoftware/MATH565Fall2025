import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, Optional, Tuple, Dict, Any, Union, Mapping, overload
from classlib.nbviz import TOL_BRIGHT, TOL_BRIGHT_ORDER # dict of named Tol colors

def plot_middle_half_sample_mean(
    sampler: Callable[..., np.ndarray],
    f: Callable[[np.ndarray], np.ndarray],
    n_max: int = 2**15,
    n_rep: int = 51,
    n_start: int = 9,
    *,
    rng: Optional[Union[int, np.random.Generator]] = None,
    ax: Optional[plt.Axes] = None,
    label: Optional[str] = None,
    color: Optional[str] = None,
    show_ci: bool = True,
    ci_level: float = 0.99,
    iqr_alpha: float = 0.20,
) -> Tuple[plt.Axes, Dict[str, Any]]:
    """
    Plot the middle half (IQR band) of the running sample mean of Y = f(X) vs. n,
    across `n_rep` independent replications up to `n_max` samples each.

    Parameters
    ----------
    sampler : callable
        `sampler(size, rng=...) -> array_like` returning X samples shaped (size, ...).
        If your sampler ignores `rng`, that's fine.
    f : callable
        Function applied elementwise/broadcasted to X to produce Y.
    n_max : int, default 2**15
        Maximum number of samples per replication. (For QMC, keep this a power of two.)
    n_rep : int, default 21
        Number of independent replications.
    n_start : int, default 9
        First index (1-based n = n_start+1) shown in the plot (avoids the noisy tiny-n tail).
    rng : int | np.random.Generator | None, default None
        Random seed or Generator. If int/None, a fresh Generator is made.
        Replications use independent substreams via SeedSequence.spawn.
    ax : matplotlib.axes.Axes or None
        If None, a new figure/axes is created.
    label : str or None
        Legend label for the median curve. Defaults to `f.__name__` if available.
    color : str or None
        Override color for band and curves.
    show_ci : bool, default True
        If True, overlay a normal-approximation CI for the *median across reps* at each n.
    ci_level : float, default 0.99
        Confidence level for dashed CI curves (two-sided, normal z).
    iqr_alpha : float, default 0.20
        Alpha for the shaded IQR band.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot.
    info : dict
        Dictionary with arrays:
        { "n", "cum_means", "q25", "median", "q75", "ci_lower", "ci_upper" }.
    """
    # -- validate and set up ---------------------------------------------------
    n_max = int(n_max)
    n_rep = int(n_rep)
    if n_max <= 0 or n_rep <= 0:
        raise ValueError("n_max and n_rep must be positive.")

    # Helpful guard for QMC folks (non-fatal)
    def _is_power_of_two(k: int) -> bool:
        return k > 0 and (k & (k - 1) == 0)
    if not _is_power_of_two(n_max):
        # Keep going; the method still works fine for MC/MCMC.
        pass

    # RNG: independent substreams per replication
    if isinstance(rng, np.random.Generator):
        base_ss = np.random.SeedSequence()  # we’ll split the provided generator anyway
    else:
        base_ss = np.random.SeedSequence(None if rng is None else int(rng))
    child_seqs = base_ss.spawn(n_rep)
    rep_rngs = [np.random.default_rng(s) for s in child_seqs]

    # -- run replications ------------------------------------------------------
    cum_means = np.empty((n_rep, n_max), dtype=float)

    for r in range(n_rep):
        # Sampler signature: sampler(size) — if sampler ignores rng, fine.
        X = sampler(n_max)
        Y = f(X)
        Y = np.asarray(Y, dtype=float).reshape(-1)[:n_max]  # 1D, length n_max
        csum = np.add.accumulate(Y)                         # cumulative sums
        cum_means[r] = csum / np.arange(1, n_max + 1, dtype=float)

    # -- aggregate across replications at each n -------------------------------
    q25   = np.percentile(cum_means, 25, axis=0)
    med   = np.percentile(cum_means, 50, axis=0)
    q75   = np.percentile(cum_means, 75, axis=0)

    # CI for the *median across reps* (via SE of med ≈ 1.253 * SE of mean across reps)
    # First compute across-rep SD at each n:
    sd_across_rep = np.std(cum_means, axis=0, ddof=1)
    sd_mean_final = sd_across_rep[-1]
    se_mean_across_rep = sd_across_rep / np.sqrt(n_rep)
    # For normal-ish across-rep distributions, SE(median) ≈ 1.253 * SE(mean)
    se_median_across_rep = 1.253314137 * se_mean_across_rep
    if show_ci:
        from math import erf, sqrt
        # Invert Phi for two-sided (1 - alpha/2)
        alpha = 1.0 - float(ci_level)
        # simple normal-quantile via erf^{-1}
        # q = Phi^{-1}(1 - alpha/2) = sqrt(2) * erfinv(1 - alpha)
        # implement erfinv using numpy for portability if available:
        try:
            from numpy import erfinv as _erfinv
        except Exception:
            # fallback: quick approximation of z for common levels
            z = {0.90:1.6449, 0.95:1.96, 0.975:2.241, 0.99:2.5758, 0.999:3.2905}.get(ci_level, 2.5758)
        else:
            z = np.sqrt(2.0) * _erfinv(1.0 - alpha)
        ci_lower = med - z * se_median_across_rep
        ci_upper = med + z * se_median_across_rep
    else:
        ci_lower = np.full_like(med, np.nan)
        ci_upper = np.full_like(med, np.nan)

    n = np.arange(1, n_max + 1)

    # -- plotting --------------------------------------------------------------
    if ax is None:
        _, ax = plt.subplots(figsize=(7.2, 4.5))
    ax.set_xscale("log")

    # IQR band
    ax.fill_between(n[n_start:], q25[n_start:], q75[n_start:], alpha=iqr_alpha, color=color)

    # Median curve
    the_label = label if label is not None else getattr(f, "__name__", "Median")
    ax.semilogx(n[n_start:], med[n_start:], linewidth=2, label=the_label, color=color)

    # CI curves (dashed)
    if show_ci:
        ax.semilogx(n[n_start:], ci_lower[n_start:], "--", linewidth=1, color=color)
        ax.semilogx(n[n_start:], ci_upper[n_start:], "--", linewidth=1, color=color)

    ax.set_xlabel("Number of samples $n$")
    ax.set_ylabel(r"Running sample mean $\hat{\mu}_n$")
    ax.set_title(r"IQR (shaded) and CI (dashed) of running mean vs. $n$")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.legend()
    plt.tight_layout()

    info = dict(
        n=n,
        cum_means=cum_means,
        q25=q25,
        median=med,
        q75=q75,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        sd_across_rep=sd_across_rep,
        sd_mean_final=sd_mean_final,
    )
    return ax, info

def plot_multiple_middle_half_sample_means(
    configs: Mapping[str, Any],
    *,
    n_max: int = 2**15,
    n_rep: int = 21,
    n_start: int = 9,
    default_sampler: Callable[[int], Any] | None = None,
    default_f: Callable[[Any], Any] | None = None,
    colors: Mapping[str, str] | None = None,
    title: str | None = None,
    legend_loc: str | None = "outside",
    ylim: tuple[float, float] | None = None,
    figsize: tuple[float, float] = (10.2, 6),
):
    """
    Compare running means for multiple (sampler, f) combinations.

    Each entry in `configs` may be:
      - dict: {"sampler": callable, "f": callable, ["color": "#hex", "label": "..."]}
      - tuple: (sampler, f)
      - callable: sampler only (requires `default_f`)
    Missing "sampler" or "f" fall back to `default_sampler` / `default_f`.
    """
    fig, ax = plt.subplots(figsize=figsize)
    info_dict: Dict[str, Dict[str, Any]] = {}

    # Default color cycling from Tol Bright if none provided
    if colors is None:
        labels = list(configs.keys())
        tol_list = [TOL_BRIGHT[name] for name in TOL_BRIGHT_ORDER]
        colors = {lab: tol_list[i % len(tol_list)] for i, lab in enumerate(labels)}

    for label, cfg in configs.items():
        # Normalize entry
        if isinstance(cfg, tuple) and len(cfg) == 2:
            sampler, f = cfg
            cfg_dict: Dict[str, Any] = {}
        elif callable(cfg):
            sampler, f = cfg, default_f
            cfg_dict = {}
        elif isinstance(cfg, dict):
            sampler = cfg.get("sampler", default_sampler)
            f = cfg.get("f", default_f)
            cfg_dict = cfg
        else:
            raise TypeError(
                f"Config for '{label}' must be dict, (sampler, f) tuple, or callable sampler."
            )

        if sampler is None or f is None:
            raise ValueError(
                f"Config '{label}' missing sampler or f (and no default provided)."
            )

        # Style (per-entry overrides > auto-colors)
        color = cfg_dict.get("color", colors.get(label))
        this_label = cfg_dict.get("label", label)

        # Plot one curve
        ax, info = plot_middle_half_sample_mean(
            sampler=sampler,
            f=f,
            n_max=n_max,
            n_rep=n_rep,
            n_start=n_start,
            ax=ax,
            label=this_label,
            color=color,
        )

        # Append SD(final n) to legend & store in output dict
        sd_final = info.get("sd_mean_final")
        if sd_final is not None:
            n_final = int(info["n"][-1])
            label_with_sd = (
                rf"{this_label} "
                rf"($\mathrm{{SD}}[\hat\mu_{{{n_final}}}]\approx{sd_final:.2e}$)"
            )
            # Update the matching line's label
            for ln in reversed(ax.get_lines()):
                if ln.get_label() == this_label:
                    ln.set_label(label_with_sd)
                    # If you want to ensure a color is stored, you can also grab it here:
                    if color is None:
                        color = ln.get_color()
                    break
            # <<< make sure to update this_label for storing/display later
            this_label = label_with_sd

        # Store for reuse in zoom
        info["sd_mean_final"] = float(sd_final) if sd_final is not None else None
        info["display_label"] = this_label
        # Store a concrete color (fallback to the plotted line color if color was None)
        if color is None:
            # last plotted line corresponds to this series
            color = ax.get_lines()[-1].get_color()
        info["color"] = color

        info_dict[label] = info

    # Title
    if title:
        ax.set_title(title)

    # Legend placement
    if legend_loc == "outside":
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    else:
        ax.legend(loc=legend_loc)

    # Optional y-axis limits
    if ylim is not None:
        ax.set_ylim(*ylim)

    plt.tight_layout()
    return ax, info_dict
