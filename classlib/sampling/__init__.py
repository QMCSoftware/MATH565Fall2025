"""
Sampling algorithms: Metropolis, Parallel Tempering, Acceptance–Rejection.

Usage
-----
from classlib.sampling import metropolis, parallel_tempering, accept_reject
"""

from .metropolis import metropolis
from .parallel_tempering import parallel_tempering
from .accept_reject import accept_reject

__all__ = ["metropolis", "parallel_tempering", "accept_reject"]