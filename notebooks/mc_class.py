"""
mc_class.py — lightweight plotting + notebook init for MATH 565
"""
# also sets highlight color

import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML

DEFAULT_HIGHLIGHT_COLOR = "#e6f7ff"   # light blue

def _inject_css(color: str) -> None:
    css = f"""
    <style>
    /* Works for any cell (code or markdown) if the cell has the 'highlight' tag */
    .tag_highlight {{
        background-color: {color} !important;
    }}

    /* Convenient class for Markdown cells so you don't repeat inline styles */
    .highlight-note {{
        background-color: {color} !important;
        padding: 10px;
        border-radius: 6px;
    }}
    </style>
    """
    display(HTML(css))

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
) -> None:
    """Set global plotting style, numeric safety, and notebook CSS."""
    # numeric safety
    np.seterr(divide="raise", invalid="raise")

    # style settings
    plt.rcParams.update({
        "font.family": font_family,
        "text.usetex": bool(use_tex),
        "mathtext.fontset": mathtext_fontset,
        "axes.labelsize": axes_labelsize,
        "axes.titlesize": axes_titlesize,
        "xtick.labelsize": tick_labelsize,
        "ytick.labelsize": tick_labelsize,
        "legend.fontsize": legend_fontsize,
        "legend.frameon": legend_frameon,
    })

    # notebook highlight CSS
    _inject_css(highlight_color)

def set_highlight_color(color: str = DEFAULT_HIGHLIGHT_COLOR) -> None:
    """Update the highlight color mid-notebook."""
    _inject_css(color)

def get_py_colors():
    """Return the default Matplotlib color cycle as a dict of 10 named colors."""
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    names = ["blue", "orange", "green", "red", "purple",
             "brown", "pink", "gray", "yellow", "cyan"]
    return dict(zip(names, color_cycle[:len(names)]))

def plot_rate_line(ax, x_range, y_start, rate,
                   color="black", label=None, ls="--"):
    """
    Plot a reference line showing O(n^{-rate}) on a log-log plot.
    """
    x0, x1 = x_range
    y0 = y_start
    y1 = y_start * (x1 / x0) ** (-rate)
    if label is None:
        label = rf"$\mathcal{{O}}(n^{{-{rate}}})$"
    ax.loglog([x0, x1], [y0, y1], color=color, linestyle=ls, label=label)
