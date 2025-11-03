---
layout: page
title: Conda Environment Setup
permalink: /conda-setup/
---

These steps set up Python, `qmcpy`, and the **MATH 565 class library** so you can run all course notebooks.

---

### 1. Clone this repository (with submodules)

```bash
# Recommended: clone and fetch submodules in one go
git clone --recurse-submodules https://github.com/QMCSoftware/MATH565Fall2025.git
cd MATH565Fall2025
```

If you already cloned without `--recurse-submodules`, run:

```bash
git submodule update --init --recursive
```

> **Note:** Downloading the repo as a ZIP will **not** include submodules. Please use `git clone`.

---

### 2. Create and activate a Conda environment

```bash
conda create -n qmcpy python=3.12 -y
conda activate qmcpy
```

*(You can use `mamba` instead of `conda` if you prefer.)*

---

### 3. Install the class package (editable)

The course repo now includes a `pyproject.toml`, so you can install it as a package directly:

```bash
pip install -e .
```

This makes the class library (`classlib`) importable from anywhere, for example:

```python
from classlib.sampling import metropolis
```

---

### 4. Install QMCSoftware (editable submodule)

The `qmcsoftware` directory is a submodule that provides the main `qmcpy` package.  
Install it in editable mode as well:

```bash
pip install -e "qmcsoftware[dev]"
```

This installs `qmcpy` plus JupyterLab, matplotlib, pandas, and other development extras.

---

### 5. Install course-specific dependencies

Additional packages used in notebooks are listed in:

```bash
pip install -r requirements-course.txt
```

---

### 6. Register the Jupyter kernel

```bash
python -m ipykernel install --user --name qmcpy --display-name "Python (qmcpy)"
```

Then choose **Python (qmcpy)** as the kernel when you open a notebook.

---

### 7. Updating later

When the repo or QMCSoftware changes:

```bash
git pull
git submodule update --init --recursive   # keep submodules in sync

conda activate qmcpy
pip install -e . --upgrade
pip install -e "qmcsoftware[dev]" --upgrade
pip install -r requirements-course.txt --upgrade
```

*(Advanced: to track the latest QMCSoftware `develop` branch, run  
`cd qmcsoftware && git checkout develop && git pull`, but this is **not required** for the course.)*

---

### 8. Verify installation

```bash
python -c "import classlib, qmcpy; print('classlib + QMCSoftware OK:', qmcpy.__version__)"
```

Expected output (version numbers may vary):

```
classlib + QMCSoftware OK: 2.0
```

---

### Troubleshooting

- **Apple Silicon (M1/M2/M3):** Prefer [miniforge](https://github.com/conda-forge/miniforge) and `mamba`.
- **Windows users:** If `pip` fails while compiling, install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
- **Starting fresh:**  
  If your environment breaks:
  ```bash
  conda env remove -n qmcpy
  conda create -n qmcpy python=3.12 -y
  conda activate qmcpy
  git submodule update --init --recursive
  pip install -e .
  pip install -e "qmcsoftware[dev]"
  pip install -r requirements-course.txt
  ```

- **Check submodules:**  
  ```bash
  git submodule status
  test -f qmcsoftware/pyproject.toml && echo "qmcsoftware present"
  ```

---

🎉 You’re ready to run the notebooks!

[⬅️ Back to Notebooks]({{ site.baseurl }}/notebooks/)
