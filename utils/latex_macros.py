# utils/latex_macros.py
from IPython.display import HTML, display
import json

# Edit these in one place:
DEFAULT_MACROS = {
    # vectors / matrices
    "vt": r"\boldsymbol{t}",
    "vx": r"\boldsymbol{x}",
    "vX": r"\boldsymbol{X}",
    # sets/operators
    "cf": r"\mathcal{F}",
    "cu": r"\mathcal{U}",
    "Ex": r"\mathbb{E}",
    "dif": r"\mathrm{d}",
    # operator names
    "disc": r"\operatorname{disc}",
    # norms: \norm{x} or \norm[2]{x}
    "norm": [r"\left\lVert #2 \right\rVert_{#1}", 2],
}

def latex_preamble(macros: dict | None = None) -> str:
    """
    Build a LaTeX preamble string for Matplotlib's text.latex.preamble based on macros.
    Only supports simple \newcommand and \DeclareMathOperator equivalents.
    """
    m = macros or DEFAULT_MACROS
    lines = [
        r"\usepackage{amsmath,amssymb,bm}",
        r"\usepackage{mathtools}",
    ]
    for k, v in m.items():
        if isinstance(v, list) and len(v) == 2 and isinstance(v[1], int):
            # e.g., ["\\left...#1...", 2]  -> \newcommand{\norm}[2]{...}
            lines.append(rf"\newcommand{{\{k}}}[{v[1]}]{{{v[0]}}}")
        else:
            # \operatorname or direct newcommand
            if v.startswith(r"\operatorname"):
                # \DeclareMathOperator{\disc}{disc} equivalent (best-effort)
                inner = v.removeprefix(r"\operatorname").strip("{}")
                # inner looks like {disc}, but we don't know the operator word;
                # fallback to a newcommand using \operatorname{name}(#1 optional not supported)
                lines.append(rf"\newcommand{{\{k}}}{{{v}}}")
            else:
                lines.append(rf"\newcommand{{\{k}}}{{{v}}}")
    return "\n".join(lines)

def load_mathjax_macros(macros: dict | None = None):
    """
    Register TeX macros in MathJax v3 (for Markdown cells).
    Call once per notebook (e.g., from notebook_header).
    """
    macros = macros or DEFAULT_MACROS
    cfg = {"tex": {"macros": macros}}
    script = f"""
    <script>
    window.MathJax = window.MathJax || {{}};
    const incoming = {json.dumps(cfg)};
    window.MathJax.tex = Object.assign({{}}, window.MathJax.tex, {{
      macros: Object.assign({{}},
        (window.MathJax.tex && window.MathJax.tex.macros) || {{}},
        incoming.tex.macros
      )
    }});
    if (window.MathJax && window.MathJax.typesetPromise) {{
      MathJax.typesetPromise();
    }} else if (window.MathJax && window.MathJax.typeset) {{
      MathJax.typeset();
    }}
    </script>
    """
    display(HTML(script))