# MATH 565 — Planned Improvements for Fall 2026
**Version: 2025.11.28**

---

### MATH 565 Improvements — Changelog

This changelog documents the evolution of planned improvements for MATH 565, using date-based versioning (YYYY.MM.DD), similar to macOS.

---

#### Version 2025.11.28
- Added Hamiltonian and Langevin MCMC

#### Version 2025.11.26
- Initial categorized improvements document created.
- Added Monte Carlo Tree Search (MCTS) as a selected topic.
- Added planned improvements for:
  - MCMC tools (emcee, PyMC/NUTS)
  - SimPy queueing simulations
  - Notebook refactoring and modernization
  - QMCPy kernel class expansion
- Added workflow plans (full repo notebook testing, student install verification).
- Added documentation/publishing considerations (Quarto, Jupyter Book).

---

## Summary of Possible Future Improvements
Record updates here as improvements evolve.


This document summarizes the planned improvements for next year’s offering of **MATH 565 Monte Carlo Methods**, grouped into categories for clarity.

---

## 1. Curricular Additions

### 1.1 Monte Carlo Tree Search (MCTS)
- Add an accessible introduction to MCTS.
- Cover exploration vs. exploitation, UCT, and links to stochastic optimization.
- Could be a short module or an optional project.

### 1.2 Expanded MCMC Coverage
- Introduce **emcee** (ensemble samplers) for intuitive MCMC.
- Consider **PyMC (NUTS)** for automatic HMC demonstrations.
- Possibly replace or supplement Metropolis + parallel tempering.
- Langevin and Hamiltonian MCMC (added 11/28/25)

### 1.3 Queueing Simulations
- Revisit switching to **SimPy**, potentially with a small shim layer for consistency.

---

## 2. Notebook & Code Upgrades

### 2.1 Refactor Older MATH 565 Notebooks
- Align all older notebooks with the improved **HickernellClassLib** workflow.
- Clean up:
  - GPU/CPU timing examples
  - SGD/GD comparisons
  - Stopping-criteria notebook
  - Asian option code architecture

### 2.2 QMCPy Introduction Notebook Enhancements
- Expand the Asian option example with **importance sampling** and **control variates**.
- Improve nbviz styling and explanatory overlays.

### 2.3 Build Out the Kernels Class in QMCPy
- Create a more complete, usable QMCPy **kernel abstraction** suitable for:
  - covariance kernels
  - kernel herding
  - Bayesian cubature demos
- Integrate into upcoming MATH 565 examples.

---

## 3. Workflow Enhancements

### 3.1 Automated Notebook Testing
- Implement periodic full-repo notebook runs to detect breakages early.
- Integrate into pre-semester workflows.

### 3.2 Student Installation Workflow
- After Dec 15, test installation using a clean macOS Test User.
- Finalize and simplify conda + qmcpy setup instructions.

---

## 4. Documentation & Publishing

### 4.1 Course Material Organization
- Continue evaluating **Quarto** and **Jupyter Book** for modern course publishing.
- Move toward a unified visual style for figures, code, and exposition.

---