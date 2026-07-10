class Roll:
    """Groups a set of die instances into a single roll."""

    def __init__(self, dice=(), name=''):
        """:param dice: list of dice this roll is composed of"""
        self.name = name
        self._dice = list()
        self._odds = None
        for d in dice:
            self.add_die(d)

    def __str__(self):
        return self.name or self.description

    def __call__(self, *args, **kwargs):
        return self.roll(*args, **kwargs)

    @property
    def description(self):
        groups = []
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
        """List of ``Die`` in Roll."""
        return self._dice[:]

    @property
    def summable(self):
        """True if all ``Die`` in Roll can be numerically added."""
        return all(die.numeric for die in self._dice)

    @property
    def odds(self):
        """Odd Structure."""
        if self._odds is None:
            self._calc_odds()
        return self._odds

    def add_die(self, die, count=1):
        """Add ``Die`` to Roll.
        :param die: Die instance
        :param count: number of times die is rolled
        """
        for _ in range(count):
            self._dice.append(die)
        self._odds = None

    def remove_die(self, die):
        """Remove ``Die`` (first matching) from Roll.
        :param die: Die instance
        """
        if die in self._dice:
            self._dice.remove(die)
            self._odds = None

    def roll(self, count=0, func=sum):
        """Roll some dice!
        :param count: [0] Return list of sums
        :param func: [sum] Apply func to list of individual die rolls func([])
        :return: A single sum or list of ``count`` sums
        """
        if count:
            return [func([die.roll() for die in self._dice]) for x in range(count)]
        return func([die.roll() for die in self._dice])

    def x_rolls(self, number, count=0, func=sum):
        """Iterator of number dice rolls.
        :param count: [0] Return list of ``count`` sums
        :param func: [sum] Apply func to list of individual die rolls func([])
        """
        for _ in range(number):
            yield self.roll(count, func)

    def iter(self, count=0, func=sum):
        """Iterator of infinite dice rolls.
        :param count: [0] Return list of ``count`` sums
        :param func: [sum] Apply func to list of individual die rolls func([])
        """
        while True:
            yield self.roll(count, func)

    def _calc_odds(self):
        """Calculates the absolute probability of all possible rolls."""

        def recur(val, h, dice, combinations):
            for pip in dice[0]:
                tot = val + pip
                if len(dice) > 1:
                    combinations = recur(tot, h, dice[1:], combinations)
                else:
                    combinations += 1
                    h[tot] = h.get(tot, 0) + 1
            return combinations

        if self.summable:
            start = 0
        else:
            start = ''
        h = dict()
        funky = [d.values for d in self._dice]
        # count of possible results of rolling dice
        combinations = recur(start, h, funky, 0.0)
        self._odds = [(roll, h[roll], h[roll] / combinations) for roll in h]
        self._odds.sort()


class FuncRoll(Roll):
    """Apply func to roll."""

    def __init__(self, func, dice=(), name=''):
        """
        :param func: Apply func to list of individual die rolls func([])
        """
        self._func = func
        super().__init__(dice, name)

    def roll(self, count=0):
        """Roll some dice!
        :param count: [0] Return list of sums
        :return: A single sum or list of ``count`` sums
        """
        return super().roll(count, self._func)

    def x_rolls(self, number, count=0):
        """Iterator of number dice rolls.
        :param count: [0] Return list of ``count`` sums
        """
        for _ in range(number):
            yield super().roll(count, self._func)

    def iter(self, count=0):
        """Iterator of infinite dice rolls.
        :param count: [0] Return list of ``count`` sums
        """
        while True:
            yield super().roll(count, self._func)
