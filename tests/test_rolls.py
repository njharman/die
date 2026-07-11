import operator

import pytest
from helpers import SequenceRng, StubRng

import die.die
import die.rolls


class TestRoll:
    dice = (die.die.Standard(6), die.die.Standard(6))

    def test_init(self):
        r = die.rolls.Roll()
        r = die.rolls.Roll(self.dice)
        assert r.dice == self.dice
        assert r.description == 'Roll of 2 x Numeric die with 6 faces numbered 1 through 6.'

    def test_init_rejects_notation(self):
        with pytest.raises(TypeError):
            die.rolls.Roll(self.dice, notation='Attack Roll')

    def test_init_name(self):
        r = die.rolls.Roll(self.dice)
        assert r.name == ''
        r = die.rolls.Roll(self.dice, name='Attack Roll')
        assert r.name == 'Attack Roll'
        r.name = 'Defense Roll'
        assert r.name == 'Defense Roll'
        assert r.notation == '2d6'

    def test_notation_read_only(self):
        r = die.rolls.Roll(self.dice)
        with pytest.raises(AttributeError):
            r.notation = 'Defense Roll'

    def test_notation_derived_from_dice(self):
        assert die.rolls.Roll(self.dice).notation == '2d6'
        assert die.rolls.Roll([die.die.Standard(6), die.die.Standard(4)]).notation == 'd6+d4'
        assert die.rolls.Roll().notation == '<unsupported>'

    def test_notation_groups_constants_without_count_prefix(self):
        two = die.die.Constant(2)
        assert die.rolls.Roll([two, two]).notation == '2+2'

    def test_notation_does_not_group_same_faced_different_behavior_dice(self):
        # d6, d6x, d6p have identical faces but different roll behavior.
        r = die.rolls.Roll.from_notation('d6x+d6p+d6')
        assert r.notation == 'd6x+d6p+d6'
        assert die.rolls.Roll.from_notation(r.notation).notation == r.notation

    def test_notation_unsupported_for_custom_func(self):
        r = die.rolls.Roll(self.dice, func=max)
        assert r.notation == '<unsupported>'

    def test_notation_round_trips(self):
        for r in (
            die.rolls.Roll(self.dice),
            die.rolls.Roll([die.die.Standard(6), die.die.Standard(4), die.die.Standard(6)]),
            die.die.Standard(6).minus(2),
            die.rolls.Roll.from_notation('3d6+2d4-1'),
        ):
            r2 = die.rolls.Roll.from_notation(r.notation)
            assert sorted(d.items for d in r2.dice) == sorted(d.items for d in r.dice)
            assert r2.odds == r.odds
            assert r2.notation == r.notation

    def test_str_rolls(self):
        dice = (die.die.Standard(6, rng=StubRng(2)), die.die.Standard(6, rng=StubRng(2)))
        r = die.rolls.Roll(dice)
        assert str(r) == '6'

    def test_call_rolls(self):
        r = die.rolls.Roll(self.dice)
        assert 2 <= r() <= 12

    def test_description_groups_nonadjacent_matching_dice(self):
        r = die.rolls.Roll([die.die.Standard(6), die.die.Standard(8), die.die.Standard(6)])
        assert r.description == (
            'Roll of 2 x Numeric die with 6 faces numbered 1 through 6; '
            '1 x Numeric die with 8 faces numbered 1 through 8.'
        )

    def test_description_empty_roll(self):
        r = die.rolls.Roll()
        assert r.description == 'Roll of no dice.'

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

    def test_rebuild_with_more_dice(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        r = die.rolls.Roll((*r.dice, die.die.Standard(4), die.die.Standard(6)))
        assert r.notation == '2d6+d4'
        assert die.rolls.Roll.from_notation(r.notation).odds == r.odds
        assert r.times(2).notation == '(2d6+d4)*2'

    def test_roll(self):
        r = die.rolls.Roll(self.dice)
        assert 2 <= r.roll() <= 12

    def test_roll_applies_func(self):
        r = die.rolls.Roll(self.dice, func=max)
        for _ in range(20):
            assert 1 <= r.roll() <= 6
        r = die.rolls.Roll(self.dice, func=lambda values: values)
        assert len(r.roll(func=lambda values: values[0])) == 2

    def test_roll_count_returns_func_applied_to_list(self):
        r = die.rolls.Roll(self.dice)
        assert 10 <= r.roll(5) <= 60

    def test_roll_count_func_list_returns_individual_results(self):
        r = die.rolls.Roll(self.dice)
        result = r.roll(5, func=list)
        assert len(result) == 5
        assert all(2 <= x <= 12 for x in result)

    def test_roll_count_applies_inner_and_outer_func(self):
        r = die.rolls.Roll(self.dice, func=min)
        result = r.roll(5, func=list)
        assert all(1 <= x <= 6 for x in result)

    def test_roll_empty_dice(self):
        r = die.rolls.Roll()
        assert r.roll() == 0
        assert r.roll(3, func=list) == [0, 0, 0]

    def test_result_state_raises_before_roll(self):
        r = die.rolls.Roll(self.dice)
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            r.results  # noqa: B018
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            r.value  # noqa: B018

    def test_result_state_after_roll(self):
        d1 = die.die.Standard(6, rng=StubRng(1))  # face '2', value 2
        d2 = die.die.Standard(6, rng=StubRng(3))  # face '4', value 4
        r = die.rolls.Roll((d1, d2))
        assert r.roll() == 6
        assert r.results == (('2', 2), ('4', 4))
        assert r.value == 6

    def test_results_with_repeated_die_instance(self):
        # parse('3d6') and Roll([d6, d6]) reuse one Die instance; each roll's result must be
        # captured as it happens, not read back afterward (which would repeat the last roll).
        d = die.die.Standard(6, rng=SequenceRng([3, 5]))
        r = die.rolls.Roll((d, d))
        assert r.roll() == 8
        assert r.results == (('3', 3), ('5', 5))
        assert r.value == 8

    def test_result_properties_read_only(self):
        d1 = die.die.Standard(6, rng=StubRng(1))
        d2 = die.die.Standard(6, rng=StubRng(3))
        r = die.rolls.Roll((d1, d2))
        r.roll()
        for attr in ('results', 'value'):
            with pytest.raises(AttributeError):
                setattr(r, attr, 'nope')

    def test_history_records_rolled_records(self):
        d1 = die.die.Standard(6, rng=StubRng(1))  # face '2', value 2
        d2 = die.die.Standard(6, rng=StubRng(3))  # face '4', value 4
        r = die.rolls.Roll((d1, d2))
        assert r.history == []
        r.roll()
        assert r[-1] == 6
        assert r.history[-1] == die.rolls.Rolled(results=(('2', 2), ('4', 4)), value=6)
        assert r.history[-1].results == r.results
        assert r.history[-1].value == r.value

    def test_history_is_a_copy(self):
        r = die.rolls.Roll((die.die.Standard(6, rng=StubRng(1)),))
        r.roll()
        r.history.clear()
        assert len(r) == 1
        with pytest.raises(AttributeError):
            r.history = []

    def test_subscript_yields_values_in_order(self):
        d1 = die.die.Standard(6, rng=SequenceRng([1, 5]))
        d2 = die.die.Standard(6, rng=SequenceRng([2, 6]))
        r = die.rolls.Roll((d1, d2))
        r.roll(2, func=list)
        assert r[0] == 3
        assert r[1] == 11
        assert r[:] == [3, 11]
        assert r[-1] == r.value

    def test_history_accumulates_across_calls_and_slices_without_rolling(self):
        d1 = die.die.Standard(6, rng=StubRng(1))
        d2 = die.die.Standard(6, rng=StubRng(3))
        r = die.rolls.Roll((d1, d2))
        r.roll(2, func=list)
        r.roll()
        assert len(r[:]) == 3
        assert list(r) == r[0:3]

    def test_len_and_clear(self):
        d1 = die.die.Standard(6, rng=StubRng(1))
        r = die.rolls.Roll((d1,))
        assert len(r) == 0
        r.roll(2, func=list)
        assert len(r) == 2
        r.clear()
        assert len(r) == 0
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            r.results  # noqa: B018

    def test_subscript_before_roll_raises_indexerror(self):
        r = die.rolls.Roll(self.dice)
        with pytest.raises(IndexError):
            r[0]
        assert r[:] == []

    def test_from_notation(self):
        r = die.rolls.Roll.from_notation('3d6+2')
        assert isinstance(r, die.rolls.Roll)
        assert r.notation == '3d6+2'
        assert len(r.dice) == 4
        assert 5 <= r.roll() <= 20

    def test_repr(self):
        r = die.rolls.Roll(self.dice, name='Attack Roll')
        text = repr(r)
        assert text.startswith('<Roll(')
        assert 'Attack Roll' in text

    def test_repr_unnamed_uses_notation(self):
        r = die.rolls.Roll(self.dice)
        assert '2d6' in repr(r)

    def test_repr_falls_back_to_unsupported_notation(self):
        r = die.rolls.Roll()
        assert '<unsupported>' in repr(r)

    def test_unhashable(self):
        r = die.rolls.Roll(self.dice)
        with pytest.raises(TypeError):
            hash(r)
        with pytest.raises(TypeError):
            {r}  # noqa: B018

    def test_equality_rolls(self):
        d = die.die.Standard(6, rng=StubRng(2))
        r = die.rolls.Roll((d, d))
        assert (r == 6) is True
        assert (r != 6) is False
        assert (r == 7) is False
        assert (r != 7) is True


class TestRollOperators:
    """Deterministic dice: each rolls 3, Roll totals 6."""

    def deterministic(self):
        d = die.die.Standard(6, rng=StubRng(2))
        return die.rolls.Roll((d, d))

    def test_coercion(self):
        r = self.deterministic()
        assert r() == 6
        assert str(r) == '6'
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


class TestCompose:
    def constant(self, value):
        return die.die.Constant(value)

    def test_lifted_numbers_are_constant(self):
        r = die.die.Standard(6).plus(2)
        assert isinstance(r.dice[1], die.die.Constant)
        r = die.die.Standard(6).minus(2)
        assert isinstance(r.dice[1], die.die.Constant)
        assert r.dice[1].notation == '-2'

    def test_plus_die(self):
        r = die.die.Standard(6).plus(die.die.Standard(4))
        assert isinstance(r, die.rolls.Roll)
        assert r.notation == 'd6+d4'
        assert len(r.dice) == 2
        assert [o.value for o in r.odds] == list(range(2, 11))

    def test_plus_number(self):
        r = die.die.Standard(6).plus(2)
        assert r.notation == 'd6+2'
        assert [o.value for o in r.odds] == [3, 4, 5, 6, 7, 8]

    def test_plus_roll(self):
        a = die.rolls.Roll([die.die.Standard(6)])
        b = die.rolls.Roll([die.die.Standard(6)])
        r = a.plus(b)
        assert len(r.dice) == 2
        assert r.odds[-1].value == 12

    def test_plus_merges_summed_dice(self):
        r = die.die.Standard(6).plus(die.die.Standard(6)).plus(2)
        assert len(r.dice) == 3
        expected = die.rolls.Roll([die.die.Standard(6), die.die.Standard(6), self.constant(2)])
        assert r.odds == expected.odds

    def test_plus_negative_number_normalizes_to_minus(self):
        r = die.die.Standard(6).plus(-2)
        assert r.notation == 'd6-2'
        assert [o.value for o in r.odds] == [-1, 0, 1, 2, 3, 4]

    def test_minus_die(self):
        r = die.die.Standard(6).minus(die.die.Standard(4))
        assert r.notation == 'd6-d4'
        assert [o.value for o in r.odds] == list(range(-3, 6))

    def test_minus_number(self):
        r = die.die.Standard(6).minus(1)
        assert r.notation == 'd6-1'
        assert [o.value for o in r.odds] == [0, 1, 2, 3, 4, 5]

    def test_minus_negative_number_normalizes_to_plus(self):
        r = die.die.Standard(6).minus(-2)
        assert r.notation == 'd6+2'

    def test_minus_keeps_exploding_behavior(self):
        # Negating must not flatten an exploding die into its plain faces.
        exploding = die.die.Exploding(6, rng=SequenceRng([6, 3]))
        r = self.constant(0).minus(exploding)
        assert r.roll() == -9

    def test_times_number(self):
        r = die.die.Standard(6).times(2)
        assert r.notation == 'd6*2'
        assert [o.value for o in r.odds] == [2, 4, 6, 8, 10, 12]

    def test_times_die(self):
        r = die.die.Standard(6).times(die.die.Standard(6))
        assert r.notation == 'd6*d6'
        assert r.odds[-1].value == 36

    def test_mod(self):
        r = die.die.Standard(6).mod(3)
        assert r.notation == 'd6%3'
        assert r.odds == [(0, 2, 1 / 3), (1, 2, 1 / 3), (2, 2, 1 / 3)]

    def test_div_default_rounds_half_up_to_int(self):
        assert self.constant(4).div(2).roll() == 2
        assert self.constant(5).div(2).roll() == 3
        assert self.constant(-5).div(2).roll() == -2
        assert isinstance(self.constant(4).div(2).roll(), int)
        assert self.constant(5).div(2).notation == '5/2'

    def test_div_rounding_up_rounds_fractions_up(self):
        assert self.constant(41).div(4, rounding='up').roll() == 11
        assert self.constant(-41).div(4, rounding='up').roll() == -10
        assert self.constant(4).div(2, rounding='up').roll() == 2

    def test_div_rounding_down_rounds_fractions_down(self):
        assert self.constant(41).div(4, rounding='down').roll() == 10
        assert self.constant(-41).div(4, rounding='down').roll() == -11
        assert self.constant(5).div(2, rounding='down').notation == '5//2'

    def test_div_ndigits(self):
        assert self.constant(5).div(2, ndigits=1).roll() == 2.5
        assert self.constant(1).div(3, ndigits=2).roll() == 0.33
        assert self.constant(1).div(3, rounding='up', ndigits=2).roll() == 0.34

    def test_div_ndigits_none_skips_rounding(self):
        assert self.constant(1).div(3, ndigits=None).roll() == 1 / 3

    def test_div_bad_arguments(self):
        d6 = die.die.Standard(6)
        with pytest.raises(ValueError, match='rounding'):
            d6.div(2, rounding='sideways')
        with pytest.raises(ValueError, match='ndigits'):
            d6.div(2, rounding='up', ndigits=None)
        with pytest.raises(ValueError, match='ndigits'):
            d6.div(2, ndigits=-1)
        with pytest.raises(ValueError, match='ndigits'):
            d6.div(2, ndigits=1.5)
        with pytest.raises(ValueError, match='ndigits'):
            d6.div(2, ndigits='nope')

    def test_chain_binds_tight_left_to_right(self):
        d6 = die.die.Standard(6)
        r = d6.times(2).plus(3).div(d6)
        assert r.notation == '(d6*2+3)/d6'
        assert len(r.dice) == 4

    def test_notation_parenthesizes_loose_right_operand(self):
        d6 = die.die.Standard(6)
        assert d6.times(d6.plus(1)).notation == 'd6*(d6+1)'
        assert d6.minus(d6.plus(1)).notation == 'd6-d6-1'

    def test_minus_negated_die_normalizes_to_plus(self):
        r = die.rolls.Roll.from_notation('1-(-d6)')
        assert r.notation == '1+d6'
        assert [o.value for o in r.odds] == [2, 3, 4, 5, 6, 7]

    def test_notation_synthesized_from_unnamed_roll(self):
        d6 = die.die.Standard(6)
        r = die.rolls.Roll([d6, d6]).times(2)
        assert r.notation == '(2d6)*2'
        assert die.rolls.Roll().plus(d6).notation == 'd6'
        assert die.rolls.Roll().times(d6).notation == '0*d6'

    def test_compose_does_not_mutate_operands(self):
        d6 = die.die.Standard(6)
        base = die.rolls.Roll([d6], name='base')
        base.plus(d6)
        assert len(base.dice) == 1
        assert base.notation == 'd6'
        assert base.name == 'base'

    def test_compose_does_not_roll(self):
        r = die.die.Standard(6).times(2).plus(3)
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            r.value  # noqa: B018

    def test_bad_operand_raises(self):
        with pytest.raises(TypeError, match='cannot compose'):
            die.die.Standard(6).plus('nope')


class TestKeepDrop:
    def test_keep_highest_default(self):
        r = die.die.Standard(20).plus(die.die.Standard(20)).keep_highest()
        assert r.notation == '(2d20)kh'
        assert [o.value for o in r.odds] == list(range(1, 21))
        assert [o.ways for o in r.odds] == [2 * v - 1 for v in range(1, 21)]

    def test_keep_lowest(self):
        r = die.die.Standard(20).plus(die.die.Standard(20)).keep_lowest()
        assert r.notation == '(2d20)kl'
        assert [o.ways for o in r.odds] == [2 * (21 - v) - 1 for v in range(1, 21)]

    def test_drop_lowest_equals_wrapped_func(self):
        def sum_but_min(values):
            return sum(values) - min(values)

        expected = die.rolls.Roll([die.die.Standard(6)] * 4, func=sum_but_min)
        assert die.parse('4d6').drop_lowest().odds == expected.odds

    def test_drop_highest_equals_keep_lowest(self):
        assert die.parse('4d6').drop_highest().odds == die.parse('4d6').keep_lowest(3).odds

    def test_keep_all_is_identity(self):
        r = die.parse('4d6').keep_highest(4)
        assert r.notation == '4d6kh4'
        assert r.odds == die.parse('4d6').odds

    def test_deterministic_roll(self):
        rng = SequenceRng([1, 3, 4, 6])
        r = die.rolls.Roll([die.die.Standard(6, rng) for _ in range(4)]).drop_lowest()
        assert r.roll() == 13
        assert tuple(result[1] for result in r.results) == (1, 3, 4, 6)
        assert r.value == 13

    def test_die_delegation(self):
        d6 = die.die.Standard(6)
        assert d6.keep_lowest().notation == 'd6kl'
        with pytest.raises(ValueError, match='cannot drop'):
            d6.drop_highest()
        with pytest.raises(ValueError, match='cannot drop'):
            d6.drop_lowest()

    def test_notation_synthesis(self):
        assert die.die.Standard(6).keep_highest().notation == 'd6kh'
        assert die.parse('3d6+2d4').keep_highest(2).notation == '(3d6+2d4)kh2'
        d6 = die.die.Standard(6)
        assert die.rolls.Roll([d6, d6]).keep_highest().notation == '(2d6)kh'

    def test_n_out_of_range(self):
        with pytest.raises(ValueError, match='cannot keep'):
            die.die.Standard(6).keep_highest(2)
        with pytest.raises(ValueError, match='cannot drop'):
            die.parse('2d6').drop_lowest(2)
        with pytest.raises(ValueError, match='cannot keep'):
            die.rolls.Roll().keep_highest()

    def test_bad_n(self):
        r = die.parse('4d6')
        for n in (0, -1, 1.5, 'x', None):
            with pytest.raises(ValueError, match='positive integer'):
                r.keep_highest(n)

    def test_non_sum_func_raises(self):
        with pytest.raises(TypeError, match='summed'):
            die.die.Standard(6).times(2).keep_highest()
        with pytest.raises(TypeError, match='summed'):
            die.parse('4d6').keep_highest(3).keep_lowest()

    def test_non_numeric_raises(self):
        symbolic = die.die.Symbolic('w', (('a', 'x', 1), ('b', 'y', 1)))
        with pytest.raises(TypeError, match='non-numeric'):
            die.rolls.Roll([symbolic, symbolic]).keep_highest()

    def test_constant_in_pool(self):
        r = die.die.Standard(6).plus(3).keep_highest()
        assert [o.value for o in r.odds] == [3, 4, 5, 6]
        assert [o.ways for o in r.odds] == [3, 1, 1, 1]

    def test_does_not_mutate_or_roll(self):
        base = die.parse('4d6')
        r = base.drop_lowest()
        assert base.notation == '4d6'
        assert len(base.dice) == 4
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            r.value  # noqa: B018

    def test_negate(self):
        r = die.parse('4d6kh3')._negated()
        assert r.notation == '-4d6kh3'
        assert [o.value for o in r.odds] == [-o.value for o in reversed(die.parse('4d6kh3').odds)]

    def test_minus_keep_roll(self):
        r = die.rolls.Roll([die.die.Numeric('0', (0,))]).minus(die.parse('2d20kh'))
        assert [o.value for o in r.odds] == list(range(-20, 0))

    def test_plus_does_not_merge(self):
        r = die.parse('4d6kh3').plus(2)
        assert r.notation == '4d6kh3+2'
        assert r.odds[-1].value == 20


class TestSuccessFailureCounting:
    def test_successes_counts_at_or_above_target(self):
        r = die.parse('3d10', rng=SequenceRng([2, 7, 10])).successes(7)
        assert r.notation == '3d10>=7'
        assert r.roll() == 2

    def test_failures_counts_at_or_below_target(self):
        r = die.parse('3d10', rng=SequenceRng([1, 1, 5])).failures(1)
        assert r.notation == '3d10<=1'
        assert r.roll() == 2

    def test_constructed_roll_notation_parenthesized(self):
        r = die.rolls.Roll([die.die.Standard(10)] * 3).successes(7)
        assert r.notation == '(3d10)>=7'

    def test_odds(self):
        r = die.rolls.Roll([die.die.Standard(10), die.die.Standard(10)]).successes(7)
        assert [o.value for o in r.odds] == [0, 1, 2]
        assert [o.ways for o in r.odds] == [36, 48, 16]

    def test_composed_notation_parenthesized(self):
        r = die.parse('3d6+2d4').successes(5)
        assert r.notation == '(3d6+2d4)>=5'

    def test_results_still_report_every_die(self):
        rng = SequenceRng([2, 7])
        r = die.rolls.Roll([die.die.Standard(10, rng) for _ in range(2)]).successes(7)
        r.roll()
        assert r.results == (('2', 2), ('7', 7))
        assert r.value == 1

    def test_die_delegation(self):
        assert die.die.Standard(6).successes(4).notation == 'd6>=4'
        assert die.die.Standard(6).failures(3).notation == 'd6<=3'

    def test_does_not_mutate_or_roll(self):
        base = die.parse('6d10')
        r = base.successes(7)
        assert base.notation == '6d10'
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            r.value  # noqa: B018

    def test_non_numeric_raises(self):
        symbolic = die.die.Symbolic('S', (('a', 'a', 1),))
        with pytest.raises(TypeError, match='non-numeric'):
            die.rolls.Roll([symbolic, symbolic]).successes(1)

    def test_non_sum_roll_raises(self):
        with pytest.raises(TypeError, match='plain summed'):
            die.rolls.Roll([die.die.Standard(6)] * 2, func=max).successes(4)
        with pytest.raises(TypeError, match='plain summed'):
            die.parse('6d10').successes(7).failures(2)

    def test_bad_target_raises(self):
        with pytest.raises(TypeError, match='target'):
            die.parse('6d10').successes('nope')
        with pytest.raises(TypeError, match='target'):
            die.parse('6d10').failures(None)


class TestChance:
    def test_gte_cumulative_percentage(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        assert r.chance(gte=3) == pytest.approx(400 / 6)

    def test_lte_cumulative_percentage(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        assert r.chance(lte=2) == pytest.approx(200 / 6)

    def test_two_dice_gte(self):
        # 2d6 rolling 7+: 21 of 36 outcomes.
        assert die.parse('2d6').chance(gte=7) == pytest.approx(2100 / 36)

    def test_two_dice_lte(self):
        # 2d6 rolling 2 or lower: 1 of 36 outcomes.
        assert die.parse('2d6').chance(lte=2) == pytest.approx(100 / 36)

    def test_bounds_are_inclusive(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        assert r.chance(gte=6) == pytest.approx(100 / 6)
        assert r.chance(lte=1) == pytest.approx(100 / 6)

    def test_bound_past_range(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        assert r.chance(gte=0) == 100.0
        assert r.chance(lte=6) == 100.0
        assert r.chance(gte=7) == 0.0
        assert r.chance(lte=0) == 0.0

    def test_neither_bound_raises(self):
        with pytest.raises(ValueError, match='exactly one'):
            die.rolls.Roll([die.die.Standard(6)]).chance()

    def test_both_bounds_raises(self):
        with pytest.raises(ValueError, match='exactly one'):
            die.rolls.Roll([die.die.Standard(6)]).chance(gte=3, lte=4)

    def test_non_number_bound_raises(self):
        with pytest.raises(TypeError, match='bound'):
            die.rolls.Roll([die.die.Standard(6)]).chance(gte='nope')

    def test_non_numeric_roll_raises(self):
        symbolic = die.die.Symbolic('S', (('a', 'a', 1),))
        with pytest.raises(TypeError, match='non-numeric'):
            die.rolls.Roll([symbolic]).chance(gte=1)

    def test_empty_roll_is_zero(self):
        assert die.rolls.Roll().chance(gte=1) == 0.0

    def test_does_not_roll(self):
        r = die.rolls.Roll([die.die.Standard(6)])
        r.chance(gte=3)
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            r.value  # noqa: B018

    def test_die_delegation(self):
        assert die.die.Standard(6).chance(gte=3) == pytest.approx(400 / 6)
        assert die.die.Standard(6).chance(lte=2) == pytest.approx(200 / 6)
