"""
notebook_header.py — portable header for VS Code, JupyterLab, and Colab.

- Adds <repo_root> and <repo_root>/utils to sys.path locally; clones in Colab.
- Always shows "Open in Colab" badge (inline).
- Injects a top Markdown cell with your LaTeX macros into the notebook file.
- Tries auto-imports + plotting prefs via utils/auto_imports.py.
- Colab: installs a LaTeX toolchain if missing (prints a 'may take several minutes' notice).
"""

from __future__ import annotations
import os, sys, re, subprocess, pathlib, shutil

# ---------------- State ----------------
_STATE = {"ran": False}
_NB_PATH = "unknown.ipynb"

# ------------- Basic env helpers -------------
def in_ipython() -> bool:
    try:
        get_ipython  # type: ignore
        return True
    except NameError:
        return False

def in_colab() -> bool:
    return ("COLAB_RELEASE_TAG" in os.environ) or ("COLAB_GPU" in os.environ)

# ------------- Repo / path helpers -------------
def get_repo_root() -> pathlib.Path | None:
    try:
        p = pathlib.Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip())
        return p if p.exists() else None
    except Exception:
        return None

def get_org_repo() -> tuple[str, str]:
    org = os.environ.get("BOOT_ORG")
    repo = os.environ.get("BOOT_REPO")
    if org and repo:
        return org, repo
    # Fallbacks
    return "QMCSoftware", "QMCSoftware"

def get_nb_override() -> str | None:
    # Notebook user_ns first
    try:
        if in_ipython():
            val = get_ipython().user_ns.get("NB_PATH")  # type: ignore
            if isinstance(val, str) and val.strip():
                return val
    except Exception:
        pass
    # Then env
    val = os.environ.get("NB_PATH")
    return val if val else None

def guess_nb_path(repo_root: pathlib.Path) -> str:
    try:
        import ipynbname
        p = pathlib.Path(ipynbname.path()).resolve()
        return str(p.relative_to(repo_root))
    except Exception:
        return "unknown.ipynb"

# ------------- Colab bootstrap -------------
def ensure_pip_packages(pkgs: list[str], quiet: bool = True) -> None:
    import importlib
    to_install = []
    for pkg in pkgs:
        mod = pkg.split("==")[0].split(">=")[0]
        try:
            importlib.import_module(mod)
        except Exception:
            to_install.append(pkg)
    if to_install:
        if not quiet:
            print("[notebook_header] pip install:", " ".join(to_install))
        subprocess.check_call([sys.executable, "-m", "pip", "install", *to_install])

def colab_bootstrap(org: str, repo: str, branch: str, quiet: bool = True) -> pathlib.Path:
    repo_dir = pathlib.Path("/content") / repo
    if not repo_dir.exists():
        if not quiet:
            print(f"[notebook_header] Cloning {org}/{repo}@{branch} (with submodules) ...")
        subprocess.check_call([
            "git","clone","--depth","1","--recurse-submodules",
            "-b", branch, f"https://github.com/{org}/{repo}.git", str(repo_dir)
        ])
    # Make sure submodules are present (e.g., qmcsoftware)
    subprocess.check_call(["git","-C",str(repo_dir),"submodule","sync","--recursive"])
    subprocess.check_call(["git","-C",str(repo_dir),"submodule","update","--init","--recursive","--depth","1"])

    # Common Python deps for header
    ensure_pip_packages(["numpy","scipy","matplotlib","pandas","ipynbname"], quiet=quiet)

    # Paths
    if str(repo_dir) not in sys.path:
        sys.path.insert(0, str(repo_dir))
    utils_dir = repo_dir / "utils"
    if str(utils_dir) not in sys.path:
        sys.path.insert(0, str(utils_dir))
    try:
        os.chdir(repo_dir)
    except Exception:
        pass
    return repo_dir

# ------------- LaTeX toolchain (Colab install + local guidance) -------------
def _have_tex_toolchain() -> bool:
    have_latex = shutil.which("latex") is not None
    have_dvipng = (shutil.which("dvipng") is not None) or (shutil.which("dvisvgm") is not None)
    have_gs = (shutil.which("gs") is not None) or (shutil.which("ghostscript") is not None)
    return have_latex and have_dvipng and have_gs

