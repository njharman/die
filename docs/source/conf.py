import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from die import __version__

project = 'die'
copyright = '2026, Norman J. Harman Jr.'
author = 'Norman J. Harman Jr.'
release = __version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

# Params documented on class docstrings, not __init__.
autoclass_content = 'both'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

html_theme = 'furo'
