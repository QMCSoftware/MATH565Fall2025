# MATH565 → QMCPy: Kernels & Discrepancy Convergence Plan

**Owner:** Fred J. Hickernell  
**Repos:**  
- Class repo (staging): `QMCSoftware/MATH565Fall2025`  
- Library repo (integration target): `QMCSoftware/QMCSoftware` (branch: `develop`)

## 1) Goals
- Keep course code useful for teaching **and** production-ready enough to upstream into QMCPy.
- Unify kernel & discrepancy abstractions so the same APIs serve: (a) discrepancy metrics, (b) two-sample tests, (c) Gaussian-process (GP) regression / Bayesian cubature.
- Provide a clean growth path for new **kernels** and **target distributions (measures)**.
- Support comparisons **point set vs measure** and **point set vs point set**.
- Allow efficient **O(n)** discrepancy evaluation when kernel/point-set structure matches.
- Ensure all kernel–measure integrals are **exact/analytical**, not estimated by Monte Carlo.

## 2) Design Principles
- **Terminology**: public API should use `discrepancy` (historical name) instead of `mmd`; documentation may reference MMD for clarity.
- **Single source of truth for APIs**: define abstract base classes (ABCs) once; keep MATH565 in lockstep with QMCPy’s `develop` branch.
- **Stateless kernels** (parameters immutable/frozen dataclasses) + **lightweight vectorized calls** (NumPy baseline; optional JAX/PyTorch later).
- **Separation of concerns**: `kernel` (similarity) vs `measure` (target distribution) vs `design` (point sets) vs `discrepancy` (metrics/comparisons).
- **Special structure**: design kernels and point sets so Gram matrices have exploitable forms (circulant, FFT-ready, etc.), reducing cost from O(n²) to O(n).
- **Hyperparameters**: all kernels expose optional tunable parameters (lengthscale, smoothness, etc.) with clear defaults.
- **Documentation-first**: doctests + minimal examples that mirror class notebooks; autodoc to site.

## 3) Unifying Abstractions

### 3.1 Kernel API
```python
@dataclass(frozen=True)
class Kernel:
    name: str
    var: float = 1.0
    lengthscale: float | Sequence[float] = 1.0
    periodic: bool = False
    def gram(self, X: np.ndarray, Y: np.ndarray, diag: bool=False) -> np.ndarray: ...
    def k(self, x: np.ndarray, y: np.ndarray) -> float: ...
    @property
    def is_stationary(self) -> bool: ...
```
**Conventions**: `X` shape `(n,d)`, `Y` shape `(m,d)`.

**Suggested concrete kernels**
- `SquaredExponential(var, lengthscale)`
- `Matern(nu, lengthscale, var)`
- `ProductSobolev(gamma: Sequence[float], anchored: bool)`
- `Brownian`, `IntegratedBrownian`
- `PeriodicExponential(lengthscale, period)`
- `QuadraticBernoulli(d)` (periodic discrepancy kernel)

### 3.2 Measures (target distributions)
```python
class Measure(Protocol):
    name: str
    def sample(self, n: int, d: int, rng: np.random.Generator) -> np.ndarray: ...
    def mean_feature(self, kernel: Kernel, X: np.ndarray | None = None) -> np.ndarray:
        """Analytical E_{T~P}[k(T, •)] at X. Must not use MC."""
```
**Concrete measures**: `UniformUnitCube`, `Gaussian(mean, cov)`, `Beta`, `TriangularSymmetric([-1,1])`, `CustomAnalytical`, `Empirical(points)`.

### 3.3 Designs (point sets)
```python
@dataclass(frozen=True)
class Design:
    X: np.ndarray  # (n,d)
    name: str = ""
    measure: Measure | None = None
    special_structure: str | None = None  # e.g. "lattice", "digitalnet"
```

### 3.4 Discrepancy API
```python
class Discrepancy(Protocol):
    name: str
    def value(self) -> float: ...
    def squared(self) -> float: ...
```
**Implementations**:
- `DiscrepancyOneSample(...)`
- `DiscrepancyTwoSample(...)`
- `CenteredDiscrepancy(...)`
- `PrefixDiscrepancy(...)`

## 4) Module Layout (target)
(same as previous draft)

## 5) Naming & Conventions
- Public API: `discrepancy_*` not `mmd`.
- Kernels: dataclasses with optional hyperparameters; user can override.
- Measures: analytical expectation required; MC fallback **not allowed**.
- Designs: flag special structures so optimized O(n) discrepancy algorithms can be triggered.

## 6) Minimal Target Interfaces
```python
def discrepancy(X: np.ndarray, kernel: Kernel, measure: Measure, unbiased: bool=False) -> float: ...

def discrepancy_two_sample(X: np.ndarray, Y: np.ndarray, kernel: Kernel, unbiased: bool=False) -> float: ...

def discrepancy_prefix(X: np.ndarray, kernel: Kernel, measure: Measure) -> np.ndarray: ...

def centered_discrepancy(X: np.ndarray, kernel: Kernel | None=None, gamma: float | Sequence[float]=1.0) -> float: ...
```

## 7) Examples of O(n) Discrepancy
- **Rank-1 Lattice Rules + Quadratic Bernoulli Kernel**: Gram matrix has circulant structure. Discrepancy can be computed using FFT in O(n log n) or reduced to O(n) with further structure.
- **Digital Nets (Sobol, Niederreiter)**: when paired with product Sobolev kernels, matrix-vector products collapse to low-cost evaluations leveraging Walsh/Fourier representations.
- These optimizations require tagging the design with `special_structure="lattice"` or `"digitalnet"` and providing specialized implementations in `discrepancy/fast.py`.

## 8) Migration Plan
(same as before, plus implementation of optimized routines for structured designs)

## 9) Testing & Validation
- Analytical integrals cross-checked against literature.
- Efficiency benchmarks: O(n) or FFT-based methods compared to O(n²) baseline.
- Hyperparameter tuning examples in docs.

## 10) Documentation & Pedagogy
- Use “discrepancy” in APIs and lectures; note equivalence to MMD in background materials.
- Demonstrate periodic/stationary kernels and O(n) discrepancy evaluation with lattice examples.

## 11) Growth Backlog
- Expand stationary & periodic kernel families (Quadratic Bernoulli, higher-order Bernoulli).
- Add specialized discrepancy algorithms for digital nets.
- Broaden measures with exact integrals.

## 12) Tasks
- [ ] Scaffold base modules in MATH565 (kernel.base, measure.base, discrepancy.one_sample).  
- [ ] Port existing kernels/discrepancies with new naming (`discrepancy_*`).  
- [ ] Implement analytical integrals for all kernels–measures (no MC fallbacks).  
- [ ] Add optimized O(n) routines for lattice/digital net point sets.  
- [ ] Write minimal unit tests + doctests.  
- [ ] Draft PR to QMCPy `develop` with mirrored layout.  

