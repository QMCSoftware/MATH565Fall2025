# MATH 565 Fall 2025
This is the repository for the MATH 565 Monte Carlo Methods class at Illinois Tech in the Fall of 2025.  There are lecture notes and links to Jupyter notebooks.

The class website at [qmcsoftware.github.io/MATH565Fall2025/](https://qmcsoftware.github.io/MATH565Fall2025/) contains the syllabus and links to lecture notes, assignments, and other resources.

## 🧭 Two Ways to Make Your Own Copy: Fork vs Use Template

You should make your own copy of this repository so that you can run the notebooks yourself and have a place for your own work.

### 🔁 Option 1: **Fork this repository** (Recommended)

Choose this if you want to:
- **Stay up to date** with course materials (notes, demo notebooks, syllabus, etc.)
- Easily pull future updates from the instructor’s repository

**Steps:**
1. Click the **"Fork"** button (top right of this page).
2. Clone your fork to your computer using GitHub Desktop, VS Code, or the command line.
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
3. Clone and begin working on your copy.

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

> 💡 This works the same as with a fork — you just have to set up the `upstream` link manually.