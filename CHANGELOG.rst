Changelog
=========

3.0.0
  Backwards incompatible changes:
    - ``Die``/``Roll`` ``name`` constructor parameter and property renamed ``notation``.
    - ``Die.numeric`` is now a read-only property computed from face values; assigning to it
      raises AttributeError, and a ``Symbolic`` die whose values are all numeric is numeric.
    - Cut ``Die``/``Roll`` ``rolls()``; use ``roll(count, func=list)`` instead.
    - Cut ``Die`` ``roll_items(count)``; build a list of rolls with ``roll_item()`` in a
      loop/comprehension instead.
    - ``Die``/``Roll`` ``roll()``/``__call__()`` now take ``count`` (number of rolls, default 1)
      and ``func`` (applied to the list of ``count`` results, default ``sum``) parameters;
      ``func`` always runs, so a non-numeric (``Symbolic``) ``Die``'s ``sum``-based default no
      longer applies (see ``Symbolic`` default below).
    - ``Die``/``Roll`` ``==``/``!=`` now roll and compare the result, like every other operator;
      compare ``Die.items``/``Roll.dice`` for structural equality.
    - ``Die``/``Roll`` ``str()`` now rolls and returns the result as a string, like
      ``int()``/``float()``; use the ``notation`` property for the textual identifier.
    - ``Roll`` ``notation`` constructor parameter removed; ``Roll.notation`` is always derived:
      composed from the contained dice on a plain summed Roll, the composed expression on a
      Roll built by the compose methods, and ``'<unsupported>'`` when underivable (empty Roll
      or constructor-supplied custom ``func``).
    - ``Roll.description`` composes the contained dice descriptions instead of notations.
    - ``Roll`` die grouping (``description``, derived ``notation``) no longer merges dice with
      identical faces but different notation (e.g. ``d6`` vs exploding ``d6x``).
    - Cut ``Roll.add_die``/``remove_die``; a Roll's dice are fixed at construction. Compose a
      new Roll (``plus()``) or rebuild one (``Roll(obj.dice + (die,))``) instead.
    - Cut ``Die.roll_item()``; use ``result`` after ``roll()`` instead.
    - ``ExplodingDie`` renamed ``Exploding``.
    - ``dFudge`` ready-made die renamed ``dF``, its notation is now ``'dF'``, and its blank
      face text is ``' '``, matching parser-created Fudge dice.
    - ``Statistic.avg`` renamed ``mean``.
    - ``Statistic.bucket`` replaced by ``counts``, returning a ``Counter`` of rolled values;
      ``sorted(stat.counts.items())`` recovers the old list.
    - ``Statistic.run()`` returns ``self`` (was the sum) and accumulates rolls across calls
      (was replacing them); ``clear()`` resets.
  New functionality:
    - ``Roll`` ``name``: read/write free-text label attribute (constructor parameter, default
      ``''``); shown by ``repr()``, independent of ``notation``.
    - ``Roll.from_notation(obj.notation)`` recreates an equivalent Roll (same dice and odds)
      whenever every contained die's notation is itself parseable.
    - ``Die``/``Roll`` compose methods ``plus``, ``minus``, ``times``, ``div``, ``mod``: each
      returns a new ``Roll`` combining the operands (Die, Roll, or number) without rolling;
      chains bind tight, left to right.
    - ``div()`` is float division then rounding: half up to ``ndigits`` decimal places (default
      0, returning int), ``rounding='up'``/``'down'`` round fractions up/down, ``ndigits=None``
      skips rounding.
    - Dice notation supports ``*``, ``/``, ``//``, ``%``, unary ``-``, and parentheses with
      standard operator precedence; ``parse()`` builds through the compose methods.
    - ``Die.result``, ``Die.face``, ``Die.value``: read-only properties for the most recently
      rolled face/value; raise ``RuntimeError`` until ``roll()`` has been called.
    - ``Roll.results``, ``Roll.value``: read-only properties for the most recently rolled
      per-die results and aggregated value; raise ``RuntimeError`` until ``roll()`` has
      been called.
    - ``Die``/``Roll`` retain every roll; subscript (``die[0]``, ``roll[-1]``), slice, or
      iterate to access past roll values; ``result``/``value`` etc. return the most recent.
    - ``Die``/``Roll`` ``history``: read-only property listing full past-roll records in roll
      order (``Die`` a ``Result(face, value)`` namedtuple, ``Roll`` a ``Rolled(results, value)``
      record).
    - Non-numeric ``Symbolic`` overrides the default ``func``: ``roll()``/``()`` return the
      single rolled value at ``count=1``, or a list of values otherwise, instead of raising
      via ``sum``; a numeric ``Symbolic`` keeps the ``sum`` default like every other ``Die``.
    - ``Die``/``Roll`` compose methods ``keep_highest``, ``keep_lowest``, ``drop_highest``,
      ``drop_lowest``: each returns a new ``Roll`` over the same dice keeping/dropping the
      ``n`` (default 1) highest/lowest die values and summing the kept.
    - Ready-made ``die.compass4`` (four point compass rose: N/E/S/W) and ``die.compass8``
      (eight point compass rose: N/NE/E/SE/S/SW/W/NW) dice, valued by bearing in degrees.
    - ``Die``/``Roll`` ``len()``: number of rolls in the roll history; ``clear()``: empties it.
    - ``Die`` ``name``: read/write free-text label attribute (default ``''``); shown by
      ``repr()``, independent of ``notation``, matching ``Roll.name``.
    - ``Odds``, ``Rolled``, and ``Result`` namedtuples exported from ``die``.
    - Ready-made ``die.d100lo``/``die.d100ho`` (Rolemaster low/high open-ended d100) exported;
      they existed but were missing from ``__all__``.
    - ``Roll.from_notation`` is a classmethod (was a staticmethod).
    - Ready-made ``die.d4d6dl`` (D&D style ability score roll: four d6, drop lowest, summed).
    - Ready-made ``die.d66`` (two d6 read sequentially as tens/ones digits).
    - Ready-made ``die.d09`` (d10 read 0-9, '0' counts as 0 not 10).
    - Ready-made ``die.doubling`` (backgammon doubling die: 2/4/8/16/32/64).
    - Ready-made ``die.averaging`` (2/3/3/4/4/5).
    - Ready-made FFG narrative dice ``die.gsys_boost``, ``die.gsys_setback``,
      ``die.gsys_ability``, ``die.gsys_difficulty``, ``die.gsys_proficiency``,
      ``die.gsys_challenge``, ``die.gsys_force`` (Genesys, Star Wars); each face value is
      a ``Counter`` of symbols.
    - Ready-made ``die.scatter`` and ``die.blast`` (Warhammer 40k scatter and
      blast/artillery dice).
    - Dice notation supports keep/drop suffixes ``kh``, ``kl``, ``dh``, ``dl`` with optional
      count on a dice term or parenthesized group, e.g. ``4d6dl``, ``2d20kh``, ``(3d6+2d4)kh2``.
    - Dice notation supports exploding (``x``) and penetrating (``p``) suffixes on a dice
      term, e.g. ``d6x``, ``3d6p``.
    - ``Rerolling`` die class: rerolls values at or below ``reroll_range``, once (keeping the
      second roll) or until out of the range.
    - Dice notation supports reroll suffixes ``r`` (once) and ``rr`` (recursive) with optional
      range on a dice term, e.g. ``4d6r``, ``d10rr2``.
    - ``Die``/``Roll`` compose methods ``successes``, ``failures``: each returns a new ``Roll``
      over the same dice counting die values >= / <= a target instead of summing.
    - ``Die``/``Roll`` ``chance(gte=)``/``chance(lte=)`` returns the cumulative percentage
      chance of rolling at or above / at or below a value.
    - Dice notation supports counting suffixes ``>=N`` and ``<=N`` on a dice term or
      parenthesized group, e.g. ``6d10>=7``, ``6d10<=1``.
    - ``Statistic`` ``values``, ``count``, ``min``, ``max``, ``median``, ``mode``, ``stdev``,
      and ``frequencies`` (observed ``Odds`` per distinct value, the empirical counterpart
      of ``Roll.odds``) properties, and ``clear()``.
    - ``die.charts`` module: ASCII ``histogram`` and ``scatter`` charts, and Vega-Lite spec
      emitters ``vega``, ``vega_scatter``, ``vega_compare``; each takes a ``Roll``/``Die``
      (theoretical odds) or ``Statistic`` (observed frequencies).
    - Base ``Die`` ``description`` now describes its faces (matching ``Numeric``/``Symbolic``/etc.)
      instead of just echoing ``notation``.
    - ``Constant`` die class: one-faced die that always rolls its value, consuming no
      randomness; composed and parsed numeric constants (the 2 in ``d6+2``) are ``Constant``
      instances.
    - ``examples/demo.py`` split into ``demo_die.py``, ``demo_rolls.py``, and ``demo_stats.py``
      (``demo.py`` runs all three), with roll history, keep/drop, odds, ``chance()``,
      ``Statistic``, and ``die.charts`` examples added.
  Bug Fixes:
    - ``examples/demo.py`` used ``Roll.add_die`` and a ``notation=`` constructor argument, both
      cut earlier in this version; updated to build the Roll from a list and use ``name=``.
    - ``Roll.results`` (and history ``results``) repeated the last roll for every occurrence of
      a ``Die`` instance appearing more than once in ``dice`` (e.g. ``parse('3d6')``).
    - ``test_d100rm`` asserted a ``-5`` lower bound that low open-ended explosion can exceed;
      replaced with deterministic ``SequenceRng`` tests covering the normal, low, and high paths.
    - Replaced probabilistic range-loop assertions in the exploding, penetrating, and dice-notation
      tests with deterministic seeded-rng checks of exact explosion, penetration, and min/max values.

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
