import unittest

import die
import die.stats


class StatsTestor(unittest.TestCase):
    def test_minimal(self):
        roll = die.Roll((die.Standard(6),))
        s = die.stats.Statistic(roll)
        s.do_sum()
        s.do_bucket(2)
        s.do_run(2)
