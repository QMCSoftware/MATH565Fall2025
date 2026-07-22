# MATH 565 Fall 2025

This is the repository for the **MATH 565 Monte Carlo Methods** class at Illinois Tech in Fall 2025.  
It contains lecture notes, Jupyter notebooks, and links to other resources.

The class website at [qmcsoftware.github.io/MATH565Fall2025](https://qmcsoftware.github.io/MATH565Fall2025/)
contains the syllabus, assignments, and links to course materials.

Found a broken link, typo, unclear instruction, missing file, or notebook error? See
[how to report a problem](https://qmcsoftware.github.io/MATH565Fall2025/report-a-problem/).
Please do not put grades, student IDs, or other private information in a public GitHub issue.

---

## 📚 New: Shared Class Library (`HickernellClassLib`)

This repository now includes a **Git submodule** called
[`HickernellClassLib`](https://github.com/QMCSoftware/HickernellClassLib),
which contains reusable Python code used across several courses.

To make sure your local copy includes the submodule, run:

```bash
git submodule update --init --recursive
```

If you cloned before this change, please run the above command once.
Future `git pull` operations will keep the submodule updated automatically.

---

## 🧭 Two Ways to Make Your Own Copy: Fork vs Use Template

You should make your own copy of this repository so that you can run the notebooks yourself and have a place for your own work.

### 🔁 Option 1: **Fork this repository** (Recommended)

Choose this if you want to:
- **Stay up to date** with course materials (notes, demo notebooks, syllabus, etc.)
- Easily pull future updates from the instructor’s repository

**Steps:**
1. Click the **"Fork"** button (top right of this page).
2. Clone your fork to your computer using GitHub Desktop, VS Code, or the command line:
   ```bash
   git clone --recurse-submodules https://github.com/YOUR-USERNAME/MATH565Fall2025.git
   ```
3. Add the instructor’s repo as a remote named `upstream` to pull updates later:
   ```bash
   git remote add upstream https://github.com/QMCSoftware/MATH565Fall2025.git
   ```

> ✅ This is the recommended option if you want to regularly sync with instructor updates.

---

### 📦 Option 2: **Use this template**

Choose this if you:
- Just want a **clean, independent copy** of the materials
- Don't plan to sync with instructor updates regularly
- Prefer not to deal with GitHub's fork mechanics

**Steps:**
1. Click the **"Use this template"** button (above the file list).
2. Create a new repo under your GitHub account.
3. Clone your new repo (including submodules) and begin working:
   ```bash
   git clone --recurse-submodules https://github.com/YOUR-USERNAME/MATH565Fall2025.git
   ```

> ⚠️ This option does **not automatically receive updates** from the instructor’s repo.

---

### 🔄 Want to update your template-based repo later?

If you chose the template route and want to get updates later, you can:

1. Add the instructor’s repo as a remote:
   ```bash
   git remote add upstream https://github.com/QMCSoftware/MATH565Fall2025.git
   ```

2. Pull in changes when needed:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

3. Update the submodule if needed:
   ```bash
   git submodule update --init --recursive
   ```

> 💡 This works the same as with a fork — you just have to set up the `upstream` link manually.

---

### ✅ Verify the submodule import (optional)

If you’re using the `qmcpy` environment, you can check that the class library works:

```bash
conda activate qmcpy
python - << 'PYCODE'
import os, sys
sys.path.append(os.path.join(os.getcwd(), "classlib"))
from classlib.distributions import UniformSumDistribution
print("✅ classlib imported successfully")
PYCODE
```

If you see the confirmation message, your setup is correct.
