"""
nbviz.py — lightweight plotting & notebook init utilities
Author: ChatGPT (GPT-5 Thinking)

Features
--------
- One-call plotting style setup with optional LaTeX text (`init`).
- Paul Tol's Bright palette helpers + easy color cycle (`set_tol_color_cycle`).
- Session configuration for figure paths, save format, and epsilon (`configure`).
- Convenient `savefig("name")` that respects configured path/format.
- Log–log trend-line fit + overlay (`fit_log_trend`, `plot_log_trend_line`).
- Simple notebook highlight CSS injection for tagged cells (id="nbviz-highlight").
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from IPython.display import display, HTML
from cycler import cycler

__all__ = [
    "init", "configure", "savefig",
    "set_tol_color_cycle", "set_highlight_color",
    "fit_log_trend", "plot_log_trend_line",
    "TOL_BRIGHT", "TOL_BRIGHT_ORDER", "TINY",
]

# ---- Defaults / constants ----
DEFAULT_HIGHLIGHT_COLOR = "#e6f7ff"   # light blue (for markdown/cell adornment)

TOL_BRIGHT = {
    "blue":   "#4477AA",
    "cyan":   "#66CCEE",
    "green":  "#228833",
    "yellow": "#CCBB44",
    "red":    "#EE6677",
    "purple": "#AA3377",
    "gray":   "#BBBBBB",
}
TOL_BRIGHT_ORDER: list[str] = ["blue", "cyan", "green", "yellow", "red", "purple", "gray"]

# ---- Session state (configured via configure()) ----
FIGPATH: Path | None = None
SAVEFIGS: bool = False            # default: don't save unless user asks
IMGFRMT: str = "pdf"
TINY: float = 1e-9                # small epsilon, exposed as public constant


# ---- Internal helpers ----

def _inject_css(color: str) -> None:
    """Insert a style tag that colors cells tagged 'highlight'. Scoped; no hiding."""
    css = f"""
    <style id="nbviz-highlight">
      .jp-Cell[data-tags~="highlight"] {{
        box-shadow: inset 4px 0 0 {color};
        background: rgba(230,247,255,0.35);
      }}
      .highlight-note {{
        padding: 0.75em 1em;
        border-left: 5px solid {color};
        background-color: #e3f3f9;
        border-radius: 6px;
        margin: 1em 0;
      }}
      .highlight-note strong {{
        color: #224466;
      }}
      .highlight-note em {{
        color: #2c3e50;
      }}
    </style>
    """
    try:
        display(HTML(css))
    except Exception:
        # If display isn't available (e.g., non-notebook), just skip.
        pass

def _tol_list(order: Iterable[int | str] | None = None) -> list[str]:
    """Return Tol Bright hexes in requested order (names or 1-based indices)."""
    if order is None:
        keys = TOL_BRIGHT_ORDER
    else:
        keys = []
        for o in order:
            if isinstance(o, str):
                keys.append(o)
            else:
                i = int(o)
                if not (1 <= i <= len(TOL_BRIGHT_ORDER)):
                    raise IndexError(f"Tol index {i} out of range 1..{len(TOL_BRIGHT_ORDER)}")
                keys.append(TOL_BRIGHT_ORDER[i - 1])
    return [TOL_BRIGHT[k] for k in keys]


def _clean_xyw(
    x: Iterable[float],
    y: Iterable[float],
    n_which: slice | np.ndarray | None = None,
    w: float | Iterable[float] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Shared cleaner for log–log fitting: selects, weights, and filters finite/positive."""
    x_arr = np.asarray(list(x), dtype=float).ravel()
    y_arr = np.asarray(list(y), dtype=float).ravel()
    if n_which is not None:
        x_arr = x_arr[n_which].ravel()
        y_arr = y_arr[n_which].ravel()

    if w is None:
        w_arr = np.sqrt(1.0 / x_arr)  # good for linearly spaced x
    elif np.isscalar(w):
        w_arr = np.full_like(x_arr, float(w), dtype=float)
    else:
        w_arr = np.asarray(list(w), dtype=float).ravel()
        if n_which is not None:
            w_arr = w_arr[n_which].ravel()

    mask = np.isfinite(x_arr) & np.isfinite(y_arr) & (x_arr > 0) & (y_arr > 0)
    x_arr, y_arr, w_arr = x_arr[mask], y_arr[mask], w_arr[mask]

    if x_arr.size < 2:
        raise ValueError("Need at least two valid (x,y) points with x>0, y>0 for log–log fit.")
    return x_arr, y_arr, w_arr


# ---- Public: setup / configuration ----

