import random

import pytest

import die


class SequenceRng:
    """Deterministic rng: choice returns the face matching the next value in a fixed sequence."""

    def __init__(self, values):
        self.values = list(values)

    def choice(self, seq):
        value = self.values.pop(0)
        for face in seq:
            if face[1] == value:
                return face
        raise ValueError(f'{value} not in {seq}')


class TestParse:
    def test_single_term(self):
        r = die.parse('3d6')
        assert r.notation == '3d6'
        assert len(r.dice) == 3
        assert all(d.sides == 6 for d in r.dice)

    def test_implicit_count(self):
        r = die.parse('d20')
        assert r.notation == 'd20'
        assert len(r.dice) == 1
        assert r.dice[0].sides == 20

    def test_constant_modifier(self):
        r = die.parse('2d10+5')
        assert r.notation == '2d10+5'
        assert len(r.dice) == 3
        assert isinstance(r.dice[2], die.Constant)
        assert die.parse('2d10+5', rng=SequenceRng([1, 1])).roll() == 7
        assert die.parse('2d10+5', rng=SequenceRng([10, 10])).roll() == 25

    def test_negative_constant(self):
        r = die.parse('2d6-1')
        assert r.notation == '2d6-1'
        assert die.parse('2d6-1', rng=SequenceRng([1, 1])).roll() == 1
        assert die.parse('2d6-1', rng=SequenceRng([6, 6])).roll() == 11

    def test_negative_dice_term(self):
        r = die.parse('d6-d4')
        assert r.notation == 'd6-d4'
        assert die.parse('d6-d4', rng=SequenceRng([1, -4])).roll() == -3
        assert die.parse('d6-d4', rng=SequenceRng([6, -1])).roll() == 5

    def test_leading_negative(self):
        r = die.parse('-d6')
        assert r.notation == '-d6'
        assert die.parse('-d6', rng=SequenceRng([-1])).roll() == -1
        assert die.parse('-d6', rng=SequenceRng([-6])).roll() == -6

    def test_fudge(self):
        r = die.parse('4dF')
        assert r.notation == '4dF'
        assert len(r.dice) == 4
        assert r.dice[0].sides == 6
        assert sorted(set(r.dice[0].values)) == [-1, 0, 1]
        assert die.parse('4dF', rng=SequenceRng([1, 1, 1, 1])).roll() == 4
        assert die.parse('4dF', rng=SequenceRng([-1, -1, -1, -1])).roll() == -4

    def test_negative_fudge(self):
        r = die.parse('-2df')
        assert r.notation == '-2dF'
        assert sorted(set(r.dice[0].values)) == [-1, 0, 1]

    def test_multi_term(self):
        r = die.parse('3d6+2d4-1')
        assert r.notation == '3d6+2d4-1'
        assert len(r.dice) == 6
        assert r.odds[0].value == 3 + 2 - 1

    def test_whitespace_tolerated(self):
        assert die.parse(' 3d6 + 2 ').notation == '3d6+2'

    def test_case_insensitive(self):
        assert die.parse('3D6').notation == '3d6'
        assert die.parse('2df').notation == '2dF'

    def test_normalizes_terms(self):
        assert die.parse('1d06+05').notation == 'd6+5'

    def test_rng_passed_to_dice(self):
        a = die.parse('3d6', rng=random.Random(11)).roll(5, func=list)
        b = die.parse('3d6', rng=random.Random(11)).roll(5, func=list)
        assert a == b

    def test_dice_follow_class_rng(self, monkeypatch):
        r = die.parse('3d6')
        monkeypatch.setattr(die.Die, 'rng', random.Random(11))
        a = r.roll(5, func=list)
        monkeypatch.setattr(die.Die, 'rng', random.Random(11))
        b = r.roll(5, func=list)
        assert a == b

    def test_keep_drop_suffix(self):
        r = die.parse('4d6dl')
        assert r.notation == '4d6dl'
        assert len(r.dice) == 4
        assert r.odds[0].value == 3
        assert r.odds[-1].value == 18
        r = die.parse('2d20kh')
        assert [o.ways for o in r.odds] == [2 * v - 1 for v in range(1, 21)]
        assert die.parse('5d10dh2').notation == '5d10dh2'

    def test_keep_drop_case_insensitive(self):
        assert die.parse('4D6DL').notation == '4d6dl'
        assert die.parse('4d6Kh3').notation == '4d6kh3'
        assert die.parse('2d20kH').notation == '2d20kh'

    def test_keep_drop_normalizes(self):
        assert die.parse('4d6kh1').notation == '4d6kh'
        assert die.parse('4d6kh01').notation == '4d6kh'
        assert die.parse('(3d6)kh2').notation == '3d6kh2'

    def test_keep_drop_group(self):
        r = die.parse('(3d6+2d4)kh2')
        assert r.notation == '(3d6+2d4)kh2'
        assert len(r.dice) == 5

    def test_keep_binds_tighter_than_unary_minus(self):
        r = die.parse('-2d20kh')
        assert r.notation == '-2d20kh'
        assert all(-20 <= o.value <= -1 for o in r.odds)

    def test_keep_drop_equals_method_chain(self):
        parsed = die.parse('4d6kh3')
        chained = die.parse('4d6').keep_highest(3)
        assert parsed.notation == chained.notation
        assert parsed.odds == chained.odds

    def test_fudge_keep(self):
        assert die.parse('4dFkh2').notation == '4dFkh2'

    def test_exploding_suffix(self):
        r = die.parse('d6x')
        assert r.notation == 'd6x'
        assert len(r.dice) == 1
        assert isinstance(r.dice[0], die.Exploding)

    def test_penetrating_suffix(self):
        r = die.parse('d6p')
        assert r.notation == 'd6p'
        assert len(r.dice) == 1
        assert isinstance(r.dice[0], die.Exploding)

    def test_exploding_count_prefix(self):
        r = die.parse('3d6x')
        assert r.notation == '3d6x'
        assert len(r.dice) == 3
        assert all(isinstance(d, die.Exploding) for d in r.dice)

    def test_penetrating_count_prefix(self):
        r = die.parse('3d6p')
        assert r.notation == '3d6p'
        assert len(r.dice) == 3
        assert all(isinstance(d, die.Exploding) for d in r.dice)

    def test_exploding_penetrating_case_insensitive(self):
        assert die.parse('D6X').notation == 'd6x'
        assert die.parse('4D6P').notation == '4d6p'

    def test_exploding_combines_with_keep_drop(self):
        r = die.parse('4d6xkh3')
        assert r.notation == '4d6xkh3'
        assert len(r.dice) == 4
        assert all(isinstance(d, die.Exploding) for d in r.dice)

    def test_exploding_rolls(self):
        r = die.parse('d6x', rng=SequenceRng([6, 3]))
        assert r.roll() == 9

    def test_penetrating_rolls(self):
        r = die.parse('d6p', rng=SequenceRng([6, 3]))
        assert r.roll() == 8

    def test_reroll_suffix(self):
        r = die.parse('d6r')
        assert r.notation == 'd6r'
        assert isinstance(r.dice[0], die.Rerolling)

    def test_reroll_range(self):
        assert die.parse('d6r2').notation == 'd6r2'
        assert die.parse('d6r1').notation == 'd6r'
        assert die.parse('d10rr2').notation == 'd10rr2'

    def test_reroll_count_prefix(self):
        r = die.parse('4d6r')
        assert r.notation == '4d6r'
        assert all(isinstance(d, die.Rerolling) for d in r.dice)

    def test_reroll_case_insensitive(self):
        assert die.parse('D6R').notation == 'd6r'
        assert die.parse('d6RR2').notation == 'd6rr2'

    def test_reroll_combines_with_keep_drop(self):
        assert die.parse('4d6rkh3').notation == '4d6rkh3'

    def test_reroll_rolls(self):
        r = die.parse('d6r', rng=SequenceRng([1, 5]))
        assert r.roll() == 5

    def test_reroll_recursive_rolls(self):
        r = die.parse('d6rr2', rng=SequenceRng([1, 2, 3]))
        assert r.roll() == 3

    def test_successes_suffix(self):
        r = die.parse('6d10>=7', rng=SequenceRng([2, 7, 10, 6, 8, 1]))
        assert r.notation == '6d10>=7'
        assert r.roll() == 3

    def test_failures_suffix(self):
        r = die.parse('6d10<=1', rng=SequenceRng([2, 1, 10, 1, 8, 1]))
        assert r.notation == '6d10<=1'
        assert r.roll() == 3

    def test_counting_group(self):
        assert die.parse('(3d6+2d4)>=5').notation == '(3d6+2d4)>=5'

    def test_counting_equals_method_chain(self):
        assert die.parse('6d10>=7').odds == die.parse('6d10').successes(7).odds

    def test_counting_combines_with_reroll(self):
        assert die.parse('6d10r>=7').notation == '6d10r>=7'

    def test_bad_notation(self):
        bad = ('', '   ', 'foo', '3d', 'd', '3d6 4d4', '0d6', 'd0', '3d6+', '+', '3d6&2', None, 3)
        bad += ('(d6', 'd6)', '()', 'd6*', 'd6//', '(d6+)2', '(d6 d6)')
        bad += ('4d6dl4', '4d6kh0', 'd6kh2', 'kh2', 'kh', '4d6dlkh', '4d6khkh2')
        bad += ('dFx', 'dFp', 'd1x', 'd1p', 'd6xx', 'd6x2', 'xd6', 'pd6')
        bad += ('dFr', 'dFrr', 'd6r0', 'd6r6', 'd1r', 'rd6', 'd6rrr')
        bad += ('6d10>=', '>=7', '6d10>=d6', '6d10>7', '6d10<1', '6d10>=7>=2', '6d10=7')
        for notation in bad:
            with pytest.raises(ValueError, match='Bad dice notation'):
                die.parse(notation)


