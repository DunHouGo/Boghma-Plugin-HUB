# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ualib'
copyright = '2023, JACKADUX'
author = 'JACKADUX'
release = 'v1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.napoleon',
              'sphinx.ext.todo',
              'sphinx.ext.coverage',
              'sphinx.ext.intersphinx'
              ]

import os, sys
path = r"D:\boghma\boghma hub\libs\boghma"
sys.path.insert(0, path)
path = r"D:\C4D 2023\resource\modules\python\libs\python39"
sys.path.insert(0, path)

templates_path = ['_templates']
exclude_patterns = []

language = 'chinese'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme' # 这个主题比较好看
html_static_path = ['_static']
