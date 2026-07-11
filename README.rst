die
===

About
-----
A dice library, for RPG and Board Game games, experiments, whatever.

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

    from die import d6, d20x, d100p   # ready-made dice
    d6.roll()          # -> single roll, e.g. 4
    d20x.roll()        # -> d20 that explodes (rolls again and adds) on a 20
    d100p.roll()       # -> Hackmaster style penetrating d100, explodes to d20

    import die

    d6 = die.Standard(6)
    d6.roll()          # -> single roll, e.g. 4
    d6.rolls(3)        # -> list of three rolls, e.g. [2, 6, 1]
    d6 + 3             # -> roll + 3

    # Exploding die, on 5-6 rolls and adds another die roll, recursively.
    d6x = die.ExplodingDie(6, explode_range=2)
    d20x = die.ExplodingDie(20)  # default is explode on max value (6)

    # Hackmaster style: math correct (subtracts 1 per explosion).
    d6p = die.ExplodingDie(6, math_correct=True)
    d20p = die.ExplodingDie(20, explode_to=d6p, math_correct=True)
    d20p.roll()

    # Rolemaster style double-ended: explodes up on 96-100, down (subtracts) on 1-5.
    d100rm = die.ExplodingDie(100, explode_range=5, explode_range_low=5)
    d100rm.roll()

    roll = die.Roll((die.Standard(6), die.Standard(6)))
    roll.roll()        # 2d6
    best = die.Roll((d6, d6), func=max)
    best.roll()        # -> higher of two d6

    attack = die.parse('2d6+3')   # construct roll from dice notation; also NdF fudge dice

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
