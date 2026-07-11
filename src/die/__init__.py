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
  - die.Symbolic

Roll Classes
------------
  - die.Roll

Support
-------
  - die.Statistic
  - die.parse
"""

__version__ = '2.0.0'

from .die import Die, Numeric, NumericBased, Standard, Symbolic
from .notation import parse
from .roll import Roll
from .stats import Statistic

__all__ = [
    'Die',
    'Numeric',
    'NumericBased',
    'Roll',
    'Standard',
    'Statistic',
    'Symbolic',
    'parse',
]