class TestExpressions:
    def test_standard_precedence(self):
        r = die.parse('d6+3*2')
        assert r.notation == 'd6+3*2'
        assert [o.value for o in r.odds] == [7, 8, 9, 10, 11, 12]

    def test_parens_override_precedence(self):
        r = die.parse('(d6+3)*2')
        assert r.notation == '(d6+3)*2'
        assert [o.value for o in r.odds] == [8, 10, 12, 14, 16, 18]

    def test_division_rounds_half_up(self):
        r = die.parse('d6/2')
        assert r.notation == 'd6/2'
        assert r.odds == [(1, 2, 1 / 3), (2, 2, 1 / 3), (3, 2, 1 / 3)]

    def test_floor_division(self):
        r = die.parse('d6//2')
        assert r.notation == 'd6//2'
        assert [o.value for o in r.odds] == [0, 1, 2, 3]

    def test_modulo(self):
        r = die.parse('d6%3')
        assert r.notation == 'd6%3'
        assert [o.value for o in r.odds] == [0, 1, 2]

    def test_complex_expression(self):
        # Constants are one-faced dice, so (d6*2+3)/d6 carries dice [d6, 2, 3, d6].
        r = die.parse('(d6*2+3)/d6')
        assert r.notation == '(d6*2+3)/d6'
        assert len(r.dice) == 4
        for _ in range(20):
            assert 1 <= r.roll() <= 15

    def test_parse_equals_method_chain(self):
        parsed = die.parse('(d6*2+3)/d6')
        chained = die.d6.times(2).plus(3).div(die.d6)
        assert parsed.notation == chained.notation
        assert parsed.odds == chained.odds

    def test_negated_paren_expression(self):
        r = die.parse('-(d6+1)')
        assert r.notation == '-(d6+1)'
        assert [o.value for o in r.odds] == [-7, -6, -5, -4, -3, -2]

    def test_negated_non_sum_expression(self):
        r = die.parse('-(d6*2)')
        assert r.notation == '-(d6*2)'
        assert [o.value for o in r.odds] == [-12, -10, -8, -6, -4, -2]

    def test_negative_constant_operand(self):
        r = die.parse('d6*-2')
        assert r.notation == 'd6*-2'
        assert [o.value for o in r.odds] == [-12, -10, -8, -6, -4, -2]

    def test_notation_round_trips(self):
        texts = ('3d6+2', '(d6*2+3)/d6', 'd6+3*2', 'd6//2', '-(d6+1)', 'd6-(d4+1)')
        texts += ('4d6dl', '2d20kh', '(3d6+2d4)kh2', '-2d20kh', '4d6kh3*2', '4dFkh2')
        texts += ('d6x', '3d6p', '4d6xkh3')
        for text in texts:
            r = die.parse(text)
            assert die.parse(r.notation).notation == r.notation


class TestRoll:
    def test_rolls_notation(self):
        assert die.roll('3d6+2', rng=SequenceRng([1, 1, 1])) == 5
        assert die.roll('3d6+2', rng=SequenceRng([6, 6, 6])) == 20

    def test_rng(self):
        a = die.roll('3d6', rng=random.Random(11))
        b = die.parse('3d6', rng=random.Random(11)).roll()
        assert a == b

    def test_bad_notation(self):
        with pytest.raises(ValueError, match='Bad dice notation'):
            die.roll('foo')
