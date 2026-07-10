import die.die
import die.roll


class TestRoll:
    dice = (die.die.Standard(6), die.die.Standard(6))

    def test_init(self):
        r = die.roll.Roll()
        r = die.roll.Roll(self.dice)
        assert [repr(s) for s in r.dice] == [repr(s) for s in self.dice]
        assert r.description == '2d6 Roll'

    def test_init_name(self):
        r = die.roll.Roll(self.dice, name='Attack Roll')
        assert r.name == 'Attack Roll'

    def test_str_uses_name_when_set(self):
        r = die.roll.Roll(self.dice, name='Attack Roll')
        assert str(r) == 'Attack Roll'

    def test_str_falls_back_to_description(self):
        r = die.roll.Roll(self.dice)
        assert str(r) == r.description == '2d6 Roll'

    def test_call_rolls(self):
        r = die.roll.Roll(self.dice)
        assert 2 <= r() <= 12
        assert len(r(func=lambda x: x)) == 2

    def test_description_groups_nonadjacent_matching_dice(self):
        r = die.roll.Roll([die.die.Standard(6), die.die.Standard(8), die.die.Standard(6)])
        assert r.description == '2d6, 1d8 Roll'

    def test_description_empty_roll(self):
        r = die.roll.Roll()
        assert r.description == ' Roll'

    def test_dice_property_returns_copy(self):
        r = die.roll.Roll(self.dice)
        result = r.dice
        result.append(die.die.Standard(20))
        assert len(r.dice) == 2

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

    def test_odds_is_cached(self):
        r = die.roll.Roll(self.dice)
        first = r.odds
        second = r.odds
        assert first is second

    def test_odds_single_die(self):
        r = die.roll.Roll([die.die.Standard(4)])
        assert r.odds == [(1, 1, 0.25), (2, 1, 0.25), (3, 1, 0.25), (4, 1, 0.25)]

    def test_odds_non_summable(self):
        coin = die.die.Weird('coin', (('H', 'H', 1), ('T', 'T', 1)))
        r = die.roll.Roll([coin, coin])
        assert r.odds == [
            ('HH', 1, 0.25),
            ('HT', 1, 0.25),
            ('TH', 1, 0.25),
            ('TT', 1, 0.25),
        ]

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

    def test_add_die_invalidates_odds_cache(self):
        r = die.roll.Roll([die.die.Standard(6)])
        assert r.odds == [(x, 1, 0.16666666666666666) for x in range(1, 7)]
        r.add_die(die.die.Standard(6))
        assert r.odds != [(x, 1, 0.16666666666666666) for x in range(1, 7)]
        assert len(r.odds) == 11

    def test_remove_die_invalidates_odds_cache(self):
        d6 = die.die.Standard(6)
        r = die.roll.Roll([d6, d6])
        assert len(r.odds) == 11
        r.remove_die(d6)
        assert r.odds == [(x, 1, 0.16666666666666666) for x in range(1, 7)]

    def test_remove_die_not_present_is_noop(self):
        r = die.roll.Roll([die.die.Standard(6)])
        r.remove_die(die.die.Standard(8))
        assert len(r.dice) == 1

    def test_remove_die_removes_only_first_match(self):
        d6 = die.die.Standard(6)
        r = die.roll.Roll([d6, d6, d6])
        r.remove_die(d6)
        assert len(r.dice) == 2

    def test_roll(self):
        r = die.roll.Roll(self.dice)
        r.roll()
        r.roll(100)
        r.roll(func=min)
        assert len(r.roll(func=lambda x: x)) == 2

    def test_roll_count_returns_list_of_sums(self):
        r = die.roll.Roll(self.dice)
        result = r.roll(5)
        assert len(result) == 5
        assert all(2 <= x <= 12 for x in result)

    def test_roll_empty_dice(self):
        r = die.roll.Roll()
        assert r.roll() == 0
        assert r.roll(3) == [0, 0, 0]

    def test_x_rolls_default(self):
        r = die.roll.Roll(self.dice)
        results = list(r.x_rolls(5))
        assert len(results) == 5
        assert all(2 <= x <= 12 for x in results)

    def test_x_rolls_with_count(self):
        r = die.roll.Roll(self.dice)
        results = list(r.x_rolls(3, count=2))
        assert len(results) == 3
        assert all(len(x) == 2 for x in results)

    def test_x_rolls_with_func(self):
        r = die.roll.Roll(self.dice)
        results = list(r.x_rolls(5, func=min))
        assert all(1 <= x <= 6 for x in results)

    def test_iter(self):
        r = die.roll.Roll(self.dice)
        gen_one = r.iter()
        gen_seq = r.iter(2)
        for _ in range(100):
            assert 2 <= next(gen_one) <= 12
            assert len(next(gen_seq)) == 2

    def test_iter_with_func(self):
        r = die.roll.Roll(self.dice)
        gen = r.iter(func=max)
        for _ in range(20):
            assert 1 <= next(gen) <= 6


class TestFuncRoll:
    dice = (die.die.Standard(6), die.die.Standard(6))

    def test_init(self):
        r = die.roll.FuncRoll(max, self.dice, name='Best of Two')
        assert r.name == 'Best of Two'
        assert [repr(s) for s in r.dice] == [repr(s) for s in self.dice]

    def test_roll_applies_func(self):
        r = die.roll.FuncRoll(max, self.dice)
        for _ in range(20):
            assert 1 <= r.roll() <= 6

    def test_roll_count_returns_list(self):
        r = die.roll.FuncRoll(max, self.dice)
        result = r.roll(5)
        assert len(result) == 5
        assert all(1 <= x <= 6 for x in result)

    def test_call_delegates_to_roll(self):
        r = die.roll.FuncRoll(max, self.dice)
        assert 1 <= r() <= 6

    def test_x_rolls(self):
        r = die.roll.FuncRoll(min, self.dice)
        results = list(r.x_rolls(5))
        assert len(results) == 5
        assert all(1 <= x <= 6 for x in results)

    def test_x_rolls_with_count(self):
        r = die.roll.FuncRoll(min, self.dice)
        results = list(r.x_rolls(3, count=2))
        assert len(results) == 3
        assert all(len(x) == 2 for x in results)

    def test_iter(self):
        r = die.roll.FuncRoll(max, self.dice)
        gen = r.iter()
        for _ in range(20):
            assert 1 <= next(gen) <= 6

    def test_iter_with_count(self):
        r = die.roll.FuncRoll(max, self.dice)
        gen = r.iter(count=2)
        for _ in range(20):
            assert len(next(gen)) == 2

    def test_inherits_roll_properties(self):
        r = die.roll.FuncRoll(max, self.dice)
        assert r.summable
        assert r.description == '2d6 Roll'
        assert len(r.odds) == 11
