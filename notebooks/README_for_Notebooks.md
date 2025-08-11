# MATH565Fall2025 — Running Notebooks in Portable VS Code, JupyterLab, or Colab Environments

This repository contains course materials for **MATH 565 — Fall 2025**, including Python notebooks, utilities, and the `notebook_header.py` bootstrap system for seamless use in **VS Code**, **JupyterLab**, and **Google Colab**.

The goal is to ensure that students can run the notebooks without worrying about Python environments, LaTeX toolchains, or the [QMCSoftware](https://github.com/QMCSoftware/QMCSoftware) dependency.

---

## Features

### 1. `notebook_header.py`
The portable header ensures a consistent setup across local and Colab environments.

- **Local (VS Code, JupyterLab)**  
  - Ensures `<repo_root>` and `<repo_root>/utils` are on `sys.path`.
  - Relies on your existing Python environment for dependencies.
  - LaTeX toolchain is assumed to be installed locally if `usetex=True` is used.

- **Google Colab**  
  - Clones the course repo and submodules from GitHub.  
  - Installs minimal Python dependencies (`numpy`, `scipy`, `matplotlib`, `pandas`, `ipynbname`).  
  - Ensures a working LaTeX toolchain (`latex`, `dvipng`/`dvisvgm`, `ghostscript`).  
  - Makes `qmcpy` importable from the `qmcsoftware` submodule if present, otherwise installs it from GitHub.
  - Registers a Colab-only execution timer after each cell.

- **All environments**  
  - Displays an "Open in Colab" badge in the first cell.  
  - Auto-imports common libraries with standard aliases:
    ```python
    np → numpy
    pd → pandas
    plt → matplotlib.pyplot
    sp → scipy
    sy → sympy (with pretty printing)
    qp → qmcpy (optional)
    ```
  - Optionally applies Matplotlib rcParams for consistent plot styling (including LaTeX text rendering).

---

### 2. `auto_imports.py`
This utility injects common aliases and optional plotting preferences into the notebook namespace.

- Controlled by environment variables:
  - `AUTO_IMPORTS_VERBOSE=1` → show diagnostics.
  - `AUTO_PLOT_PREFS=1` → apply plotting styles and LaTeX preamble.

- Loads LaTeX macros for Matplotlib from `utils/latex_macros.py`.

- Includes a post-check to confirm that essential imports (`np`, `pd`, `plt`) are available.

---

### 3. LaTeX Macros
- LaTeX macros for **Matplotlib** are defined in:
  ```
  utils/latex_macros.py
  ```
- Markdown LaTeX macros are **not automatically injected**.  
  If desired, you can manually add a first-cell Markdown block with your preferred macro definitions.

---

## Installation & Usage

### Local (VS Code or JupyterLab)
1. Clone the repo:
   ```bash
   git clone --recurse-submodules https://github.com/fredhickernell/MATH565Fall2025.git
   cd MATH565Fall2025
   ```
2. Install Python dependencies (in your conda or virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure LaTeX is installed if you want `usetex=True` in Matplotlib.

4. Open notebooks in **VS Code** (with the Jupyter extension) or **JupyterLab**.

---

### Google Colab
1. Open the repo on GitHub and click the "Open in Colab" badge in the first cell of any notebook.
2. The header will:
   - Clone the repo in `/content`
   - Install dependencies and LaTeX
   - Import `qmcpy` from submodule or GitHub
3. Run from the top.

---

## Environment Variables

These can be set in the **first cell** of your notebook *before* importing `notebook_header`:

| Variable                  | Purpose                                                        |
|---------------------------|----------------------------------------------------------------|
| `BOOT_ORG`                | GitHub org name override                                       |
| `BOOT_REPO`               | GitHub repo name override                                      |
| `BOOT_BRANCH`             | Branch to clone in Colab (default: `main` for class repo)      |
| `NB_PATH`                 | Notebook path override                                         |
| `NOTEBOOK_HEADER_AUTORUN` | Run header automatically (default: `1`)                        |
| `AUTO_PLOT_PREFS`         | Apply plotting preferences (`1` = yes, default: no)            |
| `AUTO_IMPORTS_VERBOSE`    | Verbose output from `auto_imports` (`1` = yes, default: no)    |
| `QMCPY_BRANCH`            | Branch of QMCSoftware to install from GitHub if needed         |

---

## Example First Cell

```python
%pip install ipynbname  # Only if missing locally

import os
os.environ["AUTO_PLOT_PREFS"] = "1"  # Optional: apply plot prefs
os.environ["AUTO_IMPORTS_VERBOSE"] = "1"  # Optional: see what auto_imports is doing
os.environ["QMCPY_BRANCH"] = "develop"    # Optional: install a specific branch in Colab

from utils import notebook_header
notebook_header.main()
```

---

## Development Notes

- The **badge message** in `show_colab_button()` can be customized — currently it says:
  > "If not running in `conda qmcpy`, push the button..."
- In Colab, LaTeX installation may take several minutes the first time.
- Submodules must be kept up-to-date:
  ```bash
  git submodule update --init --recursive
  ```

---

## License
MIT License — see [LICENSE](LICENSE) for details.
