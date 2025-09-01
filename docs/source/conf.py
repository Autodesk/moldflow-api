# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Configuration file for the Sphinx documentation builder."""

#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.insert(
    0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'src', 'moldflow')
)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'moldflow-api'
copyright = '2025, Autodesk'
author = 'Autodesk'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Supports Google-style/Numpy-style docstrings
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    "show-inheritance": True,
    "undoc-members": True,
    "members": True,
    "exclude-members": "__init__",
    "class-doc-from": "class",
}
napoleon_include_special_with_doc = False
autodoc_class_signature = "separated"
add_module_names = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    "back_to_top_button": False,
    "github_url": "https://github.com/Autodesk/moldflow-api",
    "external_links": "",
    "footer_end": "",
    "footer_start": "copyright",
}
html_static_path = ['_static']
html_title = "Moldflow API"
html_favicon = '_static/autodesk-moldflow-product-icon.svg'
html_css_files = ['custom.css']
html_logo = '_static/autodesk-moldflow-product-icon.svg'


def skip_member(app, what, name, obj, skip, options):
    # Check if the docstring contains a custom hide marker
    doc = getattr(obj, "__doc__", "")
    if doc and ".. internal::" in doc:
        return True  # Skip this function/class/etc.
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip_member)
