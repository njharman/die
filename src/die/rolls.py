"""Group Die instances into a single roll."""

import itertools
from collections import Counter, namedtuple

Odds = namedtuple('Odds', ('value', 'ways', 'probability'))


class Roll:
    """Groups a set of Die instances into a single roll.

    Two six-sided dice, summed::
        die.Roll([die.Standard(6), die.Standard(6)], name='2d6')

    obj() and obj.roll() both roll every die and return func(rolls).

    Constraints (same as ``Die``):
      - Roll are not hashable.
      - Roll are numeric if obj.numeric == True.
      - Two Roll are equal if they have identical dice and func.
      - obj(), int(obj), float(obj), obj.roll() return result of rolling all dice.
      - +, -, *, //, /, %, ** and >, >=, <, <= operators cause dice roll and use
        that result; they only reliably succeed when the Roll is numeric.
      - ==, != do NOT cause dice roll.
      - Comparisons (>, >=, <, <=) and sorting all roll the dice, so results are
        not stable/repeatable between comparisons.

    Differences from ``Die``:
      - No ``faces``, ``values``, ``items``, or ``sides`` properties; use ``dice`` (tuple of
        component ``Die`` instances) instead.
      - No ``roll_item``/``roll_items``; only the aggregated ``func`` result is available, not
        each component die's rolled face text.
      - ``__eq__`` compares the ``dice`` list (order matters) and ``func``.
      - ``__init__`` does not raise on an empty/default ``dice=()``, unlike ``Die`` which
        requires at least one face.

    Properties (all read only):
      - name: short textual identifier.
      - description: textual description.
      - dice: tuple of ``Die`` instances in Roll.
      - numeric: [boolean] True if all Die in Roll can be numerically summed.
      - odds: list of ``Odds(value, ways, probability)``, one per distinct result.

    :param dice: List of dice this roll is composed of.
    :param name: Optional textual identifier.
    :param func: [sum] Applied to list of individual die rolls, func([...]).
    """

    def __init__(self, dice=(), name='', func=sum):
        self._name = name
        self._func = func
        self._dice = list()
        self._odds = None
        for d in dice:
            self.add_die(d)

    def __str__(self):
        return self._name or self.description

    def __repr__(self):
        return f'<{self.__class__.__name__}({self}, {self._dice})>'

    def __call__(self):
        """Roll all the dice."""
        return self.roll()

    def __int__(self):
        """Rolls dice."""
        return int(self.roll())

    def __float__(self):
        """Rolls dice."""
        return float(self.roll())

    def __index__(self):
        """Rolls dice."""
        return int(self.roll())

    def __gt__(self, other):
        """Rolls dice."""
        return self.roll() > other

    def __ge__(self, other):
        """Rolls dice."""
        return self.roll() >= other

    def __lt__(self, other):
        """Rolls dice."""
        return self.roll() < other

    def __le__(self, other):
        """Rolls dice."""
        return self.roll() <= other

    def __add__(self, other):
        """Rolls dice."""
        return self.roll() + other

    def __radd__(self, other):
        """Rolls dice."""
        return self.roll() + other

    def __sub__(self, other):
        """Rolls dice."""
        return self.roll() - other

    def __rsub__(self, other):
        """Rolls dice."""
        return other - self.roll()

    def __mul__(self, other):
        """Rolls dice."""
        return self.roll() * other

    def __rmul__(self, other):
        """Rolls dice."""
        return self.roll() * other

    def __truediv__(self, other):
        """Rolls dice."""
        return self.roll() / other

    def __rtruediv__(self, other):
        """Rolls dice."""
        return other / self.roll()

    def __floordiv__(self, other):
        """Rolls dice."""
        return self.roll() // other

    def __rfloordiv__(self, other):
        """Rolls dice."""
        return other // self.roll()

    def __mod__(self, other):
        """Rolls dice."""
        return self.roll() % other

    def __rmod__(self, other):
        """Rolls dice."""
        return other % self.roll()

    def __pow__(self, other):
        """Rolls dice."""
        return self.roll() ** other

    def __rpow__(self, other):
        """Rolls dice."""
        return other ** self.roll()

    __hash__ = None

    def __eq__(self, other):
        if not isinstance(other, Roll):
            return False
        return self._dice == other._dice and self._func == other._func

    @staticmethod
    def from_notation(notation, rng=None):
        """Create a ``Roll`` from standard dice notation.

        :param notation: Dice notation string, e.g. ``'3d6+2'``.
        :param rng: Source of randomness given to created dice, overriding class-wide ``Die.rng``.
        :return: New ``Roll`` instance.
        :raises ValueError: If notation cannot be parsed.
        """
        from .notation import parse  # noqa: PLC0415 (circular import: notation imports Roll)

        return parse(notation, rng)

    @property
    def name(self):
        """Textual identifier."""
        return self._name

    @property
    def description(self):
        """Textual description of ``Die`` in Roll."""
        # TODO: refactor this with Counter
        groups = list()
        for die in self._dice:
            for group in groups:
                if group[0] == die:
                    group[1] += 1
                    break
            else:
                groups.append([die, 1])
        bits = [f'{count}{die}' for die, count in groups]
        return f'{", ".join(bits)} Roll'

    @property
    def dice(self):
        """Tuple of ``Die`` instances in Roll."""
        return tuple(self._dice)

    @property
    def numeric(self):
        """True if all ``Die`` in Roll are numeric, and so can be numerically summed."""
        return all(die.numeric for die in self._dice)

    @property
    def odds(self):
        """List of ``Odds(value, ways, probability)``, one per distinct result."""
        if self._odds is None:
            self._calc_odds()
        return self._odds

    def _calc_odds(self):
        """Calculate the absolute probability of every possible result."""
        if not self._dice:
            self._odds = []
            return
        counts = Counter(self._func(list(combo)) for combo in itertools.product(*(die.values for die in self._dice)))
        total = counts.total()
        self._odds = sorted(Odds(value, ways, ways / total) for value, ways in counts.items())

    def add_die(self, die, count=1):
        """Add ``Die`` to Roll.

        :param die: Die instance.
        :param count: Number of times die is added.
        """
        for _ in range(count):
            self._dice.append(die)
        self._odds = None

    def remove_die(self, die):
        """Remove first matching ``Die`` from Roll.

        :param die: Die instance.
        :raises ValueError: If die is not in Roll.
        """
        self._dice.remove(die)
        self._odds = None

    def roll(self):
        """Roll some dice!

        :return: func applied to list of individual die roll values.
        """
        return self._func([die.roll() for die in self._dice])

    def rolls(self, count):
        """Roll some dice, ``count`` times!

        :param count: Number of rolls.
        :return: List of ``count`` results, func applied to each roll separately.
        """
        return [self.roll() for _ in range(count)]
