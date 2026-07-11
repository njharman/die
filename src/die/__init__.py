"""die.

Classes to represent various dice, dice rolls, and stats on same.

Flexibility has priority over speed.

All dice share ``die.Die.rng`` (default the random module) as their source of
randomness; assign it, e.g. ``die.Die.rng = random.Random(seed)``, to affect
every die at once. Pass ``rng`` to an individual die to override; ``del obj.rng``
reverts an overridden die to the class-wide ``rng``.

Die Classes
-----------
  - die.Die (base class, roll your own)
  - die.Standard
  - die.Numeric
  - die.NumericBased
  - die.Constant
  - die.Exploding
  - die.Rerolling
  - die.Symbolic

Ready-made Dice
---------------
  - die.d0 (null die, always rolls 0)
  - die.d09 (d10 read 0-9, '0' counts as 0 not 10)
  - die.d3d6 (Roll, three d6 summed)
  - die.d4d6dl (Roll, D&D ability score: four d6, drop lowest, summed)
  - die.d66 (Roll, two d6 read as tens/ones digits, e.g. rolling 4 then 3 gives 43)
  - die.d1...die.d20 (every value), plus die.d24, die.d30, die.d100, die.d1000, die.d10000
  - Exploding: die.d2x...die.d20x, plus die.d24x, die.d30x, die.d100x, die.d1000x, die.d10000x
  - Hackmaster penetrating: die.d2p...die.d100p
  - Rolemaster open-ended: die.d100rm (both ends), die.d100ho (high only), die.d100lo (low only)
  - Coin flip: die.coin (heads=1, tails=0)
  - Fudge die: die.dF (Fudge/FATE: +=1, blank=0, -=-1)
  - Backgammon doubling die: die.doubling (2/4/8/16/32/64)
  - Averaging die: die.averaging (2/3/3/4/4/5, mean 3.5)
  - Compass rose: die.compass4 (N/E/S/W), die.compass8 (N/NE/E/SE/S/SW/W/NW); values are
    compass bearing in degrees
  - FFG narrative dice (Genesys, Star Wars): die.gsys_boost, die.gsys_setback,
    die.gsys_ability, die.gsys_difficulty, die.gsys_proficiency, die.gsys_challenge,
    die.gsys_force; each face value is a Counter of symbols
    (success/advantage/failure/threat/triumph/despair/light/dark)
  - Warhammer 40k: die.scatter (HIT/arrow), die.blast (2/4/6/8/10/MISFIRE)

Roll Classes
------------
  - die.Roll

Composition
-----------
Die and Roll compose via ``plus``/``minus``/``times``/``div``/``mod`` methods, each returning
a new Roll; chains bind tight, left to right. ``keep_highest``/``keep_lowest``/``drop_highest``/
``drop_lowest`` keep/drop the n highest/lowest die values, summing the kept;
``successes``/``failures`` count die values >= / <= a target::

    die.d6.times(2).plus(3).div(die.d6)  # the Roll (d6*2+3)/d6
    die.parse('4d6').drop_lowest()       # the Roll 4d6dl
    die.parse('6d10').successes(7)       # the Roll 6d10>=7

``die.parse`` accepts the same expressions in dice notation (standard operator precedence,
keep/drop suffixes ``kh``/``kl``/``dh``/``dl``, counting suffixes ``>=``/``<=``)::

    die.parse('(d6*2+3)/d6')
    die.parse('4d6dl')
    die.parse('2d20kh')
    die.parse('6d10>=7')

Support
-------
  - die.Statistic
  - die.charts (ASCII histogram/scatter charts, Vega-Lite spec emitters)
  - die.parse
  - die.roll
  - die.Odds, die.Rolled (namedtuples returned by ``Roll.odds`` and ``Roll.history``)
  - die.Result (namedtuple in ``Die.history``)
"""

__version__ = '3.0.0'

from collections import Counter

from . import charts  # re-export: die.charts usable after `import die`
from .die import (
    Constant,
    Die,
    Exploding,
    Numeric,
    NumericBased,
    Rerolling,
    Result,
    Standard,
    Symbolic,
)
from .notation import parse, roll
from .rolls import Odds, Roll, Rolled
from .stats import Statistic

