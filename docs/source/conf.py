import sys
import os

sys.path.append(os.path.abspath('../..'))

project = 'users project'
copyright = '2024, DmytroSDV'
author = 'DmytroSDV'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinxdoc'
html_static_path = ['_static']
