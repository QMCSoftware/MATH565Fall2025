"""
mc_class.py — lightweight plotting + notebook init for MATH 565
Author: ChatGPT (GPT-5 Thinking)
"""

from __future__ import annotations

import re
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from IPython.display import display, HTML

# ---- Defaults ----
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

# ---- Internal helpers ----

def _inject_css(color: str) -> None:
    """Inject CSS to style cells tagged 'highlight' and a .highlight-note helper.
    Works in JupyterLab Desktop and VS Code notebooks.
    """
    css = f"""
    <style>
    /* Any cell that has the 'highlight' tag */
    .jp-Cell[data-tags~="highlight"] {{
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


def _merge_latex_preamble(extra: str) -> None:
    """Append LaTeX preamble lines idempotently when text.usetex=True.

    - Ensures \\usepackage{{xcolor}} is present before any \\definecolor.
    - Avoids duplicate identical segments.
    """
    pre = mpl.rcParams.get("text.latex.preamble", "")
    pre_str = pre if isinstance(pre, str) else "\n".join(pre)

    # Ensure xcolor is loaded if we plan to define or use colors
    if "\\usepackage{xcolor}" not in pre_str:
        pre_str += ("" if pre_str.endswith("\n") or pre_str == "" else "\n") + r"\usepackage{xcolor}"

    # Append the extra block if it isn't already present
    if extra and extra not in pre_str:
        pre_str += ("" if pre_str.endswith("\n") else "\n") + extra

    mpl.rcParams["text.latex.preamble"] = pre_str


def _looks_hex(color: str) -> bool:
    return isinstance(color, str) and bool(re.fullmatch(r"#?[0-9A-Fa-f]{6}", color.strip("#")))


# ---- Public API ----

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
    define_tol_colors: bool = True,
) -> None:
    """Set global plotting style, numeric safety, and notebook CSS.

    Parameters
    ----------
    font_family : str
        Matplotlib rcParam \"font.family\".
    use_tex : bool
        If True, enable LaTeX text rendering (requires a TeX distro).
        Note: when True, mathtext fontset is ignored.
    mathtext_fontset : str
        Used only when use_tex=False.
    define_tol_colors : bool
        When use_tex=True, defines LaTeX color names for Paul Tol's palette.
        Adds: tolblue, tolcyan, tolgreen, tolyellow, tolred, tolpurple, tolgray.
    """
    # numeric safety
    np.seterr(divide="raise", invalid="raise")

    # style settings
    mpl.rcParams.update({
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

    if use_tex:
        # Ensure xcolor is loaded, and optionally define Tol colors
        extra = ""
        if define_tol_colors:
            defines = []
            for name, hexval in TOL_BRIGHT.items():
                defines.append(rf"\definecolor{{tol{name}}}{{HTML}}{{{hexval.lstrip('#')}}}")
            extra = "\n".join(defines)
        _merge_latex_preamble(extra)

    # notebook highlight CSS
    _inject_css(highlight_color)


def set_highlight_color(color: str = DEFAULT_HIGHLIGHT_COLOR) -> None:
    """Update the highlight color mid-notebook."""
    _inject_css(color)


def get_py_colors() -> dict[str, str]:
    """Return the default Matplotlib color cycle as a dict of 10 named colors."""
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    names = ["blue", "orange", "green", "red", "purple",
             "brown", "pink", "gray", "yellow", "cyan"]
    return dict(zip(names, color_cycle[:len(names)]))


def get_tol_colors() -> dict[str, str]:
    """Return Paul Tol's Bright 7-color palette as a dict of hex strings."""
    return dict(TOL_BRIGHT)


def enable_tol_latex_colors() -> None:
    """(Re)define LaTeX color names for Tol palette.

    Safe to call multiple times. Requires text.usetex=True.
    Defines: \\color{{tolblue}}, \\color{{tolcyan}}, \\color{{tolgreen}},
             \\color{{tolyellow}}, \\color{{tolred}}, \\color{{tolpurple}}, \\color{{tolgray}}.
    """
    if not mpl.rcParams.get("text.usetex", False):
        raise RuntimeError("enable_tol_latex_colors requires text.usetex=True")

    defines = []
    for name, hexval in TOL_BRIGHT.items():
        defines.append(rf"\definecolor{{tol{name}}}{{HTML}}{{{hexval.lstrip('#')}}}")
    _merge_latex_preamble("\n".join(defines))


def latex_colorize(text: str, color: str, *, usetex: bool | None = None) -> str:
    """Wrap `text` in a LaTeX color command appropriate to the current mode.

    - If usetex=True:
        * Named colors:  \\color{blue}{text}
        * Hex colors:    \\color[HTML]{4477AA}{text}  (xcolor)
    - If usetex=False (mathtext):
        * Only named colors are supported: \\color{blue}{text}
          (hex codes are not supported by mathtext).

    Parameters
    ----------
    text : str
        The text to wrap (no math delimiters).
    color : str
        A named color (e.g., \"blue\") or a hex string (\"#4477AA\" or \"4477AA\").
    usetex : bool | None
        Override autodetection of rcParams['text.usetex'] if provided.
    """
    if usetex is None:
        usetex = bool(mpl.rcParams.get("text.usetex", False))

    if usetex:
        if _looks_hex(color):
            hexval = color.lstrip("#")
            return rf"\color[HTML]{{{hexval}}}{{{text}}}"
        else:
            return rf"\color{{{color}}}{{{text}}}"
    else:
        if _looks_hex(color):
            raise ValueError("MathText mode does not support hex colors. Use a named color (e.g., 'blue').")
        return rf"\color{{{color}}}{{{text}}}"


def plot_rate_line(ax: plt.Axes,
                   x_range: tuple[float, float],
                   y_start: float,
                   rate: float,
                   color: str = "black",
                   label: str | None = None,
                   ls: str = "--") -> None:
    """Plot a reference line showing O(n^{-rate}) on a log-log plot."""
    x0, x1 = x_range
    y0 = y_start
    y1 = y_start * (x1 / x0) ** (-rate)
    if label is None:
        label = rf"$\mathcal{{O}}(n^{{-{rate}}})$"
    ax.loglog([x0, x1], [y0, y1], color=color, linestyle=ls, label=label)


# ---- Examples (strings only; remove or adapt in your notebook) ----
EXAMPLE_K_Q_LABEL_TOL = r"$" + \
    latex_colorize("k", "tolblue", usetex=True) + r",\ " + \
    latex_colorize("Q(p)", "tolgreen", usetex=True) + r"$"

EXAMPLE_K_Q_LABEL_HEX = r"$" + \
    latex_colorize("k", "#4477AA", usetex=True) + r",\ " + \
    latex_colorize("Q(p)", "#228833", usetex=True) + r"$"
