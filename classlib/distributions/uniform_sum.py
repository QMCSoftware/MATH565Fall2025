"""
uniform_sum.py

Exact distribution for the sum of independent Uniform[a_i, b_i] variables.

Implements a piecewise-polynomial pdf/cdf using the standard
inclusion–exclusion formula for sums of non-identical uniforms.

Complexity is O(2^n) in the number of summands n, so this is intended
for moderate n (say n ≤ 10–14). For large n, consider a CLT
approximation or a segment-wise convolution / FFT-based approach.

Example
-------
>>> from classlib.distributions.uniform_sum import UniformSumDistribution
>>> usd = UniformSumDistribution([(0.0, 1.0), (0.0, 0.5)])
>>> xs = np.array([0.25, 0.75, 1.25])
>>> usd.pdf(xs)
array([0.5, 1. , 0.5])
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple, Union, Optional

import numpy as np

ArrayLike = Union[float, Sequence[float], np.ndarray]


@dataclass
class UniformSumDistribution:
    """
    Sum of independent Uniform[a_i, b_i] with exact pdf/cdf.

    Parameters
    ----------
    intervals : sequence of (a_i, b_i)
        Each pair (a_i, b_i) defines one Uniform[a_i, b_i] variable with b_i > a_i.

    Attributes
    ----------
    a : np.ndarray
        Left endpoints (a_i).
    b : np.ndarray
        Right endpoints (b_i).
    W : np.ndarray
        Widths (b_i - a_i).
    n : int
        Number of summands.
    shift : float
        Sum of a_i; support starts at this value.
    support : (float, float)
        Tuple (low, high) where the pdf is nonzero.

    Methods
    -------
    pdf(x)
        Exact pdf evaluated at x (vectorized).
    cdf(x)
        Exact cdf evaluated at x (vectorized).
    rvs(size=None, rng=None)
        Draw samples of the sum.
    breakpoints()
        All polynomial breakpoints (kinks) of the pdf.
    mean()
        Mean of the sum.
    var()
        Variance of the sum.
    """

    intervals: Sequence[Tuple[float, float]]

    def __post_init__(self) -> None:
        ab = np.asarray(self.intervals, dtype=float)
        if ab.ndim != 2 or ab.shape[1] != 2:
            raise ValueError("intervals must be a sequence of (a, b) pairs, shape (n, 2).")

        a, b = ab[:, 0], ab[:, 1]
        if not np.all(b > a):
            raise ValueError("Each interval must satisfy b > a.")

        self.a = a
        self.b = b
        self.W = self.b - self.a
        self.n = len(self.W)

        # Support of the sum
        self.shift = float(np.sum(self.a))
        self.total_width = float(np.sum(self.W))
        self.support = (self.shift, self.shift + self.total_width)

        # Precompute all subset sums of widths and their signs for inclusion–exclusion
        # There are 2^n subsets, which is fine for moderate n.
        m = 1 << self.n  # 2^n
        subset_sums = np.empty(m, dtype=float)
        subset_sizes = np.zeros(m, dtype=int)

        subset_sums[0] = 0.0  # empty subset
        for i in range(self.n):
            bit = 1 << i
            w = float(self.W[i])
            for mask in range(bit):
                new_mask = mask | bit
                subset_sums[new_mask] = subset_sums[mask] + w
                subset_sizes[new_mask] = subset_sizes[mask] + 1

        # (-1)^{|A|} sign for each subset
        signs = np.where(subset_sizes % 2 == 0, 1, -1).astype(int)

        self._subset_sums = subset_sums  # shape (2^n,)
        self._signs = signs              # shape (2^n,)

        # Normalizing constants for pdf/cdf
        widths_prod = float(np.prod(self.W))
        self._pdf_norm = widths_prod * math.factorial(self.n - 1)
        self._cdf_norm = widths_prod * math.factorial(self.n)

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _positive_part_pow(x: np.ndarray, k: int) -> np.ndarray:
        """
        Compute (x_+)^k elementwise: max(x, 0)^k, k >= 0 integer.
        """
        return np.maximum(x, 0.0) ** k

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def pdf(self, x: ArrayLike) -> np.ndarray:
        """
        Exact pdf of the sum evaluated at x (vectorized).

        Parameters
        ----------
        x : array_like
            Points at which to evaluate the pdf.

        Returns
        -------
        np.ndarray
            pdf(x), with shape broadcast from x.
        """
        x = np.asarray(x, dtype=float)
        t = x - self.shift  # reduce to sum of U[0, W_i]

        # Shape broadcasting: (..., 1) - (2^n,) -> (..., 2^n)
        vals = self._positive_part_pow(
            t[..., None] - self._subset_sums[None, :],
            self.n - 1,
        )
        s = np.sum(self._signs[None, :] * vals, axis=-1)
        out = s / self._pdf_norm

        lo, hi = self.support
        # Clean up numerical noise outside support
        return np.where((x < lo) | (x > hi), 0.0, out)

    def cdf(self, x: ArrayLike) -> np.ndarray:
        """
        Exact cdf of the sum evaluated at x (vectorized).

        Parameters
        ----------
        x : array_like
            Points at which to evaluate the cdf.

        Returns
        -------
        np.ndarray
            cdf(x), with shape broadcast from x.
        """
        x = np.asarray(x, dtype=float)
        t = x - self.shift

        vals = self._positive_part_pow(
            t[..., None] - self._subset_sums[None, :],
            self.n,
        )
        s = np.sum(self._signs[None, :] * vals, axis=-1)
        out = s / self._cdf_norm

        lo, hi = self.support
        out = np.where(x <= lo, 0.0, out)
        out = np.where(x >= hi, 1.0, out)
        return out

    def rvs(
        self,
        size: Optional[int] = None,
        rng: Optional[Union[int, np.random.Generator]] = None,
    ) -> np.ndarray:
        """
        Random variates: sum of independent Uniform[a_i, b_i].

        Parameters
        ----------
        size : int or None, optional
            Number of samples to draw. If None, draws a single sample.
        rng : int or np.random.Generator, optional
            Seed or Generator for reproducibility.

        Returns
        -------
        np.ndarray
            If size is None, returns a scalar ndarray.
            Otherwise returns a 1D array of shape (size,).
        """
        if isinstance(rng, np.random.Generator):
            gen = rng
        else:
            gen = np.random.default_rng(rng)

        if size is None:
            u01 = gen.random(self.n)
            return float(np.sum(self.a + self.W * u01))

        u01 = gen.random((size, self.n))
        return np.sum(self.a + self.W * u01, axis=-1)

    def breakpoints(self) -> np.ndarray:
        """
        All polynomial breakpoints (kinks) of the pdf.

        Returns
        -------
        np.ndarray
            Sorted array of breakpoint locations.
        """
        return np.sort(self.shift + self._subset_sums)

    # Convenience stats -------------------------------------------------
    def mean(self) -> float:
        """
        Mean of the sum.
        """
        return float(np.sum(0.5 * (self.a + self.b)))

    def var(self) -> float:
        """
        Variance of the sum.
        """
        return float(np.sum(self.W**2 / 12.0))
    
    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_weights(cls, coord_wts):
        """
        Construct UniformSumDistribution for S = sum_i w_i * U[0,1].

        Parameters
        ----------
        coord_wts : sequence of positive floats
            The weights w_i. Each term corresponds to a U[0,1] random variable
            scaled by w_i.

        Returns
        -------
        UniformSumDistribution
        """
        w = np.asarray(coord_wts, dtype=float)
        if np.any(w <= 0):
            raise ValueError("All coord_wts must be positive.")
        intervals = [(0.0, float(wi)) for wi in w]
        return cls(intervals)
    