def ensure_latex_toolchain(quiet: bool = True) -> bool:
    """Colab: install LaTeX if missing (prints 'may take several minutes'). Local: no install."""
    if _have_tex_toolchain():
        return True
    if in_colab():
        try:
            print("[notebook_header] LaTeX not found — installing in Colab (this may take several minutes)...")
            subprocess.check_call(["bash","-lc","apt-get -y update"])
            subprocess.check_call([
                "bash","-lc",
                "apt-get -y install texlive-latex-extra texlive-fonts-recommended dvipng dvisvgm cm-super ghostscript"
            ])
            return _have_tex_toolchain()
        except Exception as e:
            print("[notebook_header] WARNING: LaTeX install failed; Matplotlib usetex may not work:", e)
            return False
    # Non-Colab: do nothing silently; you manage local TeX yourself.
    if not quiet:
        print("[notebook_header] LaTeX toolchain not found locally. Please install TeX (TeX Live / MiKTeX) and dvipng/ghostscript.")
    return False

# ------------- Colab badge -------------
def show_colab_button(org: str, repo: str, branch: str, nb_path: str) -> None:
    from IPython.display import HTML, display
    nb_quoted = nb_path.replace(" ", "%20")
    url = f"https://colab.research.google.com/github/{org}/{repo}/blob/{branch}/{nb_quoted}"
    html = (
        'If not running in <code>conda qmcpy</code>, open in '
        f'<a target="_blank" href="{url}"><img src="https://colab.research.google.com/assets/colab-badge.svg" '
        'alt="Open In Colab"/></a>.'
    )
    display(HTML(html))

# ------------- Auto-imports hook -------------
def try_auto_imports() -> None:
    try:
        try:
            from utils.auto_imports import inject_common  # preferred
        except ImportError:
            import auto_imports
            inject_common = auto_imports.inject_common
        ns = get_ipython().user_ns  # type: ignore
        verbose = os.environ.get("AUTO_IMPORTS_VERBOSE","0").lower() in ("1","true","yes")
        plot_prefs = os.environ.get("AUTO_PLOT_PREFS","0").lower() in ("1","true","yes")
        inject_common(ns, verbose=verbose, plot_prefs=plot_prefs)
    except Exception as e:
        print("[notebook_header] auto_imports failed:", e)


# ------------- Main -------------
def main(force: bool = False, quiet: bool = True):
    """Run header once; on subsequent calls, just re-render the badge."""
    global _NB_PATH

    if _STATE["ran"] and not force:
        # Re-render the badge so a re-run doesn't blank it out in some UIs
        try:
            org, repo = get_org_repo()
            branch = os.environ.get("BOOT_BRANCH", "main")
            show_colab_button(org, repo, branch, _NB_PATH)
        except Exception:
            pass
        return
    _STATE["ran"] = True

    repo_root = get_repo_root()
    org, repo = get_org_repo()
    branch = os.environ.get("BOOT_BRANCH", "main")

    # Resolve notebook path
    nb_override = get_nb_override()
    if nb_override:
        _NB_PATH = nb_override
    elif repo_root:
        _NB_PATH = guess_nb_path(repo_root)
    else:
        _NB_PATH = "unknown.ipynb"

    # Colab setup (clone + TeX install if missing)
    if in_colab():
        colab_bootstrap(org, repo, branch, quiet=quiet)
        ensure_latex_toolchain(quiet=True)

    # Local: add utils to path
    if repo_root and not in_colab():
        utils_dir = repo_root / "utils"
        if str(utils_dir) not in sys.path:
            sys.path.insert(0, str(utils_dir))
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))


    # Auto-imports + badge
    try_auto_imports()
    try:
        show_colab_button(org, repo, branch, _NB_PATH)
    except Exception:
        pass

def reload_header(quiet: bool = True):
    return main(force=True, quiet=quiet)

# Autorun (can disable via NOTEBOOK_HEADER_AUTORUN=0)
if os.environ.get("NOTEBOOK_HEADER_AUTORUN","1").lower() in ("1","true","yes"):
    if in_ipython():
        try:
            main(False)
        except Exception as e:
            print("[notebook_header] ERROR: autorun failed:", e)