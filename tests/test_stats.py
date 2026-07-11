import pytest

import die
import die.stats


class FakeRoll:
    """Test double satisfying the interface Statistic needs from a Roll:
    ``numeric`` and ``rolls(count)``. Lets bucket/sum aggregation be
    asserted against fixed values instead of real dice randomness.
    """

    def __init__(self, rolls, numeric=True):
        self.numeric = numeric
        self._rolls = list(rolls)

    def rolls(self, count):
        return list(self._rolls)


class TestStatistic:
    def test_roll_property_read_only(self):
        r = die.Roll((die.Standard(6),))
        s = die.stats.Statistic(r)
        assert s.roll is r
        with pytest.raises(AttributeError):
            s.roll = die.Roll()

    def test_results_raise_before_run(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        for attr in ('sum', 'avg', 'bucket'):
            with pytest.raises(RuntimeError, match='run'):
                getattr(s, attr)

    def test_run_default_count(self):
        s = die.stats.Statistic(die.Roll((die.Standard(1),)))
        assert s.run() == 1
        assert s.sum == 1
        assert s.avg == 1.0
        assert s.bucket == [(1, 1)]

    def test_run_sets_sum_avg_bucket(self):
        s = die.stats.Statistic(FakeRoll([2, 2, 3]))
        s.run(3)
        assert s.sum == 7
        assert s.avg == 7 / 3
        assert s.bucket == [(2, 2), (3, 1)]

    def test_run_returns_sum(self):
        s = die.stats.Statistic(FakeRoll([2, 2, 3]))
        assert s.run(3) == 7 == s.sum

    def test_bucket_property_sorted(self):
        s = die.stats.Statistic(FakeRoll([3, 1, 1, 2]))
        s.run(4)
        assert s.bucket == [(1, 2), (2, 1), (3, 1)]

    def test_run_resets_between_calls(self):
        fake = FakeRoll([1, 1, 2])
        s = die.stats.Statistic(fake)
        s.run(3)
        fake._rolls = [5, 5]
        s.run(2)
        assert s.bucket == [(5, 2)]
        assert s.sum == 10
        assert s.avg == 5.0

    def test_not_numeric_roll_raises(self):
        coin = die.Symbolic('coin', (('H', 'H', 1), ('T', 'T', 1)))
        with pytest.raises(ValueError, match='not numeric'):
            die.stats.Statistic(die.Roll((coin,)))

    def test_run_count_zero_raises(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        with pytest.raises(ValueError, match='count must be'):
            s.run(0)
