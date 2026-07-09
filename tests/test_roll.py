import die.die
import die.roll


class TestRoll:
    dice = (die.die.Standard(6), die.die.Standard(6))

    def test_init(self):
        r = die.roll.Roll()
        r = die.roll.Roll(self.dice)
        assert [repr(s) for s in r.dice] == [repr(s) for s in self.dice]
        assert r.description == '2d6 Roll'

    def test_odds(self):
        r = die.roll.Roll(self.dice)
        proper = [
            (2, 1, 0.027777777777777776),
            (3, 2, 0.055555555555555552),
            (4, 3, 0.083333333333333329),
            (5, 4, 0.1111111111111111),
            (6, 5, 0.1388888888888889),
            (7, 6, 0.16666666666666666),
            (8, 5, 0.1388888888888889),
            (9, 4, 0.1111111111111111),
            (10, 3, 0.083333333333333329),
            (11, 2, 0.055555555555555552),
            (12, 1, 0.027777777777777776),
        ]
        assert r.odds == proper

    def test_summable(self):
        r = die.roll.Roll(self.dice)
        assert r.summable
        r = die.roll.Roll([die.die.Standard(6), die.die.Weird('Al', (('a', 'a', 1),))])
        assert not r.summable

    def test_add_die_remove_die(self):
        r = die.roll.Roll()
        r.add_die(die.die.Standard(8))
        r.add_die(die.die.Standard(6), 3)
        assert len(r.dice) == 4
        r.remove_die(die.die.Standard(6))
        assert len(r.dice) == 3

    def test_roll(self):
        r = die.roll.Roll(self.dice)
        r.roll()
        r.roll(100)
        r.roll(func=min)
        assert len(r.roll(func=lambda x: x)) == 2

    def test_iter(self):
        r = die.roll.Roll(self.dice)
        gen_one = r.iter()
        gen_seq = r.iter(2)
        for _ in range(100):
            assert 2 <= next(gen_one) <= 12
            assert len(next(gen_seq)) == 2