d0 = Numeric('d0', (0,))
d1 = Standard(1)
d2 = Standard(2)
d3 = Standard(3)
d4 = Standard(4)
d5 = Standard(5)
d6 = Standard(6)
d7 = Standard(7)
d8 = Standard(8)
d9 = Standard(9)
d10 = Standard(10)
d09 = Numeric('d09', tuple(range(10)))  # d10 read 0-9 ('0' counts as 0, not 10).
d11 = Standard(11)
d12 = Standard(12)
d13 = Standard(13)
d14 = Standard(14)
d15 = Standard(15)
d16 = Standard(16)
d17 = Standard(17)
d18 = Standard(18)
d19 = Standard(19)
d20 = Standard(20)
d24 = Standard(24)
d30 = Standard(30)
d100 = Standard(100)
d1000 = Standard(1000)
d10000 = Standard(10000)

# Exploding dice: roll again on max value, add to total, recursively.
# no d1x as it would explode infinitely
d2x = Exploding(2)
d3x = Exploding(3)
d4x = Exploding(4)
d5x = Exploding(5)
d6x = Exploding(6)
d7x = Exploding(7)
d8x = Exploding(8)
d9x = Exploding(9)
d10x = Exploding(10)
d11x = Exploding(11)
d12x = Exploding(12)
d13x = Exploding(13)
d14x = Exploding(14)
d15x = Exploding(15)
d16x = Exploding(16)
d17x = Exploding(17)
d18x = Exploding(18)
d19x = Exploding(19)
d20x = Exploding(20)
d24x = Exploding(24)
d30x = Exploding(30)
d100x = Exploding(100)
d1000x = Exploding(1000)
d10000x = Exploding(10000)

# Hackmaster style math correct penetrating dice: subtract 1 from every rolled-again value.
# Some dice explode down to a smaller die (e.g. d20 explodes to d6).
d2p = Exploding(2, math_correct=True)
d3p = Exploding(3, math_correct=True)
d4p = Exploding(4, math_correct=True)
d6p = Exploding(6, math_correct=True)
d8p = Exploding(8, math_correct=True)
d10p = Exploding(10, math_correct=True)
d12p = Exploding(12, math_correct=True)
d16p = Exploding(16, math_correct=True)
d20p = Exploding(20, explode_to=d6p, math_correct=True)
d24p = Exploding(24, explode_to=d8p, math_correct=True)
d30p = Exploding(30, explode_to=d12p, math_correct=True)
d100p = Exploding(100, explode_to=d20p, math_correct=True)

# Rolemaster style open-ended dicie explodes up on 96-100 (add), down on 1-5 (subtract).
d100rm = Exploding(100, explode_range=5, explode_range_low=5)  # both open ended
d100lo = Exploding(100, explode_range_low=5)  # low open ended
d100ho = Exploding(100, explode_range=5)  # high open ended

# d66: two d6 read sequentially as tens/ones digits (RPG convention: Traveller etc).
d66 = Roll([d6, d6], func=lambda values: values[0] * 10 + values[1], name='d66')

# B/X, OD&D ability score
d3d6 = Roll([d6, d6, d6])

# D&D ability score roll: 4d6, drop lowest.
d4d6dl = parse('4d6dl')

# Fudge https://www.fudgerpg.com/ Fudge die
dF = NumericBased('dF', (('+', 1, 2), (' ', 0, 2), ('-', -1, 2)))

# Coin flip: heads=1 (True), tails=0 (False)
coin = NumericBased('coin', (('heads', 1, 1), ('tails', 0, 1)))

# Backgammon doubling cube.
doubling = Numeric('doubling', (2, 4, 8, 16, 32, 64))

# Averaging die: reduced variance, mean 3.5 like a d6.
averaging = Numeric('averaging', (2, 3, 3, 4, 4, 5))


# Compass rose: values are compass bearing in degrees.
compass4 = NumericBased('compass4', (('N', 0, 1), ('E', 90, 1), ('S', 180, 1), ('W', 270, 1)))
compass8 = NumericBased(
    'compass8',
    (
        ('N', 0, 1),
        ('NE', 45, 1),
        ('E', 90, 1),
        ('SE', 135, 1),
        ('S', 180, 1),
        ('SW', 225, 1),
        ('W', 270, 1),
        ('NW', 315, 1),
    ),
)

