from . import distributions as _distributions
from . import generators as _generators
from . import discrepancy as _discrepancy

from .distributions import *  # re-export what distributions.__all__ says
from .generators    import *  # re-export what generators.__all__ says
from .discrepancy   import *  # re-export what discrepancy.__all__ says

__all__ = []
__all__ += getattr(_distributions, "__all__", [])
__all__ += getattr(_generators, "__all__", [])
__all__ += getattr(_discrepancy, "__all__", [])