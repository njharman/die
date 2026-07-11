"""Group Die instances into a single roll."""

import itertools
from collections import Counter, namedtuple

Odds = namedtuple('Odds', ('value', 'ways', 'probability'))


class Roll:
    """Groups a set of Die instances into a single roll.

    Two six-sided dice, summed::
        die.Roll([die.Standard(6), die.Standard(6)], name='2d6')

    obj() and obj.roll() both roll every die and return func(rolls).

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

    def __call__(self):
        """Roll all the dice."""
        return self.roll()

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
    def summable(self):
        """True if all ``Die`` in Roll can be numerically summed."""
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
