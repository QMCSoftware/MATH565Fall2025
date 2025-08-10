"""
notebook_header.py — portable header for VS Code, JupyterLab, and Colab.

- Minimal output by default (quiet=True). Re-running re-renders the badge.
- Always shows an inline "Open in Colab" badge (one line, no break).
- Honors NB_PATH (from notebook user_ns or environment).
- Org/repo detection prefers BOOT_ORG/BOOT_REPO, then git remote.
- Branch resolution prefers BOOT_BRANCH; defaults to 'main' for MATH565Fall2025,
  otherwise to DEFAULT_BOOT_BRANCH (e.g., 'bootstrap_colab').
- Local runs: header ensures both <repo_root> and <repo_root>/utils are on sys.path.
- Colab bootstrap:
    • Clone/update repo and submodules.
    • Find QMCSoftware submodule under either 'QMCSoftware' or 'qmcsoftware'.
    • pip -e the submodule if installable; else add correct path (flat or src) to sys.path.
    • Never editable-install the top-level repo; just add to sys.path.
- Optional auto-import hook (utils/auto_imports.py) if present.
"""

from __future__ import annotations
import os
import sys
import re
import subprocess
import pathlib
from typing import Optional, List

_STATE = {"ran": False}
_NB_PATH = "unknown.ipynb"  # updated at runtime

DEFAULT_BOOT_BRANCH = (
    os.environ.get("BOOT_BRANCH")
    or os.environ.get("QMCSOFTWARE_REF")
    or "bootstrap_colab"
)

# ---------------------------
# Environment helpers
# ---------------------------
def in_ipython() -> bool:
    try:
        get_ipython  # type: ignore[name-defined]
        return True
    except NameError:
        return False

def in_colab() -> bool:
    return "COLAB_RELEASE_TAG" in os.environ or "COLAB_GPU" in os.environ

def conda_env_name() -> Optional[str]:
    name = os.environ.get("CONDA_DEFAULT_ENV")
    if name:
        return name
    prefix = sys.prefix
    m = re.search(r"(?:^|[/\\\\])envs[/\\\\]([^/\\\\]+)$", prefix)
    return m.group(1) if m else None

def in_qmcpy_env() -> bool:
    env = (conda_env_name() or "").lower()
    if env == "qmcpy":
        return True
    flag = os.environ.get("QMCPY_ENV", "").lower()
    if flag in ("1", "true", "yes", "y"):
        return True
    return False

# ---------------------------
# Git / repo helpers
# ---------------------------
def get_repo_root() -> Optional[pathlib.Path]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        p = pathlib.Path(out)
        return p if p.exists() else None
    except Exception:
        return None

def get_org_repo() -> tuple[str, str]:
    """Prefer explicit overrides (ORG/REPO, BOOT_ORG/BOOT_REPO), else derive from git remote."""
    org = (globals().get("ORG") or os.environ.get("ORG")
           or os.environ.get("BOOT_ORG"))
    repo = (globals().get("REPO") or os.environ.get("REPO")
            or os.environ.get("BOOT_REPO"))
    if org and repo:
        return str(org), str(repo)
    try:
        url = subprocess.check_output(
            ["git", "config", " --get", "remote.origin.url"], text=True
        ).strip()
    except Exception:
        try:
            url = subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"], text=True
            ).strip()
        except Exception:
            url = ""
    m = re.search(r"[:/](?P<org>[^/]+)/(?P<repo>[^/\\.]+)(?:\\.git)?$", url)
    if m:
        return m.group("org"), m.group("repo")
    return "QMCSoftware", "QMCSoftware"

def _resolve_branch(org: str, repo: str) -> str:
    """Pick a reasonable default branch; prefer explicit override."""
    env_branch = os.environ.get("BOOT_BRANCH")
    if env_branch:
        return env_branch
    if repo == "MATH565Fall2025":
        return "main"
    return DEFAULT_BOOT_BRANCH

def _ensure_qp_alias():
    """Guarantee qp is available if qmcpy is importable."""
    try:
        ns = get_ipython().user_ns  # type: ignore[attr-defined]
        if 'qp' not in ns:
            import qmcpy as _qp
            ns['qp'] = _qp
    except Exception:
        pass

# ---------------------------
# NB_PATH override + detection
# ---------------------------
def get_nb_override() -> Optional[str]:
    """Read NB_PATH override from the notebook's user_ns or environment."""
    try:
        if in_ipython():
            ns = get_ipython().user_ns  # type: ignore[attr-defined]
            val = ns.get("NB_PATH")
            if isinstance(val, str) and val.strip():
                return val
    except Exception:
        pass
    val = os.environ.get("NB_PATH")
    return val if val else None

