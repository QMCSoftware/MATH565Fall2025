# Re-export the public API for simple imports in notebooks
from .core import mmd, AnalyticalMeasure
from .kernels import make_kernel, restrict_to_unit_cube, make_cd_kernel
from .measures import cd_uniform_k_mean, cd_uniform_k_self
from .usage import show_mmd_usage

__all__ = [
    "mmd", "AnalyticalMeasure",
    "make_kernel", "restrict_to_unit_cube", "make_cd_kernel",
    "cd_uniform_k_mean", "cd_uniform_k_self",
    "show_mmd_usage",
]