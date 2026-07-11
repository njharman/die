"""Roll dice repeatedly and calculate statistics."""

import statistics
from collections import Counter

from .rolls import Odds


class Statistic:
    def __init__(self, roll):
        """Roll dice many times, report statistics.

        Ten thousand rolls of 3d6::
            stat = die.Statistic(die.parse('3d6')).run(10_000)
            stat.mean

        ``run()`` accumulates: repeated calls extend the rolled values rather than
        replacing them; ``clear()`` empties them.

        Properties (all read only, raise RuntimeError until ``run()`` has been called):
          - values: tuple of every rolled value, in roll order.
          - sum: total of all rolled values.
          - mean: arithmetic mean of rolled values.
          - min, max: smallest/largest rolled value.
          - median: median of rolled values.
          - mode: most common rolled value (first rolled wins ties).
          - stdev: sample standard deviation of rolled values; raises
            ``statistics.StatisticsError`` with fewer than two rolls.
          - counts: ``Counter`` of rolled values.
          - frequencies: observed ``Odds(value, ways, probability)`` per distinct value,
            sorted by value; the empirical counterpart of ``Roll.odds``.

        ``count`` (number of rolls made) never raises; it is 0 until ``run()``.

        :param roll: ``Roll`` instance.
        :raises ValueError: If roll is not numeric.
        """
        if not roll.numeric:
            raise ValueError('Roll is not numeric')
        self._roll = roll
        self._values = []

    @property
    def roll(self):
        """``Roll`` statistics are calculated on."""
        return self._roll

    @property
    def count(self):
        """Number of rolls made; 0 until ``run()`` has been called."""
        return len(self._values)

    @property
    def values(self):
        """Tuple of every rolled value, in roll order."""
        self._check_ran()
        return tuple(self._values)

    @property
    def sum(self):
        """Total of all rolled values."""
        self._check_ran()
        return sum(self._values)

    @property
    def mean(self):
        """Arithmetic mean of rolled values."""
        self._check_ran()
        return statistics.fmean(self._values)

    @property
    def min(self):
        """Smallest rolled value."""
        self._check_ran()
        return min(self._values)

    @property
    def max(self):
        """Largest rolled value."""
        self._check_ran()
        return max(self._values)

    @property
    def median(self):
        """Median of rolled values."""
        self._check_ran()
        return statistics.median(self._values)

    @property
    def mode(self):
        """Most common rolled value; the first rolled wins ties."""
        self._check_ran()
        return statistics.mode(self._values)

    @property
    def stdev(self):
        """Sample standard deviation of rolled values.

        :raises statistics.StatisticsError: If fewer than two rolls have been made.
        """
        self._check_ran()
        return statistics.stdev(self._values)

    @property
    def counts(self):
        """``Counter`` of rolled values (a new Counter each access)."""
        self._check_ran()
        return Counter(self._values)

    @property
    def frequencies(self):
        """Observed ``Odds(value, ways, probability)`` per distinct value, sorted by value.

        The empirical counterpart of ``Roll.odds``: ``ways`` is times observed,
        ``probability`` is ways / ``count``.
        """
        self._check_ran()
        total = len(self._values)
        counts = Counter(self._values)
        return sorted(Odds(value, times, times / total) for value, times in counts.items())

    def _check_ran(self):
        if not self._values:
            raise RuntimeError('run() has not been called')

    def run(self, count=1):
        """Roll ``count`` times, accumulating onto any previous runs.

        :param count: Number of rolls to make.
        :return: self, so statistics chain: ``Statistic(roll).run(10_000).mean``.
        :raises ValueError: If count < 1.
        """
        if count < 1:
            raise ValueError('count must be >= 1')
        self._values.extend(self._roll.roll(count, func=list))
        return self

    def clear(self):
        """Empty the accumulated rolls.

        Afterward the statistic properties raise RuntimeError again, as before the
        first ``run()``.
        """
        self._values.clear()