def guess_nb_path(repo_root: pathlib.Path) -> str:
    """Guess path to the current notebook, relative to repo root."""
    try:
        import ipynbname  # type: ignore
        full = pathlib.Path(ipynbname.path())
        return str(full.resolve().relative_to(repo_root))
    except Exception:
        return "unknown.ipynb"

# ---------------------------
# Local path setup
# ---------------------------
def _ensure_local_paths(repo_root: pathlib.Path):
    """Ensure both repo_root and repo_root/utils are importable locally."""
    root = str(repo_root)
    util = str(repo_root / "utils")
    if root not in sys.path:
        sys.path.insert(0, root)
    if util not in sys.path:
        sys.path.insert(0, util)

# ---------------------------
# Colab bootstrap
# ---------------------------
def ensure_pip_packages(pkgs: List[str], *, quiet: bool = True) -> None:
    import importlib
    to_install = []
    for p in pkgs:
        mod = p.split("==")[0].split(">=")[0]
        try:
            importlib.import_module(mod if mod != "matplotlib" else "matplotlib")
        except Exception:
            to_install.append(p)
    if to_install:
        if not quiet:
            print("[notebook_header] pip install:", " ".join(to_install))
        subprocess.check_call([sys.executable, "-m", "pip", "install", *to_install])

def _is_editable_installable(path: pathlib.Path) -> bool:
    return any((path / fname).exists() for fname in ("pyproject.toml", "setup.cfg", "setup.py"))

def _find_qmc_submodule(repo_dir: pathlib.Path) -> Optional[pathlib.Path]:
    # Common names used across repos
    for name in ("QMCSoftware", "qmcsoftware"):
        p = repo_dir / name
        if p.exists():
            return p
    # Fallback: shallow scan for a dir containing 'qmcpy'
    try:
        for p in repo_dir.iterdir():
            if p.is_dir() and (p / "qmcpy").exists():
                return p
    except Exception:
        pass
    return None

def _add_qmc_to_syspath(qmc_path: pathlib.Path) -> None:
    """Add correct folder (flat or src layout) to sys.path."""
    add = qmc_path / "src" if (qmc_path / "src" / "qmcpy").exists() else qmc_path
    if str(add) not in sys.path:
        sys.path.insert(0, str(add))

def colab_bootstrap(org: str, repo: str, branch: str, *, quiet: bool = True) -> pathlib.Path:
    """Clone/update repo & submodules, ensure deps & imports work in Colab."""
    repo_dir = pathlib.Path("/content") / repo
    if not repo_dir.exists():
        if not quiet:
            print(f"[notebook_header] Cloning {org}/{repo}@{branch} (with submodules) ...")
        subprocess.check_call([
            "git", "clone", "--depth", "1", "--recurse-submodules",
            "-b", branch, f"https://github.com/{org}/{repo}.git", str(repo_dir)
        ])

    # Ensure submodules are present/up-to-date (even for reused shallow clones)
    subprocess.check_call(["git", "-C", str(repo_dir), "submodule", "sync", "--recursive"])
    subprocess.check_call(["git", "-C", str(repo_dir), "submodule", "update", "--init", "--recursive", "--depth", "1"])

    # requirements
    req = repo_dir / "requirements-colab.txt"
    if req.exists():
        if not quiet:
            print("[notebook_header] Installing requirements-colab.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req)])
    else:
        ensure_pip_packages(["numpy", "scipy", "matplotlib", "pandas", "ipynbname"], quiet=quiet)

    # QMCSoftware submodule: editable if possible; else add to sys.path
    qmc_path = _find_qmc_submodule(repo_dir)
    if qmc_path:
        if _is_editable_installable(qmc_path):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(qmc_path)])
            except Exception as e:
                print("[notebook_header] WARNING: Editable install of QMCSoftware failed; falling back to sys.path:", e)
                _add_qmc_to_syspath(qmc_path)
        else:
            _add_qmc_to_syspath(qmc_path)
    else:
        print("[notebook_header] WARNING: QMCSoftware submodule not found (tried 'QMCSoftware' and 'qmcsoftware').")

    # Top-level repo: never editable-install; just add to sys.path
    if str(repo_dir) not in sys.path:
        sys.path.insert(0, str(repo_dir))

    # Ensure utils on path + chdir for relative paths
    utils_dir = repo_dir / "utils"
    if str(utils_dir) not in sys.path:
        sys.path.insert(0, str(utils_dir))
    try:
        os.chdir(repo_dir)
    except Exception:
        pass

    return repo_dir

