# utils/auto_imports.py

def inject_common(ns, *, verbose=False):
    """
    Inject common aliases into the notebook namespace.
      np -> numpy
      pd -> pandas
      plt -> matplotlib.pyplot
      sp -> scipy
      sy -> sympy (pretty printing on)
      qp -> qmcpy  (optional; only if installed)
    Each import is independent; failures don't block others.
    """
    def _try(alias, mod, post=None):
        if alias in ns:
            return
        try:
            module = __import__(mod, fromlist=['*'])
            ns[alias] = module
            if post:
                try:
                    post(module)
                except Exception as e:
                    if verbose:
                        print(f"[auto_imports] post({alias}) error:", e)
        except Exception as e:
            if verbose:
                print(f"[auto_imports] skipped {alias} ({mod}): {e}")

    _try('np',  'numpy')
    _try('pd',  'pandas')
    _try('plt', 'matplotlib.pyplot')
    _try('sp',  'scipy')
    _try('sy',  'sympy', post=lambda sy: sy.init_printing(use_unicode=True))
    _try('qp',  'qmcpy')  # optional; fine if missing initially