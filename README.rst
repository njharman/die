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
    d6.rolls(3)        # -> list of three rolls, e.g. [2, 6, 1]
    d6 + 3             # -> roll + 3

    roll = die.Roll((die.Standard(6), die.Standard(6)))
    roll.roll()        # -> sum of both dice

    best = die.Roll((d6, d6), func=max)
    best.roll()        # -> higher of two d6

    attack = die.parse('2d6+3')   # dice notation; also NdF fudge dice
    attack.roll()

    import random
    die.Die.rng = random.Random(42)                  # reproducible rolls, all dice
    seeded = die.Standard(6, rng=random.Random(42))  # reproducible rolls, one die

See ``examples/demo.py`` for a fuller walk through.


Testing
-------

    ruff check .
    pytest

pre-commit_ runs ``ruff check`` and ``ruff format`` automatically before each commit::

    pre-commit install
    pre-commit run --all-files


Documentation
-------------
Full docs at `Read the Docs`_.

Build locally::

    uv sync --group docs
    uv run sphinx-build -b html docs/source docs/build

Then open ``docs/build/index.html`` in a browser.


History
-------
See CHANGELOG_ for release history and breaking changes.


.. _pre-commit: https://pre-commit.com/
.. _CHANGELOG: https://github.com/njharman/die/blob/main/CHANGELOG.rst
.. _Read the Docs: https://python-die.readthedocs.io
