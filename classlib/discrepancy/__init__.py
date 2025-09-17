# Re-export the public API for simple imports in notebooks
from .core import mmd, AnalyticalMeasure
from .kernels import make_kernel, restrict_to_unit_cube
from .usage import show_mmd_usage

__all__ = ["mmd", "AnalyticalMeasure", "make_kernel",
           "restrict_to_unit_cube", "show_mmd_usage"]