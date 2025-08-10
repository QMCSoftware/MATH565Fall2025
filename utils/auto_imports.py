# utils/auto_imports.py

def inject_common(ns):
    """Inject commonly used imports into the given namespace."""
    try:
        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import scipy as sp
        import sympy as sy
        import qmcpy as qp

        # Optional: init sympy printing for better display
        sy.init_printing(use_unicode=True)

        ns.update({
            'np': np,
            'pd': pd,
            'plt': plt,
            'sp': sp,  # scipy
            'sy': sy,  # sympy
            'qp': qp,  # qmcpy
        })
    except Exception as e:
        print("[auto_imports] Error importing common modules:", e)