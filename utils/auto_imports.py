# utils/auto_imports.py

def inject_common(ns, *, verbose=False, plot_prefs=None):
    """
    Inject aliases into the notebook namespace.
      np -> numpy, pd -> pandas, plt -> matplotlib.pyplot
      sp -> scipy,  sy -> sympy (pretty printing on), qp -> qmcpy (if installed)

    plot_prefs: bool | None
      True  -> apply matplotlib rcParams below
      False -> skip
      None  -> follow env var AUTO_PLOT_PREFS (1/true/yes)
    """
    def _try(alias, mod, post=None):
        if alias in ns:
            return
        try:
            module = __import__(mod, fromlist=['*'])
            ns[alias] = module
            if post:
                try: post(module)
                except Exception as e:
                    if verbose: print(f"[auto_imports] post({alias}) error:", e)
        except Exception as e:
            if verbose: print(f"[auto_imports] skipped {alias} ({mod}): {e}")

    _try('np',  'numpy')
    _try('pd',  'pandas')
    _try('plt', 'matplotlib.pyplot')
    _try('sp',  'scipy')
    _try('sy',  'sympy', post=lambda sy: sy.init_printing(use_unicode=True))
    _try('qp',  'qmcpy')  # optional; ok if missing

    # Optional plotting preferences
    if plot_prefs is None:
        plot_prefs = str(__import__('os').environ.get('AUTO_PLOT_PREFS', '0')).lower() in ('1','true','yes')

    if plot_prefs and 'plt' in ns:
        plt = ns['plt']
        rc = plt.rcParams
        # Figure / text
        rc['figure.figsize'] = (6.0, 4.0)
        rc['figure.dpi']     = 120
        rc['savefig.dpi']    = 120
        rc['font.size']      = 12
        rc['axes.titlesize'] = 'medium'
        rc['axes.labelsize'] = 'medium'
        rc['xtick.labelsize'] = 10
        rc['ytick.labelsize'] = 10
        rc['legend.fontsize'] = 10
        # Axes / grid
        rc['axes.grid']      = True
        rc['grid.alpha']     = 0.25
        rc['grid.linestyle'] = '--'
        rc['axes.spines.top'] = False
        rc['axes.spines.right'] = False
        # Lines / markers
        rc['lines.linewidth'] = 2.0
        rc['lines.markersize'] = 4.0
        # Math text uses Computer Modern-like
        rc['mathtext.fontset'] = 'cm'