def init(
    *,
    font_family: str = "serif",
    use_tex: bool = True,
    mathtext_fontset: str = "dejavuserif",
    axes_labelsize: int = 18,
    axes_titlesize: int = 18,
    tick_labelsize: int = 14,
    legend_fontsize: int = 14,
    legend_frameon: bool = False,
    highlight_color: str = DEFAULT_HIGHLIGHT_COLOR,
    set_tol_cycle: bool = True,
) -> None:
    """
    Set global plotting style and inject notebook CSS.

    Notes:
    - No stdout/display publisher manipulation here.
    - We enable interactive plotting (`plt.ion()`) for notebook friendliness.
    """
    np.seterr(divide="raise", invalid="raise")

    rc = {
        "font.family": font_family,
        "text.usetex": bool(use_tex),
        "axes.labelsize": axes_labelsize,
        "axes.titlesize": axes_titlesize,
        "xtick.labelsize": tick_labelsize,
        "ytick.labelsize": tick_labelsize,
        "legend.fontsize": legend_fontsize,
        "legend.frameon": legend_frameon,
    }
    if not use_tex:
        rc["mathtext.fontset"] = mathtext_fontset  # only relevant when not using TeX
    mpl.rcParams.update(rc)

    # Friendly defaults for saving and layout
    mpl.rcParams.setdefault("savefig.bbox", "tight")
    mpl.rcParams.setdefault("figure.autolayout", True)

    if set_tol_cycle:
        set_tol_color_cycle()

    _inject_css(highlight_color)

    # Make sure figures display inline without requiring explicit plt.show()
    try:
        plt.ion()
        try:
            import matplotlib_inline.backend_inline as be
            be.set_matplotlib_formats("png")
        except Exception:
            pass
    except Exception:
        pass


def configure(
    *,
    figpath: str | Path | None = None,
    savefigs: bool = False,
    imgfrmt: str = "pdf",
    tiny: float = 1e-9,
    make_dirs: bool = True,
    set_savefig_rc: bool = True,
    transparent: bool = False,
) -> None:
    """Set session-wide figure/output defaults for notebooks."""
    global FIGPATH, SAVEFIGS, IMGFRMT, TINY
    FIGPATH = Path(figpath) if figpath is not None else None
    SAVEFIGS = bool(savefigs)
    IMGFRMT = str(imgfrmt).lower()
    TINY = float(tiny)

    if make_dirs and FIGPATH is not None:
        try:
            FIGPATH.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    if set_savefig_rc:
        mpl.rcParams.update({
            "savefig.format": IMGFRMT,
            "savefig.bbox": "tight",
            "savefig.transparent": bool(transparent),
            # editable text in pdf/ps (so text stays text in Adobe/Keynote)
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        })


def savefig(name: str, *, ext: str | None = None, **kwargs) -> None:
    """Save the current figure if saving is enabled and a figpath is set.
    If saving is disabled or no figpath is configured, do nothing.
    """
    if not SAVEFIGS or FIGPATH is None:
        return
    suffix = (ext or IMGFRMT).lstrip(".")
    outfile = FIGPATH / f"{name}.{suffix}"
    plt.gcf().savefig(outfile, **kwargs)


# ---- Public: color utilities ----

def set_tol_color_cycle(
    *,
    order: Iterable[int | str] | None = None,
    axes: mpl.axes.Axes | None = None
) -> None:
    """Set the Tol Bright color cycle globally (rcParams) or for a single Axes."""
    cycle = cycler(color=_tol_list(order))
    if axes is None:
        mpl.rcParams["axes.prop_cycle"] = cycle
    else:
        axes.set_prop_cycle(cycle)


def set_highlight_color(color: str = DEFAULT_HIGHLIGHT_COLOR) -> None:
    """Update the highlight color mid-notebook (replaces style block)."""
    _inject_css(color)


# ---- Public: log–log trend fitting and plotting ----

def fit_log_trend(
    x: Iterable[float],
    y: Iterable[float],
    n_which: slice | np.ndarray | None = None,
    w: float | Iterable[float] | None = None,
) -> tuple[float, float]:
    """
    Fit log(y) ~ slope * log(x) + intercept on the selected data.

    Returns
    -------
    power : float
        The slope in log–log space (often negative for decays).
    coef : float
        exp(intercept), so the fitted model is y ≈ coef * x**power.
    """
    x_arr, y_arr, w_arr = _clean_xyw(x, y, n_which, w)
    slope, intercept = np.polyfit(np.log(x_arr), np.log(y_arr), deg=1, w=w_arr)
    power = float(slope)
    coef = float(np.exp(intercept))
    return power, coef


