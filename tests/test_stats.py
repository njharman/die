import pytest

import die
import die.stats


class FakeRoll:
    """Test double satisfying the interface Statistic needs from a Roll:
    ``summable``, ``roll(count)``, ``x_rolls(count)``. Lets bucket/sum
    aggregation be asserted against fixed values instead of real dice
    randomness.
    """

    def __init__(self, rolls, summable=True):
        self.summable = summable
        self._rolls = list(rolls)

    def roll(self, count):
        return self._rolls

    def x_rolls(self, count):
        return iter(self._rolls)


class TestStatistic:
    def test_init_defaults(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        assert s.bucket == []
        assert s.sum == 0
        assert s.avg == 0
        assert s.average == 0

    def test_average_is_alias_for_avg(self):
        s = die.stats.Statistic(die.Roll((die.Standard(1),)))
        s.do_sum(4)
        assert s.average == s.avg == 1.0

    def test_bucket_property_sorted(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        s._bucket = {3: 1, 1: 2, 2: 1}
        assert s.bucket == [(1, 2), (2, 1), (3, 1)]

    def test_do_sum_default_count(self):
        s = die.stats.Statistic(die.Roll((die.Standard(1),)))
        assert s.do_sum() == 1
        assert s.sum == 1
        assert s.avg == 1.0

    def test_do_sum_with_count(self):
        s = die.stats.Statistic(die.Roll((die.Standard(1),)))
        assert s.do_sum(5) == 5
        assert s.sum == 5
        assert s.avg == 1.0

    def test_do_sum_not_summable_raises(self):
        coin = die.Weird('coin', (('H', 'H', 1), ('T', 'T', 1)))
        s = die.stats.Statistic(die.Roll((coin,)))
        with pytest.raises(ValueError, match='not summable'):
            s.do_sum()

    def test_do_sum_count_zero_raises(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        with pytest.raises(ValueError, match='count must be'):
            s.do_sum(0)

    def test_do_bucket_default_count(self):
        s = die.stats.Statistic(die.Roll((die.Standard(1),)))
        assert s.do_bucket() == [(1, 1)]

    def test_do_bucket_aggregates_repeats(self):
        s = die.stats.Statistic(FakeRoll([1, 1, 2, 3, 3, 3]))
        assert s.do_bucket(6) == [(1, 2), (2, 1), (3, 3)]

    def test_do_bucket_resets_between_calls(self):
        s = die.stats.Statistic(FakeRoll([1, 1, 2]))
        s.do_bucket(3)
        s.roll = FakeRoll([5, 5])
        assert s.do_bucket(2) == [(5, 2)]

    def test_do_bucket_not_summable_raises(self):
        coin = die.Weird('coin', (('H', 'H', 1), ('T', 'T', 1)))
        s = die.stats.Statistic(die.Roll((coin,)))
        with pytest.raises(ValueError, match='not summable'):
            s.do_bucket()

    def test_do_bucket_count_zero_raises(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        with pytest.raises(ValueError, match='count must be'):
            s.do_bucket(0)

    def test_do_bucket_return_matches_bucket_property(self):
        s = die.stats.Statistic(FakeRoll([1, 2, 2]))
        result = s.do_bucket(3)
        assert result == s.bucket

    def test_do_run_not_summable_raises(self):
        coin = die.Weird('coin', (('H', 'H', 1), ('T', 'T', 1)))
        s = die.stats.Statistic(die.Roll((coin,)))
        with pytest.raises(ValueError, match='not summable'):
            s.do_run()

    def test_do_run_sets_sum_avg_bucket(self):
        s = die.stats.Statistic(FakeRoll([2, 2, 3]))
        s.do_run(3)
        assert s.sum == 7
        assert s.avg == 7 / 3
        assert s.bucket == [(2, 2), (3, 1)]

    def test_do_run_resets_bucket_between_calls(self):
        s = die.stats.Statistic(FakeRoll([1, 1, 2]))
        s.do_run(3)
        s.roll = FakeRoll([5, 5])
        s.do_run(2)
        assert s.bucket == [(5, 2)]

    def test_do_run_returns_sum(self):
        s = die.stats.Statistic(FakeRoll([2, 2, 3]))
        assert s.do_run(3) == 7 == s.sum

    def test_do_run_count_zero_raises(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        with pytest.raises(ValueError, match='count must be'):
            s.do_run(0)
