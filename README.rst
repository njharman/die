die
===

About
-----
die is a dice library, for RPG and Board Game games, experiments, whatever.

Speed / efficiency are not priorities.


Installing
----------
via uv::

    uv add die

via pip::

    pip install die


Using
-----
::

    import die

    d6 = die.Standard(6)
    d6.roll()          # -> single roll, e.g. 4
    d6 + 3             # -> roll + 3

    roll = die.Roll((die.Standard(6), die.Standard(6)))
    roll.roll()        # -> sum of both dice

See ``examples/demo.py`` for a fuller walk through.


Testing
-------

    ruff check .
    pytest

pre-commit_ runs ``ruff check`` and ``ruff format`` automatically before each commit::

    pre-commit install
    pre-commit run --all-files


History
-------

1.0.0
  No API changes.
  Modern packaging: MIT license, python 3.14.
  uv with pyproject.toml/hatchling, ruff, pytest.
  pre-commit hooks.
  GitHub Actions CI.

0.4.0
  Backwards incompatible.
  Operators, coercions, comparisons roll die, str() no longer does)

0.3.0
  Merged rolls() into roll(), renamed tuple_* to, added die.items property.
  str() rolls die,

0.2.0
  Updated to modern style, pep8, tests, docs, travis-ci, more unittests.
  Py3.x support.

0.1.0
  Initial release.


.. _pre-commit: https://pre-commit.com/