def plot_log_trend_line(
    ax: plt.Axes,
    x: Iterable[float],
    y: Iterable[float],
    *,
    n_which: slice | np.ndarray | None = None,
    w: float | Iterable[float] | None = None,
    endpoints: str | tuple[float, float] = "data",
    color: str | None = None,
    ls: str = "--",
    label: str | None = None,
    show_as_rate: bool = True,
    decimals: int = 2,
) -> tuple[float, float]:
    """
    Fit y ≈ coef * x**power on log–log, then plot a guide line through chosen endpoints.

    Parameters
    ----------
    endpoints : "data" | "ends" | (x0, x1)
        - "data": from min(x_sel) to max(x_sel) after cleaning
        - "ends": from first to last in the (cleaned) order
        - (x0, x1): explicit numeric endpoints
    """
    x_sel, y_sel, w_sel = _clean_xyw(x, y, n_which, w)
    power, coef = fit_log_trend(x_sel, y_sel, w=w_sel)

    if isinstance(endpoints, tuple) and len(endpoints) == 2:
        x0, x1 = map(float, endpoints)
    elif endpoints == "ends":
        x0, x1 = float(x_sel[0]), float(x_sel[-1])
    else:  # "data"
        x0, x1 = float(np.min(x_sel)), float(np.max(x_sel))

    y0 = coef * (x0 ** power)
    y1 = coef * (x1 ** power)

    if label is None:
        if show_as_rate:
            rate = -power
            label = rf"$\mathcal{{O}}(n^{{-{rate:.{decimals}f}}})$"
        else:
            label = rf"$\mathcal{{O}}(n^{{{power:.{decimals}f}}})$"

    ax.loglog([x0, x1], [y0, y1], color=color, linestyle=ls, label=label)
    return power, coef


def plot_power_line(
    ax: plt.Axes,
    x: Iterable[float] | tuple[float, float],
    *,
    power: float,
    coef: float | None = None,
    anchor: tuple[float, float] | None = None,  # (x_ref, y_ref) to infer coef if coef is None
    endpoints: str | tuple[float, float] | None = None,
    color: str | None = None,
    ls: str = "--",
    label: str | None = None,
    show_as_rate: bool = True,
    decimals: int = 2,
):
    """
    Plot y = coef * x**power on log–log between chosen endpoints.

    Parameters
    ----------
    x : array-like or (x0, x1)
        If array-like, we use first→last unless `endpoints` overrides.
        If a 2-tuple, it's treated as explicit (x0, x1).
    power : float
        The log–log slope (decays typically have negative power).
    coef : float, optional
        Coefficient in y = coef * x**power. If omitted, `anchor` must be given.
    anchor : (x_ref, y_ref), optional
        If provided (and `coef` is None), we set coef = y_ref / x_ref**power.
    endpoints : "data" | "ends" | (x0, x1) | None
        - "data": span min(x)→max(x) if x is array-like
        - "ends": span first→last of x (after flattening)
        - (x0, x1): explicit endpoints
        - None: if x is a 2-tuple, use it; else use "ends".
    color, ls, label : styling
    show_as_rate : bool
        If True, label as O(n^{-alpha}) with alpha = -power; else O(n^{power}).
    decimals : int
        Digits in the default label.

    Returns
    -------
    power, coef : tuple[float, float]
        The (power, coef) actually used to draw the line.
    """
    # Resolve endpoints
    if isinstance(x, tuple) and len(x) == 2 and endpoints is None:
        x0, x1 = float(x[0]), float(x[1])
    else:
        xs = np.asarray(list(x), float).ravel()
        if endpoints is None or endpoints == "ends":
            if xs.size < 2:
                raise ValueError("Need at least two x values or a 2-tuple for endpoints.")
            x0, x1 = float(xs[0]), float(xs[-1])
        elif endpoints == "data":
            x0, x1 = float(np.min(xs)), float(np.max(xs))
        elif isinstance(endpoints, tuple) and len(endpoints) == 2:
            x0, x1 = map(float, endpoints)
        else:
            raise ValueError("Invalid `endpoints`. Use 'data', 'ends', a 2-tuple, or None.")

    if x0 <= 0 or x1 <= 0:
        raise ValueError("Endpoints must be positive for log–log plotting.")

    # Determine coefficient
    if coef is None:
        if anchor is None:
            raise ValueError("Provide either `coef` or `anchor=(x_ref, y_ref)`.")
        x_ref, y_ref = map(float, anchor)
        if x_ref <= 0 or y_ref <= 0:
            raise ValueError("Anchor must have positive x_ref and y_ref.")
        coef = float(y_ref / (x_ref ** power))
    else:
        coef = float(coef)

    # Build points
    y0 = coef * (x0 ** power)
    y1 = coef * (x1 ** power)

    # Default label
    if label is None:
        if show_as_rate:
            alpha = -power
            label = rf"$\mathcal{{O}}(n^{{-{alpha:.{decimals}f}}})$"
        else:
            label = rf"$\mathcal{{O}}(n^{{{power:.{decimals}f}}})$"

    ax.loglog([x0, x1], [y0, y1], color=color, linestyle=ls, label=label)
    return float(power), float(coef)