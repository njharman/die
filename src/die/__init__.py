"""die

Classes to represent various dice, dice rolls, and stats on same.

Flexibility has priority over speed.

Die Classes
-----------
  - die.Standard
  - die.Numeric
  - die.NumericBased
  - die.Weird
  - die.Roll
  - die.FuncRoll

Support Classes
---------------
  - die.stats.Statistic
"""

__version__ = '1.0.0'

from .die import Numeric, NumericBased, Standard, Weird
from .roll import FuncRoll, Roll
from .stats import Statistic

__all__ = [
    'FuncRoll',
    'Numeric',
    'NumericBased',
    'Roll',
    'Standard',
    'Statistic',
    'Weird',
]
