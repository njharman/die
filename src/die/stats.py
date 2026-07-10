class Statistic:
    """Roll lots of dice, calc statistics.

    ``sum``, ``avg``, and ``average`` are set by do_sum/do_bucket/do_run
    and are read only; treat them as results, not inputs.
    """

    def __init__(self, roll):
        """
        :param roll: ``Roll`` instance.
        """
        self.roll = roll
        self._bucket = dict()
        self.sum = 0
        self.avg = 0

    @property
    def bucket(self):
        result = list(self._bucket.items())
        result.sort()
        return result

    @property
    def average(self):
        """Alias for ``avg``."""
        return self.avg

    def _check(self, count):
        """Validate common preconditions shared by do_sum/do_bucket/do_run.
        :raises ValueError: If roll is not summable or count < 1
        """
        if not self.roll.summable:
            raise ValueError('Roll is not summable')
        if count < 1:
            raise ValueError('count must be >= 1')

    def do_sum(self, count=1):
        """Set self.sum, self.avg and return sum of dice rolled, count times.
        :param count: Number of rolls to make
        :return: Total sum of all rolls
        :raises ValueError: If roll is not summable or count < 1
        """
        self._check(count)
        self.sum = sum(self.roll.roll(count))
        self.avg = self.sum / count
        return self.sum

    def do_bucket(self, count=1):
        """Set self.bucket and return results.
        :param count: Number of rolls to make
        :return: List of tuples (total of roll, times it was rolled)
        :raises ValueError: If roll is not summable or count < 1
        """
        self._check(count)
        self._bucket = dict()
        for roll in self.roll.roll(count):
            self._bucket[roll] = self._bucket.get(roll, 0) + 1
        return self.bucket

    def do_run(self, count=1):
        """Roll count dice, store results. Does all stats so might be slower
        than specific doFoo methods. But, it is proly faster than running
        each of those separately to get same stats.

        Sets the following properties:
          - stats.bucket
          - stats.sum
          - stats.avg

        :param count: Number of rolls to make.
        :return: Total sum of all rolls
        :raises ValueError: If roll is not summable or count < 1
        """
        self._check(count)
        h = dict()
        total = 0
        for roll in self.roll.x_rolls(count):
            total += roll
            h[roll] = h.get(roll, 0) + 1
        self._bucket = h
        self.sum = total
        self.avg = total / count
        return self.sum
