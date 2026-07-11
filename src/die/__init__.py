"""die.

Classes to represent various dice, dice rolls, and stats on same.

Flexibility has priority over speed.

All dice share ``die.Die.rng`` (default the random module) as their source of
randomness; assign it, e.g. ``die.Die.rng = random.Random(seed)``, to affect
every die at once. Pass ``rng`` to an individual die to override.

Die Classes
-----------
  - die.Die (base class, roll your own)
  - die.Standard
  - die.Numeric
  - die.NumericBased
  - die.ExplodingDie
  - die.Symbolic

Ready-made Dice
---------------
  - die.d0 (null die, always rolls 0)
  - die.d1...die.d20 (every value), plus die.d24, die.d30, die.d100, die.d1000, die.d10000
  - Exploding: die.d2x...die.d20x, plus die.d24x, die.d30x, die.d100x, die.d1000x, die.d10000x
  - Hackmaster penetrating: die.d2p...die.d100p
  - Rolemaster double-ended: die.d100rm
  - Coin flip: die.coin (heads=1, tails=0)
  - Fudge die: die.dFudge (Fudge/FATE: +=1, blank=0, -=-1)
  - die.d3d6 (Roll, three d6 summed)

Roll Classes
------------
  - die.Roll

Support
-------
  - die.Statistic
  - die.parse
  - die.roll
"""

__version__ = '2.1.0'

from .die import Die, ExplodingDie, Numeric, NumericBased, Standard, Symbolic
from .notation import parse, roll
from .rolls import Roll
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

d2x = ExplodingDie(2)
d3x = ExplodingDie(3)
d4x = ExplodingDie(4)
d5x = ExplodingDie(5)
d6x = ExplodingDie(6)
d7x = ExplodingDie(7)
d8x = ExplodingDie(8)
d9x = ExplodingDie(9)
d10x = ExplodingDie(10)
d11x = ExplodingDie(11)
d12x = ExplodingDie(12)
d13x = ExplodingDie(13)
d14x = ExplodingDie(14)
d15x = ExplodingDie(15)
d16x = ExplodingDie(16)
d17x = ExplodingDie(17)
d18x = ExplodingDie(18)
d19x = ExplodingDie(19)
d20x = ExplodingDie(20)
d24x = ExplodingDie(24)
d30x = ExplodingDie(30)
d100x = ExplodingDie(100)
d1000x = ExplodingDie(1000)
d10000x = ExplodingDie(10000)

# Hackmaster style math correct penetrating dice: subtract 1 from every rolled-again value.
# Some dice explode down to a smaller die (e.g. d20 explodes to d6).
d2p = ExplodingDie(2, math_correct=True)
d3p = ExplodingDie(3, math_correct=True)
d4p = ExplodingDie(4, math_correct=True)
d6p = ExplodingDie(6, math_correct=True)
d8p = ExplodingDie(8, math_correct=True)
d10p = ExplodingDie(10, math_correct=True)
d12p = ExplodingDie(12, math_correct=True)
d16p = ExplodingDie(16, math_correct=True)
d20p = ExplodingDie(20, explode_to=d6p, math_correct=True)
d24p = ExplodingDie(24, explode_to=d8p, math_correct=True)
d30p = ExplodingDie(30, explode_to=d12p, math_correct=True)
d100p = ExplodingDie(100, explode_to=d20p, math_correct=True)

# Rolemaster style double-ended die: explodes up on 96-100 (add), down on 1-5 (subtract).
d100rm = ExplodingDie(100, explode_range=5, explode_range_low=5)

# Fudge https://www.fudgerpg.com/ Fudge die
dFudge = NumericBased('dFudge', (('+', 1, 2), ('', 0, 2), ('-', -1, 2)))

# Coin flip: heads=1 (True), tails=0 (False)
coin = NumericBased('coin', (('heads', 1, 1), ('tails', 0, 1)))

d3d6 = Roll([d6, d6, d6], name='3d6')

__all__ = [
    'Die',
    'ExplodingDie',
    'Numeric',
    'NumericBased',
    'Roll',
    'Standard',
    'Statistic',
    'Symbolic',
    'coin',
    'd0',
    'd1',
    'd2',
    'd2p',
    'd2x',
    'd3',
    'd3d6',
    'd3p',
    'd3x',
    'd4',
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
    'd100',
    'd100p',
    'd100rm',
    'd100x',
    'd1000',
    'd1000x',
    'd10000',
    'd10000x',
    'dFudge',
    'parse',
    'roll',
]
