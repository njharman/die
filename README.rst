die
===
A dice library.

For use in dice mechanics explorations, probability experiments, and little
tools for Table Top RPGs and Board Games. Not designed or optimized to be used
in computer games, high CPU simulations or the like.


Installing
----------
via uv::

    uv add die

via pip::

    pip install die

Also on PyPI_.


Quickstart
----------
::

    from die import d6

    d6() or d6.roll()       # roll a ready-made six-sided die
    # Die, also return result of roll when mathed, compared, or coerced
    result = d6 + 3         # adds 3 to result of rolling d6
    if d6 > 3:              # if roll is greater than 3, prints 'lucky!'
        print('lucky!')
    d6 == 6                 # True if roll equals 3
    print(f'rolled a {d6}') # conversion to string rolls d6
    result = float(d6)      # rolls d6, coerces to float

    import die

    die.roll('3d6+2')           # parse dice notation, roll it once
    d8d6 = die.d8.plus(die.d6)  # compose dice (d8+d6)


Usage
-----
See ``examples/`` for runnable walk throughs of everything die library has to
offer: ``demo_die.py`` (dice), ``demo_rolls.py`` (rolls, notation, composing,
odds), ``demo_stats.py`` (statistics and charts); ``demo.py`` runs all three.


Standard Dice
~~~~~~~~~~~~~
``Standard(sides)`` is the common numeric die. Ready-made instances (``d1``...``d20``,
``d24``, ``d30``, ``d100``, ``d1000``, ``d10000``) are importable directly::

    from die import d6, d20 # ready-made dice
    d6()                    # -> single roll, e.g. 4

    import die
    d69 = die.Standard(69)  # or construct your own
    d6(3)                   # -> sum of three rolls
    d6(3, max)              # -> max of three rolls
    d6(3, func=list)        # -> return individual rolls as a list

After a roll, the die remembers it::

    d6.roll()
    d6.result          # -> (face, value) of the most recent roll
    d6.face            # -> face text, e.g. '4'
    d6.value           # -> value, e.g. 4

The die retains every roll; subscript it to reach older ones (this does not roll)::

    d6.roll(3)         # roll three times
    d6[0]              # -> first roll's value
    d6[-1]             # -> most recent value, same as d6.value
    list(d6)           # -> all rolled values, in order
    sum(d6)            # -> total of every retained roll
    d6.history         # -> full Result(face, value) records, in order
    len(d6)            # -> number of retained rolls
    d6.clear()         # empty the history


Exploding dice
~~~~~~~~~~~~~~
``Exploding`` rolls again and adds when it rolls into the explode range, recursively.
Ready-made: ``d2x``...``d10000x`` (explode on max), ``d2p``...``d100p`` (Hackmaster
penetrating), ``d100rm`` (Rolemaster double-ended)::

    d20x = die.Exploding(20)                 # explodes on 20 (the max), rolls itself again
    d6x = die.Exploding(6, explode_range=2)  # explodes on 5-6

    # Hackmaster style: math correct (subtracts 1 per explosion), may explode to a smaller die.
    d6p = die.Exploding(6, math_correct=True)
    d20p = die.Exploding(20, explode_to=d6p, math_correct=True)

    # Rolemaster style double-ended: explodes up on 96-100 and down (subtracts) on 1-5.
    d100rm = die.Exploding(100, explode_range=5, explode_range_low=5)


Rerolling dice
~~~~~~~~~~~~~~
``Rerolling`` rolls again (replacing original roll) when it rolls into the reroll range::

    d6r = die.Rerolling(6)                          # rerolls 1s once, keeps the second roll
    d6rr2 = die.Rerolling(6, reroll_range=2, once=False)  # rerolls 1-2 until it rolls 3+


