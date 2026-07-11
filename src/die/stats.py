"""Roll dice repeatedly and calculate statistics."""

from collections import Counter


class Statistic:
    """Roll dice many times, report statistics.

    ``run()`` must be called before accessing ``sum``, ``avg``, or ``bucket``.

    Ten thousand rolls of 3d6::
        stat = die.Statistic(die.parse('3d6'))
        stat.run(10000)
        stat.avg

    :param roll: ``Roll`` instance.
    :raises ValueError: If roll is not summable.
    """

    def __init__(self, roll):
        if not roll.summable:
            raise ValueError('Roll is not summable')
        self._roll = roll
        self._bucket = None
        self._sum = None
        self._avg = None

    @property
    def roll(self):
        """``Roll`` statistics are calculated on."""
        return self._roll

    @property
    def sum(self):
        """Total of all rolls made by ``run()``."""
        self._check_ran()
        return self._sum

    @property
    def avg(self):
        """Average roll made by ``run()``."""
        self._check_ran()
        return self._avg

    @property
    def bucket(self):
        """List of (roll value, times rolled) tuples, sorted by value."""
        self._check_ran()
        return sorted(self._bucket.items())

    def _check_ran(self):
        if self._bucket is None:
            raise RuntimeError('run() has not been called')

    def run(self, count=1):
        """Roll ``count`` times, calculate statistics.

        Sets ``sum``, ``avg``, ``bucket``.

        :param count: Number of rolls to make.
        :return: Total sum of all rolls.
        :raises ValueError: If count < 1.
        """
        if count < 1:
            raise ValueError('count must be >= 1')
        self._bucket = Counter(self._roll.rolls(count))
        self._sum = sum(value * times for value, times in self._bucket.items())
        self._avg = self._sum / count
        return self._sum