# Fantasy Flight Games narrative dice (Genesys, Star Wars: EotE/AoR/FaD).
# Each face value is a Counter of symbols; blank faces are an empty Counter. Symbol
# cancellation (success vs failure, advantage vs threat) is left to the caller, e.g.
# ``gsys_boost.roll(2, func=lambda vs: sum(vs, Counter()))`` to total symbols across dice.
gsys_boost = Symbolic(
    'gsys_boost',
    (
        (' ', Counter(), 2),
        ('S', Counter(success=1), 1),
        ('SA', Counter(success=1, advantage=1), 1),
        ('AA', Counter(advantage=2), 1),
        ('A', Counter(advantage=1), 1),
    ),
)
gsys_setback = Symbolic(
    'gsys_setback',
    (
        (' ', Counter(), 2),
        ('F', Counter(failure=1), 2),
        ('T', Counter(threat=1), 2),
    ),
)
gsys_ability = Symbolic(
    'gsys_ability',
    (
        (' ', Counter(), 1),
        ('S', Counter(success=1), 2),
        ('SS', Counter(success=2), 1),
        ('A', Counter(advantage=1), 2),
        ('SA', Counter(success=1, advantage=1), 1),
        ('AA', Counter(advantage=2), 1),
    ),
)
gsys_difficulty = Symbolic(
    'gsys_difficulty',
    (
        (' ', Counter(), 1),
        ('F', Counter(failure=1), 1),
        ('FF', Counter(failure=2), 1),
        ('T', Counter(threat=1), 3),
        ('TT', Counter(threat=2), 1),
        ('FT', Counter(failure=1, threat=1), 1),
    ),
)
gsys_proficiency = Symbolic(
    'gsys_proficiency',
    (
        (' ', Counter(), 1),
        ('S', Counter(success=1), 2),
        ('SS', Counter(success=2), 2),
        ('A', Counter(advantage=1), 1),
        ('SA', Counter(success=1, advantage=1), 3),
        ('AA', Counter(advantage=2), 2),
        ('Tri', Counter(triumph=1), 1),
    ),
)
gsys_challenge = Symbolic(
    'gsys_challenge',
    (
        (' ', Counter(), 1),
        ('F', Counter(failure=1), 2),
        ('FF', Counter(failure=2), 2),
        ('T', Counter(threat=1), 2),
        ('FT', Counter(failure=1, threat=1), 2),
        ('TT', Counter(threat=2), 2),
        ('Des', Counter(despair=1), 1),
    ),
)
gsys_force = Symbolic(
    'gsys_force',
    (
        ('Dk', Counter(dark=1), 6),
        ('DkDk', Counter(dark=2), 1),
        ('Lt', Counter(light=1), 2),
        ('LtLt', Counter(light=2), 3),
    ),
)

# Warhammer 40k
# scatter die: 4 arrow faces (scatter in the arrow direction), 2 HIT faces.
scatter = Symbolic('scatter', (('HIT', 'HIT', 2), ('arrow', 'arrow', 4)))
# blast/artillery die: numeric shots, or MISFIRE.
blast = Symbolic(
    'blast',
    (
        ('2', 2, 1),
        ('4', 4, 1),
        ('6', 6, 1),
        ('8', 8, 1),
        ('10', 10, 1),
        ('MISFIRE', 'MISFIRE', 1),
    ),
)

__all__ = [
    'Constant',
    'Die',
    'Exploding',
    'Numeric',
    'NumericBased',
    'Odds',
    'Rerolling',
    'Result',
    'Roll',
    'Rolled',
    'Standard',
    'Statistic',
    'Symbolic',
    'averaging',
    'blast',
    'coin',
    'compass4',
    'compass8',
    'd0',
    'd09',
    'd1',
    'd2',
    'd2p',
    'd2x',
    'd3',
    'd3d6',
    'd3p',
    'd3x',
    'd4',
    'd4d6dl',
    'd4p',
    'd4x',
    'd5',
    'd5x',
    'd6',
    'd6p',
    'd6x',
    'd7',
    'd7x',
    'd8',
    'd8p',
    'd8x',
    'd9',
    'd9x',
    'd10',
    'd10p',
    'd10x',
    'd11',
    'd11x',
    'd12',
    'd12p',
    'd12x',
    'd13',
    'd13x',
    'd14',
    'd14x',
    'd15',
    'd15x',
    'd16',
    'd16p',
    'd16x',
    'd17',
    'd17x',
    'd18',
    'd18x',
    'd19',
    'd19x',
    'd20',
    'd20p',
    'd20x',
    'd24',
    'd24p',
    'd24x',
    'd30',
    'd30p',
    'd30x',
    'd66',
    'd100',
    'd100ho',
    'd100lo',
    'd100p',
    'd100rm',
    'd100x',
    'd1000',
    'd1000x',
    'd10000',
    'd10000x',
    'dF',
    'doubling',
    'gsys_ability',
    'gsys_boost',
    'gsys_challenge',
    'gsys_difficulty',
    'gsys_force',
    'gsys_proficiency',
    'gsys_setback',
    'parse',
    'roll',
    'scatter',
]
