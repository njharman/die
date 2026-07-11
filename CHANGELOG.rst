Changelog
=========

2.1.0
  Backwards incompatible changes:
    - Module ``die.roll`` renamed ``die.rolls``, freeing the name for the new ``die.roll()``
      function. Only direct submodule imports are affected; ``die.Roll`` is unchanged.
    - ``Die``/``Roll`` ``__eq__`` returns ``False`` (not ``NotImplemented``) for non-``Die``/non-``Roll``
      comparisons, so ``other.__eq__`` is never tried as a fallback.
    - Cut ``Roll.summable``, redundant with ``Roll.numeric`` (identical behavior); use ``numeric`` instead.
  New functionality:
    - ``ExplodingDie``: rolls again (and adds) when landing in the explode range; supports
      Hackmaster style ``math_correct`` and Rolemaster style double-ended explosion
      (``explode_range_low``).
    - Ready-made dice constants (``d1``-``d10000``, exploding ``dNx``, penetrating ``dNp``,
      ``d100rm``, ``coin``, ``dFudge``) exported from ``die``.
    - ``d0`` null die, always rolls 0.
    - ``Roll.from_notation()`` builds a ``Roll`` from dice notation.
    - ``die.roll(notation)`` parses dice notation and rolls it once.
    - ``Roll`` interface parity with ``Die``: ``int()``/``float()``/``index``, comparisons, and
      arithmetic operators all roll the dice; ``==``/``!=`` compare dice and func without
      rolling; ``repr()``; ``numeric`` property.
  Bug Fixes:
    - Reflected subtraction was backwards: ``7 - d6`` computed ``roll - 7`` instead of ``7 - roll``.

2.0.0
  Backwards incompatible changes:
    - Weird die renamed to Symbolic.
    - ``roll()`` always returns a single result; new ``rolls(count)`` returns a list (``count=0`` scalar/list switching is gone). Applies to Die and Roll.
    - Rename ``tuple_roll`` to ``roll_item``; new ``roll_items(count)``.
    - Cut infinite generators ``iter``/``tuple_iter``/``Roll.iter`` and ``Roll.x_rolls``.
    - Merge ``FuncRoll`` into ``Roll(dice, name, func=sum)``; ``roll()`` no longer takes ``func``.
    - ``Roll.odds`` applies the Roll's ``func`` and returns ``Odds`` namedtuples; empty Roll has ``odds == []``.
    - Merge ``Statistic.do_sum``/``do_bucket``/``do_run`` into ``run(count)``.
    - ``Statistic.sum``/``avg``/``bucket`` are read-only properties, raise RuntimeError before ``run()``.
    - Cut ``Statistic.average`` alias.
    - Always were read-only, now enforced via properties: ``Die.name``/``description``, ``Roll.name``, ``Statistic.roll``.
      ``Roll.dice`` returns a tuple.
    - ``Roll.remove_die`` raises ValueError when die absent (list.remove semantics).
    - Die names are ``str()``-coerced (``Die(0, ...)`` now valid, name ``'0'``).
    - ``Standard`` rejects non-integral sides (``Standard(6.9)`` and ``Standard('6')`` raise).
  New functionality:
    - Dice notation parser ``die.parse('3d6+2d4-1')``, including fudge dice (``4dF``).
    - Seedable randomness: assign ``die.Die.rng`` (e.g. ``random.Random(seed)``) to affect every die, even ones already created; all die constructors accept ``rng=`` as a per-die override.
    - ``die.Die`` base class exported for rolling your own.
  Bug Fixes:
    - Die kept a live reference to caller's faces list; now copied.
    - ``Roll().odds`` on an empty roll raised IndexError.

1.1.0
  100% test coverage (line+branch) across all modules.
  Backwards incompatible Changes:
    - Statistic.avr renamed to Statistic.avg (Statistic.average added as alias).
    - Statistic.do_sum/do_bucket now raise ValueError for non-summable rolls or count < 1, matching do_run.
  Bug Fixes:
    - Roll.remove_die wasn't invalidating the cached odds (stale odds after removing a die).

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
