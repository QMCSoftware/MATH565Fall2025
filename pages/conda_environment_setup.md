---
layout: page
title: Conda Environment Setup
permalink: /conda-setup/
---

These steps set up Python and the `qmcpy` environment so you can run the course notebooks.

---

### 1. Clone this repository (with submodules)

```bash
git clone --recurse-submodules https://github.com/QMCSoftware/MATH565Fall2025.git
cd MATH565Fall2025
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

---

### 2. Create and activate a Conda environment

```bash
conda create -n qmcpy python=3.12 -y
conda activate qmcpy
```

*(You can use `mamba` instead of `conda` if you prefer.)*

---

### 3. Install QMCSoftware (editable)

```bash
pip install -e submodules/QMCSoftware[dev]
```

This installs `qmcpy` plus its development extras (JupyterLab, matplotlib, pandas, etc.).

---

### 4. Install course-specific extras

We keep our extras in a single file, `requirements-course.txt`.

```bash
pip install -r requirements-course.txt
```

---

### 5. Register the Jupyter kernel

```bash
python -m ipykernel install --user --name qmcpy --display-name "Python (qmcpy)"
```

Now, when you open Jupyter, choose **Python (qmcpy)** as the kernel for the notebooks.

---

### 6. Updating later

When the repo or QMCSoftware changes:

```bash
git pull
git submodule update --init --recursive

conda activate qmcpy
pip install -e submodules/QMCSoftware[dev] --upgrade
pip install -r requirements-course.txt --upgrade
```

---

### Troubleshooting

- **Apple Silicon (M1/M2/M3):** Prefer [miniforge](https://github.com/conda-forge/miniforge) and `mamba`.  
- **Windows users:** If `pip` tries to compile something and fails, you may need [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).  
- **Starting fresh:** If your environment breaks:  

  ```bash
  conda env remove -n qmcpy
  conda create -n qmcpy python=3.12 -y
  conda activate qmcpy
  pip install -e submodules/QMCSoftware[dev]
  pip install -r requirements-course.txt
  ```

---

🎉 You’re ready to run the notebooks!

[⬅️ Back to Notebooks]({{ site.baseurl }}/notebooks/)
