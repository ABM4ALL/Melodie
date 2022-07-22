import os
import sys


def melodie_dir():
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    directory = root
    print(directory)
    return directory


sys.path.append(melodie_dir())
from sphinx.builders.html import StandaloneHTMLBuilder

# -- Project information -----------------------------------------------------

project = "Melodie"
copyright = "2021-2022, ABM4ALL"
author = "Songmin Yu, Zhanyi Hou"
release = "1.0.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
# They can be extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx_rtd_theme",
    "recommonmark",
    "sphinx_markdown_tables",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to excel_source directory, that match files and
# directories to ignore when looking for excel_source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"
html_logo = "image/logo.jpg"
html_theme_options = {"collapse_navigation": False}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a data named "default.css" will overwrite the builtin "default.css".
html_static_path = []
html_css_files = []
# This allows us to dynamically pick between gif and png images based on the build.
# For example, when we have something like:
# .. image:: that_directory/this_image.*
# Then the build will look for the image in that_directory in the following
# order. Because html supports gif, it will grab the gif image before the png,
# whereas because pdf does not support gif, it will grab the png.
StandaloneHTMLBuilder.supported_image_types = [
    "image/svg+xml",
    "image/gif",
    "image/png",
    "image/jpeg",
]
html_sidebars = {
    "**": ["globaltoc.html", "relations.html", "sourcelink.html", "searchbox.html"]
}