Custom dice
~~~~~~~~~~~
Dice need not be sequential, numeric, or even mappable to numbers::

    # Numeric: non-sequential numeric faces, e.g. a backgammon doubling die.
    doubling = die.Numeric('doubling', (2, 4, 8, 16, 32, 64))
    # Ready-made: die.doubling (2/4/8/16/32/64), die.averaging (2/3/3/4/4/5, mean
    # 3.5), die.d09 (d10 read 0-9, '0' counts as 0 not 10).

    # NumericBased: textual faces with numeric values; (face, value, count) spec.
    fudge = die.NumericBased('dF', (('+', 1, 2), (' ', 0, 2), ('-', -1, 2)))
    # Ready-made: die.dF and die.coin (heads=1, tails=0).

    # Symbolic: values need not be numeric; roll() returns the value
    # (a list of them when count > 1).
    pet = die.Symbolic('pet', (('bark', 'dog', 2), ('meow', 'cat', 1)))
    pet.roll()         # -> 'dog' or 'cat'
    # Ready-made: Warhammer 40k die.scatter (HIT/arrow) and die.blast (2/4/6/8/10/MISFIRE).

    # Die: the base class, roll your own from (face, value) pairs.
    d6 = die.Die('d6', (('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6)))


Gensys Narrative Dice
~~~~~~~~~~~~~~~~~~~~~
Ready-made FFG narrative dice (Genesys, Star Wars): ``gsys_boost``, ``gsys_setback``,
``gsys_ability``, ``gsys_difficulty``, ``gsys_proficiency``, ``gsys_challenge``,
``gsys_force``. Each ``Symbolic`` face value is a ``collections.Counter`` of symbols
(success/advantage/failure/threat/triumph/despair/light/dark); sum a pool's rolls to
total its symbols (cancellation is left to you)::

    from collections import Counter

    die.gsys_proficiency.roll()   # -> e.g. Counter({'success': 1, 'advantage': 1})
    pool = (die.gsys_proficiency, die.gsys_ability, die.gsys_difficulty)
    sum((d.roll() for d in pool), Counter())  # -> totalled symbols across the pool


Rolls
~~~~~
``Roll`` groups dice and applies ``func`` (default ``sum``) to their rolled values::

    roll = die.Roll((die.d6, die.d6))
    roll.notation      # -> '2d6', derived from the dice
    roll.roll()        # -> 2d6
    roll.roll(3)       # -> 2d6, three times, summed
    roll.roll(3, func=list)  # -> 2d6, three times, as a list

    best = die.Roll((die.d20, die.d20), func=max, name='advantage')
    best.roll()        # -> higher of two d20

    # A Roll's dice are fixed at construction; compose a new Roll to change them.
    bigger = roll.plus(die.d4)
    bigger.notation    # -> '2d6+d4'

Like ``Die``, a ``Roll`` remembers its most recent roll::

    roll.roll()
    roll.results       # -> ((face, value), ...) one per die
    roll.value         # -> the aggregated (func-applied) result

It retains every roll too; subscripting yields aggregate values (no roll)::

    roll.roll(3)
    roll[-1]                  # -> most recent value, same as roll.value
    roll[0]                   # -> first roll's value
    roll.history[-1]          # -> Rolled(results=((face, value), ...), value=...)
    roll.history[0].results   # -> first roll's per-die (face, value) tuples


Dice Notation
~~~~~~~~~~~~~
``parse()`` builds a ``Roll`` from standard dice notation: ``NdS`` terms, ``NdF`` Fudge
dice, integer constants, ``+ - * / // %``, parentheses, standard precedence, keep/drop
suffixes ``kh kl dh dl`` (optional count, default 1), counting suffixes ``>=N``/``<=N``,
and exploding/penetrating/reroll suffixes ``x``/``p``/``r``/``rr`` on a dice term (not
valid on Fudge dice)::

    attack = die.parse('2d6+3')
    attack.roll()
    die.parse('4dF')              # four Fudge dice
    die.parse('(d6*2+3)/d6')      # full expressions
    die.parse('4d6dl')            # 4d6, drop the lowest
    die.parse('2d20kh')           # 2d20, keep the highest
    die.parse('3d6x')             # three exploding d6, summed
    die.parse('d6p')              # one penetrating (Hackmaster math-corrected) d6
    die.parse('4d6r')             # four d6, each rerolling 1s once
    die.parse('6d10>=7')          # six d10, count of dice rolling 7+
    die.roll('3d6+2')             # parse and roll once, in one call


Composing
~~~~~~~~~
Die and Roll compose in code via ``plus``, ``minus``, ``times``, ``div``, ``mod`` — each
returns a new ``Roll`` instance (nothing rolls until you say so); chains bind
tight, left to right::

    combo = die.d6.times(2).plus(3).div(die.d6)   # the Roll (d6*2+3)/d6
    combo.roll()

``div()`` is float division, rounded half up to an int by default::

    die.d6.div(2)                    # fractions round half up
    die.d6.div(2, rounding='down')   # fractions round down (floor, //)
    die.d6.div(2, rounding='up', ndigits=2)  # fractions round up at 2 decimal places

``keep_highest``, ``keep_lowest``, ``drop_highest``, ``drop_lowest`` keep/drop the ``n`` (default 1)
highest/lowest die values and sum the kept::

    die.parse('4d6').drop_lowest()      # the Roll 4d6dl
    die.d20.plus(die.d20).keep_highest()     # the Roll (d20+d20)kh

``successes``, ``failures`` count die values >= / <= a target instead of summing (dice
pools)::

    die.parse('6d10').successes(7)      # the Roll 6d10>=7
    die.parse('6d10').failures(1)       # the Roll 6d10<=1


Odds
~~~~
Every numeric ``Roll`` knows its exact probabilities; ``chance()`` (on both Die
and Roll) answers "what are the odds of rolling N or better?"::

    roll = die.parse('3d6')
    roll.odds            # -> [Odds(value, ways, probability), ...] one per distinct result
    roll.odds[0]         # -> Odds(value=3, ways=1, probability=0.00463)
    roll.chance(gte=15)  # -> 9.26, percent chance of rolling 15 or higher
    die.d20.chance(lte=2)  # -> 10.0, percent chance of rolling 2 or lower

``odds`` is a Roll property; for a lone Die, compose or parse it into a Roll
first (``die.parse('d6').odds``). Odds are computed from face values, so they
are wrong for dice whose rolls don't come straight from their faces
(``Exploding``, ``Rerolling``).


Reproducible rolls
~~~~~~~~~~~~~~~~~~
Set your own seed for all Die. And/or, override specific Die::

    import random
    die.Die.rng = random.Random(42)                  # reproducible rolls, all dice
    seeded = die.Standard(6, rng=random.Random(42))  # reproducible rolls, one die


Statistics
~~~~~~~~~~
``Statistic`` rolls a numeric ``Roll`` many times and reports empirical
statistics (a non-numeric Roll raises ValueError). ``run()`` returns self, so
statistics chain; it also accumulates — repeated calls extend the rolled
values — and ``clear()`` empties them::

    die.Statistic(die.parse('3d6')).run(10_000).mean

    stat = die.Statistic(die.d3d6)
    stat.run(1000)
    stat.run(1000)     # now 2000 accumulated rolls
    stat.clear()       # back to none

Properties (all read only; every one but ``count`` raises RuntimeError until
``run()`` has been called)::

    stat.roll          # -> the Roll statistics are calculated on
    stat.count         # -> number of rolls made; 0 until run(), never raises
    stat.values        # -> tuple of every rolled value, in roll order
    stat.sum           # -> total of all rolled values
    stat.mean          # -> arithmetic mean of rolled values
    stat.min, stat.max # -> smallest / largest rolled value
    stat.median        # -> median of rolled values
    stat.mode          # -> most common rolled value (first rolled wins ties)
    stat.stdev         # -> sample standard deviation (StatisticsError if < 2 rolls)
    stat.counts        # -> collections.Counter of rolled values
    stat.frequencies   # -> observed Odds(value, ways, probability) per distinct
                       #    value, sorted; the empirical counterpart of Roll.odds


Charts
~~~~~~
``die.charts`` charts dice probabilities and rolled results (usable directly
after ``import die``). Chart functions take a ``Roll`` or ``Die`` (theoretical
probabilities, from ``odds``) or a ``Statistic`` (observed frequencies, from a
simulation).

ASCII charts return multi-line strings for terminals::

    print(die.charts.histogram(die.parse('3d6')))        # theoretical probability curve
    stat = die.Statistic(die.d3d6).run(10_000)
    print(die.charts.histogram(stat, width=40))          # observed, one bar per value
    print(die.charts.scatter(stat, width=70, height=10)) # rolled results, roll order vs value

Vega-Lite emitters return spec dicts; ``json.dumps()`` one and render it with
any Vega-Lite tool (https://vega.github.io/editor, VSCode, JupyterLab,
``vl-convert`` for PNG/SVG)::

    die.charts.vega(die.parse('3d6'))     # bar chart of probability per value
    die.charts.vega(stat, kind='line')    # same chart as a line
    die.charts.vega_scatter(stat)         # scatter of rolled results, roll order vs value
    die.charts.vega_compare(stat)         # observed frequency bars overlaid with theoretical odds line

``vega_compare``'s theoretical line carries the ``odds`` caveat: it is wrong
for ``Exploding``/``Rerolling`` dice; the observed bars show the real
distribution.


Warnings
~~~~~~~~
Every operator and coercion rolls the die — including equality and ``str()``::

    die.d6 + 3         # rolls, then adds 3
    die.d6 == die.d6   # rolls BOTH dice, compares the results!
    str(die.d6)        # rolls, returns the result as a string, same as int()/float()

Dice are not hashable, and comparing or sorting them gives unstable results.
Compare ``Die.items`` / ``Roll.dice`` for structural equality. Use the
``notation`` property, not ``str()``, to get a die/roll's textual name. Or,
set your own via ``name`` property.

The roll-state properties (``result``, ``face``, ``value``, ``results``) raise
RuntimeError until the first roll; subscripting into the roll history
(``obj[i]``) instead raises IndexError while empty, ``history`` is just empty,
and neither rolls.


Testing
-------
::

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
.. _PyPI: https://pypi.org/project/die/
