import operator

import pytest

import die.die
import die.rolls


class StubRng:
    """Deterministic rng: choice returns face at fixed index, choices repeats it."""

    def __init__(self, index=0):
        self.index = index

    def choice(self, seq):
        return seq[self.index]

    def choices(self, seq, k=1):
        return [seq[self.index]] * k


class TestRoll:
    dice = (die.die.Standard(6), die.die.Standard(6))

    def test_init(self):
        r = die.rolls.Roll()
        r = die.rolls.Roll(self.dice)
        assert r.dice == self.dice
        assert r.description == '2d6 Roll'

    def test_init_name(self):
        r = die.rolls.Roll(self.dice, name='Attack Roll')
        assert r.name == 'Attack Roll'

    def test_name_read_only(self):
        r = die.rolls.Roll(self.dice, name='Attack Roll')
        with pytest.raises(AttributeError):
            r.name = 'Defense Roll'

    def test_str_uses_name_when_set(self):
        r = die.rolls.Roll(self.dice, name='Attack Roll')
        assert str(r) == 'Attack Roll'

    def test_str_falls_back_to_description(self):
        r = die.rolls.Roll(self.dice)
        assert str(r) == r.description == '2d6 Roll'

    def test_call_rolls(self):
        r = die.rolls.Roll(self.dice)
        assert 2 <= r() <= 12

    def test_description_groups_nonadjacent_matching_dice(self):
        r = die.rolls.Roll([die.die.Standard(6), die.die.Standard(8), die.die.Standard(6)])
        assert r.description == '2d6, 1d8 Roll'

    def test_description_empty_roll(self):
        r = die.rolls.Roll()
        assert r.description == ' Roll'

    def test_dice_property_returns_tuple(self):
        r = die.rolls.Roll(self.dice)
        assert isinstance(r.dice, tuple)
        assert len(r.dice) == 2

    def test_odds(self):
        r = die.rolls.Roll(self.dice)
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

    def test_odds_named_fields(self):
        r = die.rolls.Roll(self.dice)
        first = r.odds[0]
        assert first.value == 2
        assert first.ways == 1
        assert first.probability == 1 / 36

    def test_odds_is_cached(self):
        r = die.rolls.Roll(self.dice)
        first = r.odds
        second = r.odds
        assert first is second

    def test_odds_single_die(self):
        r = die.rolls.Roll([die.die.Standard(4)])
        assert r.odds == [(1, 1, 0.25), (2, 1, 0.25), (3, 1, 0.25), (4, 1, 0.25)]

    def test_odds_empty_roll(self):
        assert die.rolls.Roll().odds == []

    def test_odds_uses_func(self):
        r = die.rolls.Roll(self.dice, func=max)
        proper = [(v, 2 * v - 1, (2 * v - 1) / 36) for v in range(1, 7)]
        assert r.odds == proper

    def test_odds_non_numeric(self):
        coin = die.die.Symbolic('coin', (('H', 'H', 1), ('T', 'T', 1)))
        r = die.rolls.Roll([coin, coin], func=''.join)
        assert r.odds == [
            ('HH', 1, 0.25),
            ('HT', 1, 0.25),
            ('TH', 1, 0.25),
            ('TT', 1, 0.25),
        ]

    def test_numeric(self):
        r = die.rolls.Roll(self.dice)
        assert r.numeric
        r = die.rolls.Roll([die.die.Standard(6), die.die.Symbolic('Al', (('a', 'a', 1),))])
        assert not r.numeric

    def test_add_die_remove_die(self):
        r = die.rolls.Roll()
        r.add_die(die.die.Standard(8))
        r.add_die(die.die.Standard(6), 3)
        assert len(r.dice) == 4
        r.remove_die(die.die.Standard(6))
        assert len(r.dice) == 3

    def test_add_die_invalidates_odds_cache(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        assert r.odds == [(x, 1, 0.16666666666666666) for x in range(1, 7)]
        r.add_die(die.die.Standard(6))
        assert r.odds != [(x, 1, 0.16666666666666666) for x in range(1, 7)]
        assert len(r.odds) == 11

    def test_remove_die_invalidates_odds_cache(self):
        d6 = die.die.Standard(6)
        r = die.rolls.Roll([d6, d6])
        assert len(r.odds) == 11
        r.remove_die(d6)
        assert r.odds == [(x, 1, 0.16666666666666666) for x in range(1, 7)]

    def test_remove_die_not_present_raises(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        with pytest.raises(ValueError, match='not in list'):
            r.remove_die(die.die.Standard(8))
        assert len(r.dice) == 1

    def test_remove_die_removes_only_first_match(self):
        d6 = die.die.Standard(6)
        r = die.rolls.Roll([d6, d6, d6])
        r.remove_die(d6)
        assert len(r.dice) == 2

    def test_roll(self):
        r = die.rolls.Roll(self.dice)
        assert 2 <= r.roll() <= 12

    def test_roll_applies_func(self):
        r = die.rolls.Roll(self.dice, func=max)
        for _ in range(20):
            assert 1 <= r.roll() <= 6
        r = die.rolls.Roll(self.dice, func=lambda values: values)
        assert len(r.roll()) == 2

    def test_rolls_returns_list(self):
        r = die.rolls.Roll(self.dice)
        result = r.rolls(5)
        assert len(result) == 5
        assert all(2 <= x <= 12 for x in result)

    def test_rolls_applies_func(self):
        r = die.rolls.Roll(self.dice, func=min)
        assert all(1 <= x <= 6 for x in r.rolls(5))

    def test_roll_empty_dice(self):
        r = die.rolls.Roll()
        assert r.roll() == 0
        assert r.rolls(3) == [0, 0, 0]

    def test_from_notation(self):
        r = die.rolls.Roll.from_notation('3d6+2')
        assert isinstance(r, die.rolls.Roll)
        assert r.name == '3d6+2'
        assert len(r.dice) == 4
        assert 5 <= r.roll() <= 20

    def test_repr(self):
        r = die.rolls.Roll(self.dice, name='Attack Roll')
        text = repr(r)
        assert text.startswith('<Roll(')
        assert 'Attack Roll' in text

    def test_unhashable(self):
        r = die.rolls.Roll(self.dice)
        with pytest.raises(TypeError):
            hash(r)
        with pytest.raises(TypeError):
            {r}  # noqa: B018

    def test_equality_compares_dice_and_func(self):
        a = die.rolls.Roll(self.dice)
        b = die.rolls.Roll((die.die.Standard(6), die.die.Standard(6)), name='other name')
        assert a == b
        assert not (a != b)
        assert a != die.rolls.Roll([die.die.Standard(6)])
        assert a != die.rolls.Roll(self.dice, func=max)
        assert (a == 'not a roll') is False
        assert a != 'not a roll'

    def test_equality_does_not_roll(self):
        def boom(values):
            raise AssertionError('rolled')

        a = die.rolls.Roll(self.dice, func=boom)
        b = die.rolls.Roll(self.dice, func=boom)
        assert a == b


class TestRollOperators:
    """Deterministic dice: each rolls 3, Roll totals 6."""

    def deterministic(self):
        d = die.die.Standard(6, rng=StubRng(2))
        return die.rolls.Roll((d, d))

    def test_coercion(self):
        r = self.deterministic()
        assert r() == 6
        assert int(r) == 6
        assert float(r) == 6.0

    def test_index(self):
        r = self.deterministic()
        seq = list(range(10))
        assert operator.index(r) == 6
        assert seq[r] == 6

    def test_operators(self):
        r = self.deterministic()
        assert r + 1 == 7
        assert 1 + r == 7
        assert r - 1 == 5
        assert 7 - r == 1
        assert r * 3 == 18
        assert 3 * r == 18
        assert r / 2 == 3.0
        assert 3 / r == 0.5
        assert r // 4 == 1
        assert 13 // r == 2
        assert r % 4 == 2
        assert 13 % r == 1
        assert r**2 == 36
        assert 2**r == 64

    def test_comparisons(self):
        r = self.deterministic()
        assert (r > 5) is True
        assert (r >= 6) is True
        assert (r < 6) is False
        assert (r <= 6) is True
