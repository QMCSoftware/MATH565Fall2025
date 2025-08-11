"""
notebook_header.py — portable header for VS Code, JupyterLab, and Colab.

Keeps:
- Minimal output (quiet=True). Re-running re-renders the Colab badge.
- Detect org/repo/branch via env overrides (BOOT_ORG/BOOT_REPO/BOOT_BRANCH).
- Local: add <repo_root> and <repo_root>/utils to sys.path.
- Colab: clone/update repo + submodules; ensure qmcpy importable.
- Always show an "Open in Colab" badge (inline).
- Auto-imports (np/pd/plt/sp/sy/qp) + optional plot prefs via AUTO_PLOT_PREFS=1.

Removed:
- Any LaTeX macro injection or file edits. You’ll paste macros manually when needed.
"""

from __future__ import annotations
import os, sys, re, subprocess, pathlib
from typing import Optional, List

# --- State ---
_STATE = {"ran": False}
_NB_PATH = "unknown.ipynb"

# --- Defaults ---
DEFAULT_BOOT_BRANCH = (
    os.environ.get("BOOT_BRANCH")
    or os.environ.get("QMCSOFTWARE_REF")
    or "bootstrap_colab"
)

# =============================================================================
# Environment helpers
# =============================================================================
def in_ipython() -> bool:
    try:
        get_ipython  # type: ignore
        return True
    except NameError:
        return False

def in_colab() -> bool:
    return "COLAB_RELEASE_TAG" in os.environ or "COLAB_GPU" in os.environ

def conda_env_name() -> Optional[str]:
    name = os.environ.get("CONDA_DEFAULT_ENV")
    if name:
        return name
    m = re.search(r"(?:^|[/\\\\])envs[/\\\\]([^/\\\\]+)$", sys.prefix)
    return m.group(1) if m else None

def in_qmcpy_env() -> bool:
    env = (conda_env_name() or "").lower()
    if env == "qmcpy":
        return True
    return os.environ.get("QMCPY_ENV", "").lower() in ("1","true","yes","y")

# =============================================================================
# Git / repo helpers
# =============================================================================
def get_repo_root() -> Optional[pathlib.Path]:
    try:
        p = pathlib.Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip())
        return p if p.exists() else None
    except Exception:
        return None

def get_org_repo() -> tuple[str, str]:
    org = (globals().get("ORG") or os.environ.get("ORG")
           or os.environ.get("BOOT_ORG"))
    repo = (globals().get("REPO") or os.environ.get("REPO")
            or os.environ.get("BOOT_REPO"))
    if org and repo:
        return str(org), str(repo)
    try:
        url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], text=True
        ).strip()
    except Exception:
        url = ""
    m = re.search(r"[:/](?P<org>[^/]+)/(?P<repo>[^/\\.]+)(?:\\.git)?$", url)
    return (m.group("org"), m.group("repo")) if m else ("QMCSoftware", "QMCSoftware")

def _resolve_branch(org: str, repo: str) -> str:
    if os.environ.get("BOOT_BRANCH"):
        return os.environ["BOOT_BRANCH"]
    return "main" if repo == "MATH565Fall2025" else DEFAULT_BOOT_BRANCH

# =============================================================================
# NB_PATH helpers
# =============================================================================
def get_nb_override() -> Optional[str]:
    if in_ipython():
        val = get_ipython().user_ns.get("NB_PATH")  # type: ignore
        if isinstance(val, str) and val.strip():
            return val
    return os.environ.get("NB_PATH")

def guess_nb_path(repo_root: pathlib.Path) -> str:
    try:
        import ipynbname
        return str(pathlib.Path(ipynbname.path()).resolve().relative_to(repo_root))
    except Exception:
        return "unknown.ipynb"

# =============================================================================
# Local path setup
# =============================================================================
def _ensure_local_paths(repo_root: pathlib.Path):
    for path in (repo_root, repo_root / "utils"):
        p = str(path)
        if p not in sys.path:
            sys.path.insert(0, p)

# =============================================================================
# Colab bootstrap
# =============================================================================
def ensure_pip_packages(pkgs: List[str], quiet: bool = True):
    import importlib
    to_install = []
    for pkg in pkgs:
        mod = pkg.split("==")[0].split(">=")[0]
        try:
            importlib.import_module(mod if mod != "matplotlib" else "matplotlib")
        except ImportError:
            to_install.append(pkg)
    if to_install:
        if not quiet:
            print("[notebook_header] pip install:", " ".join(to_install))
        subprocess.check_call([sys.executable, "-m", "pip", "install", *to_install])

def _is_editable_installable(path: pathlib.Path) -> bool:
    return any((path / f).exists() for f in ("pyproject.toml", "setup.cfg", "setup.py"))

def _find_qmc_submodule(repo_dir: pathlib.Path) -> Optional[pathlib.Path]:
    for name in ("QMCSoftware", "qmcsoftware"):
        p = repo_dir / name
        if p.exists():
            return p
    for p in repo_dir.iterdir():
        if p.is_dir() and (p / "qmcpy").exists():
            return p
    return None

