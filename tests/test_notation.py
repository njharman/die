import random

import pytest

import die


class TestParse:
    def test_single_term(self):
        r = die.parse('3d6')
        assert r.name == '3d6'
        assert str(r) == '3d6'
        assert len(r.dice) == 3
        assert all(d.sides == 6 for d in r.dice)

    def test_implicit_count(self):
        r = die.parse('d20')
        assert r.name == 'd20'
        assert len(r.dice) == 1
        assert r.dice[0].sides == 20

    def test_constant_modifier(self):
        r = die.parse('2d10+5')
        assert r.name == '2d10+5'
        assert len(r.dice) == 3
        for _ in range(50):
            assert 7 <= r.roll() <= 25

    def test_negative_constant(self):
        r = die.parse('2d6-1')
        assert r.name == '2d6-1'
        for _ in range(50):
            assert 1 <= r.roll() <= 11

    def test_negative_dice_term(self):
        r = die.parse('d6-d4')
        assert r.name == 'd6-d4'
        for _ in range(50):
            assert -3 <= r.roll() <= 5

    def test_leading_negative(self):
        r = die.parse('-d6')
        assert r.name == '-d6'
        for _ in range(20):
            assert -6 <= r.roll() <= -1

    def test_fudge(self):
        r = die.parse('4dF')
        assert r.name == '4dF'
        assert len(r.dice) == 4
        assert r.dice[0].sides == 6
        assert sorted(set(r.dice[0].values)) == [-1, 0, 1]
        for _ in range(50):
            assert -4 <= r.roll() <= 4

    def test_negative_fudge(self):
        r = die.parse('-2df')
        assert r.name == '-2dF'
        assert sorted(set(r.dice[0].values)) == [-1, 0, 1]

    def test_multi_term(self):
        r = die.parse('3d6+2d4-1')
        assert r.name == '3d6+2d4-1'
        assert len(r.dice) == 6
        assert r.odds[0].value == 3 + 2 - 1

    def test_whitespace_tolerated(self):
        assert die.parse(' 3d6 + 2 ').name == '3d6+2'

    def test_case_insensitive(self):
        assert die.parse('3D6').name == '3d6'
        assert die.parse('2df').name == '2dF'

    def test_normalizes_terms(self):
        assert die.parse('1d06+05').name == 'd6+5'

    def test_rng_passed_to_dice(self):
        a = die.parse('3d6', rng=random.Random(11)).rolls(5)
        b = die.parse('3d6', rng=random.Random(11)).rolls(5)
        assert a == b

    def test_dice_follow_class_rng(self, monkeypatch):
        r = die.parse('3d6')
        monkeypatch.setattr(die.Die, 'rng', random.Random(11))
        a = r.rolls(5)
        monkeypatch.setattr(die.Die, 'rng', random.Random(11))
        b = r.rolls(5)
        assert a == b

    def test_bad_notation(self):
        bad = ('', '   ', 'foo', '3d', 'd', '3d6 4d4', '0d6', 'd0', '3d6+', '+', '3d6&2', None, 3)
        for notation in bad:
            with pytest.raises(ValueError, match='Bad dice notation'):
                die.parse(notation)


class TestRoll:
    def test_rolls_notation(self):
        for _ in range(20):
            assert 5 <= die.roll('3d6+2') <= 20

    def test_rng(self):
        a = die.roll('3d6', rng=random.Random(11))
        b = die.parse('3d6', rng=random.Random(11)).roll()
        assert a == b

    def test_bad_notation(self):
        with pytest.raises(ValueError, match='Bad dice notation'):
            die.roll('foo')