# ---------------------------
# Colab badge helper
# ---------------------------
def show_colab_button(org: str, repo: str, branch: str, nb_path: str) -> None:
    """Display an inline message + Open in Colab badge (one line, no break)."""
    from IPython.display import HTML, display
    nb_quoted = nb_path.replace(" ", "%20")
    url = f"https://colab.research.google.com/github/{org}/{repo}/blob/{branch}/{nb_quoted}"
    html = (
        'If you are not running this notebook in the '
        '<code>conda qmcpy</code> environment, then '
        f'<a target="_blank" href="{url}">'
        '<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        'alt="Open In Colab"/></a>'
        ' and rerun the cell above.  Otherwise proceed to the next cell.'
    )
    display(HTML(html))

# ---------------------------
# Auto imports (optional)
# ---------------------------
def try_auto_imports():
    """Inject common aliases (np, pd, plt, sp, sy, qp) into the interactive namespace."""
    try:
        from utils import auto_imports  # type: ignore
        ns = get_ipython().user_ns  # type: ignore[attr-defined]
        auto_imports.inject_common(ns)
    except Exception as e:
        print("[notebook_header] auto_imports failed:", e)

# ---------------------------
# Post-run hook (rarely needed)
# ---------------------------
def _post_run_attempt_path(repo_root: pathlib.Path, org: str, repo: str, branch: str, quiet: bool):
    ip = get_ipython()  # type: ignore[attr-defined]
    def _callback(*args, **kwargs):
        global _NB_PATH
        try:
            override = get_nb_override()
            new_path = override if override else guess_nb_path(repo_root)
            if new_path != "unknown.ipynb":
                _NB_PATH = new_path
                try:
                    show_colab_button(org, repo, branch, _NB_PATH)
                except Exception:
                    pass
                try:
                    ip.events.unregister('post_run_cell', _callback)  # type: ignore[attr-defined]
                except Exception:
                    pass
        except Exception:
            try:
                ip.events.unregister('post_run_cell', _callback)  # type: ignore[attr-defined]
            except Exception:
                pass
    try:
        ip.events.register('post_run_cell', _callback)  # type: ignore[attr-defined]
    except Exception:
        pass

# ---------------------------
# Main entry
# ---------------------------
def main(force: bool = False, quiet: bool = True):
    """Run header once; on subsequent calls, just re-render the badge."""
    global _NB_PATH

    repo_root = get_repo_root()
    org, repo = get_org_repo()
    branch = _resolve_branch(org, repo)

    # NEW: on local runs, ensure repo_root and utils are importable
    if repo_root and not in_colab():
        _ensure_local_paths(repo_root)

    if _STATE["ran"] and not force:
        try:
            show_colab_button(org, repo, branch, _NB_PATH)
        except Exception as e:
            if not quiet:
                print("[notebook_header] Colab badge error:", e)
        return

    _STATE["ran"] = True

    # Determine notebook path
    nb_override = get_nb_override()
    if nb_override:
        _NB_PATH = nb_override
    elif repo_root:
        _NB_PATH = guess_nb_path(repo_root)
    else:
        _NB_PATH = "unknown.ipynb"

    # Always show the badge (inline)
    try:
        show_colab_button(org, repo, branch, _NB_PATH)
    except Exception as e:
        if not quiet:
            print("[notebook_header] Colab badge error:", e)

    # If in Colab, ensure the repo & deps are ready
    if in_colab():
        try:
            colab_bootstrap(org, repo, branch, quiet=quiet)
        except Exception as e:
            print("[notebook_header] ERROR: Colab bootstrap failed:", e)

    # If we couldn't resolve NB path on first import, try right after first cell
    if _NB_PATH == "unknown.ipynb" and in_ipython() and repo_root:
        _post_run_attempt_path(repo_root, org, repo, branch, quiet)

    # Optional auto-imports
    try_auto_imports()
    _ensure_qp_alias()   # <- make qp always available when qmcpy is present

def reload_header(quiet: bool = True):
    return main(force=True, quiet=quiet)

# ---------------------------
# Autorun (default on; you can disable via NOTEBOOK_HEADER_AUTORUN=0)
# ---------------------------
if os.environ.get("NOTEBOOK_HEADER_AUTORUN", "1").lower() in ("1", "true", "yes"):
    if in_ipython():
        try:
            main(False)
        except Exception as e:
            print("[notebook_header] ERROR: autorun failed:", e)