def _add_qmc_to_syspath(qmc_path: pathlib.Path):
    add_path = qmc_path / "src" if (qmc_path / "src" / "qmcpy").exists() else qmc_path
    if str(add_path) not in sys.path:
        sys.path.insert(0, str(add_path))

def colab_bootstrap(org: str, repo: str, branch: str, quiet: bool = True) -> pathlib.Path:
    repo_dir = pathlib.Path("/content") / repo
    if not repo_dir.exists():
        if not quiet:
            print(f"[notebook_header] Cloning {org}/{repo}@{branch} ...")
        subprocess.check_call([
            "git", "clone", "--depth", "1", "--recurse-submodules",
            "-b", branch, f"https://github.com/{org}/{repo}.git", str(repo_dir)
        ])
    subprocess.check_call(["git", "-C", str(repo_dir), "submodule", "sync", "--recursive"])
    subprocess.check_call(["git", "-C", str(repo_dir), "submodule", "update", "--init", "--recursive", "--depth", "1"])

    req = repo_dir / "requirements-colab.txt"
    if req.exists():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req)])
    else:
        ensure_pip_packages(["numpy", "scipy", "matplotlib", "pandas", "ipynbname"], quiet=quiet)

    qmc_path = _find_qmc_submodule(repo_dir)
    if qmc_path:
        if _is_editable_installable(qmc_path):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(qmc_path)])
            except Exception as e:
                print("[notebook_header] WARNING: Editable install failed; falling back:", e)
                _add_qmc_to_syspath(qmc_path)
        else:
            _add_qmc_to_syspath(qmc_path)

    if str(repo_dir) not in sys.path:
        sys.path.insert(0, str(repo_dir))
    utils_dir = str(repo_dir / "utils")
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    try:
        os.chdir(repo_dir)
    except Exception:
        pass

    return repo_dir

# =============================================================================
# Colab badge
# =============================================================================
def show_colab_button(org: str, repo: str, branch: str, nb_path: str):
    from IPython.display import HTML, display
    nb_quoted = nb_path.replace(" ", "%20")
    url = f"https://colab.research.google.com/github/{org}/{repo}/blob/{branch}/{nb_quoted}"
    html = (
        'If not running in <code>conda qmcpy</code>, open in '
        f'<a target="_blank" href="{url}">'
        '<img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>.'
    )
    display(HTML(html))

# =============================================================================
# Auto imports
# =============================================================================
def try_auto_imports():
    """Load utils/auto_imports.inject_common silently unless AUTO_IMPORTS_VERBOSE=1."""
    try:
        verbose = os.environ.get("AUTO_IMPORTS_VERBOSE", "0").lower() in ("1","true","yes")
        try:
            from utils.auto_imports import inject_common  # preferred
            if verbose: print("[notebook_header] auto_imports: using utils.auto_imports")
        except ImportError:
            import auto_imports  # fallback
            inject_common = auto_imports.inject_common
            if verbose: print("[notebook_header] auto_imports: using local auto_imports")

        ns = get_ipython().user_ns  # type: ignore[attr-defined]
        plot_prefs = os.environ.get("AUTO_PLOT_PREFS", "0").lower() in ("1","true","yes")
        inject_common(ns, verbose=verbose, plot_prefs=plot_prefs)
        if verbose: print("[notebook_header] auto_imports loaded successfully.")
    except Exception as e:
        print("[notebook_header] auto_imports failed:", e)

def _ensure_qp_alias():
    try:
        ns = get_ipython().user_ns  # type: ignore
        if "qp" not in ns:
            import qmcpy as _qp
            ns["qp"] = _qp
    except Exception:
        pass

# =============================================================================
# Main entry
# =============================================================================
def main(force: bool = False, quiet: bool = True):
    global _NB_PATH
    repo_root = get_repo_root()
    org, repo = get_org_repo()
    branch = _resolve_branch(org, repo)

    if repo_root and not in_colab():
        _ensure_local_paths(repo_root)

    if _STATE["ran"] and not force:
        try:
            show_colab_button(org, repo, branch, _NB_PATH)
        except Exception:
            pass
        return
    _STATE["ran"] = True

    _NB_PATH = get_nb_override() or (guess_nb_path(repo_root) if repo_root else "unknown.ipynb")

    try:
        show_colab_button(org, repo, branch, _NB_PATH)
    except Exception:
        pass

    if in_colab():
        try:
            colab_bootstrap(org, repo, branch, quiet=quiet)
        except Exception as e:
            print("[notebook_header] ERROR: Colab bootstrap failed:", e)

    try_auto_imports()
    _ensure_qp_alias()

def reload_header(quiet: bool = True):
    return main(force=True, quiet=quiet)

# Autorun
if os.environ.get("NOTEBOOK_HEADER_AUTORUN", "1").lower() in ("1","true","yes"):
    if in_ipython():
        try:
            main(False)
        except Exception as e:
            print("[notebook_header] ERROR: autorun failed:", e)