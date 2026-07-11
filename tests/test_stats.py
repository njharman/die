import statistics
from collections import Counter

import pytest
from helpers import FakeRoll

import die
import die.stats


class TestStatistic:
    def test_roll_property_read_only(self):
        r = die.Roll((die.Standard(6),))
        s = die.stats.Statistic(r)
        assert s.roll is r
        with pytest.raises(AttributeError):
            s.roll = die.Roll()

    def test_statistics_raise_before_run(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        for attr in (
            'values',
            'sum',
            'mean',
            'min',
            'max',
            'median',
            'mode',
            'stdev',
            'counts',
            'frequencies',
        ):
            with pytest.raises(RuntimeError, match='run'):
                getattr(s, attr)

    def test_count_zero_before_run(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        assert s.count == 0

    def test_run_default_count(self):
        s = die.stats.Statistic(die.Roll((die.Standard(1),)))
        s.run()
        assert s.count == 1
        assert s.sum == 1
        assert s.mean == 1.0
        assert s.values == (1,)

    def test_run_returns_self(self):
        s = die.stats.Statistic(FakeRoll([2, 2, 3]))
        assert s.run(3) is s

    def test_values_in_roll_order(self):
        s = die.stats.Statistic(FakeRoll([3, 1, 1, 2])).run(4)
        assert s.values == (3, 1, 1, 2)

    def test_sum_mean(self):
        s = die.stats.Statistic(FakeRoll([2, 2, 3])).run(3)
        assert s.sum == 7
        assert s.mean == 7 / 3

    def test_min_max_median_mode_stdev(self):
        s = die.stats.Statistic(FakeRoll([3, 1, 1, 2])).run(4)
        assert s.min == 1
        assert s.max == 3
        assert s.median == 1.5
        assert s.mode == 1
        assert s.stdev == statistics.stdev([3, 1, 1, 2])

    def test_stdev_single_roll_raises(self):
        s = die.stats.Statistic(FakeRoll([4])).run(1)
        with pytest.raises(statistics.StatisticsError):
            _ = s.stdev

    def test_counts_is_counter(self):
        s = die.stats.Statistic(FakeRoll([3, 1, 1, 2])).run(4)
        assert s.counts == Counter({1: 2, 2: 1, 3: 1})
        assert s.counts[9] == 0

    def test_counts_copy_cannot_corrupt(self):
        s = die.stats.Statistic(FakeRoll([1, 2])).run(2)
        s.counts[1] = 99
        assert s.counts == Counter({1: 1, 2: 1})

    def test_frequencies(self):
        s = die.stats.Statistic(FakeRoll([3, 1, 1, 2])).run(4)
        assert s.frequencies == [
            die.Odds(1, 2, 0.5),
            die.Odds(2, 1, 0.25),
            die.Odds(3, 1, 0.25),
        ]

    def test_run_accumulates(self):
        fake = FakeRoll([1, 1, 2])
        s = die.stats.Statistic(fake)
        s.run(3)
        fake._rolls = [5, 5]
        s.run(2)
        assert s.values == (1, 1, 2, 5, 5)
        assert s.count == 5
        assert s.sum == 14

    def test_clear(self):
        s = die.stats.Statistic(FakeRoll([1, 2])).run(2)
        s.clear()
        assert s.count == 0
        with pytest.raises(RuntimeError, match='run'):
            _ = s.values

    def test_not_numeric_roll_raises(self):
        coin = die.Symbolic('coin', (('H', 'H', 1), ('T', 'T', 1)))
        with pytest.raises(ValueError, match='not numeric'):
            die.stats.Statistic(die.Roll((coin,)))

    def test_run_count_zero_raises(self):
        s = die.stats.Statistic(die.Roll((die.Standard(6),)))
        with pytest.raises(ValueError, match='count must be'):
            s.run(0)
