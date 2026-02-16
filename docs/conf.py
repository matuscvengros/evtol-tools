project = "evtol-tools"
copyright = "2026, Matus Cvengros"
version = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
]

# MyST settings
myst_enable_extensions = ["colon_fence", "deflist"]

# Autodoc
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Napoleon (Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# Intersphinx — link to numpy/scipy/matplotlib docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

# Theme
html_theme = "furo"
html_title = "evtol-tools"
