import numbers
import operator
import random

import pytest
from helpers import SequenceRng, StubRng

import die.die


class StubDie(die.die.Die):
    """Fake ``explode_to`` die whose roll() always returns a forced value, isolating
    math_correct."""

    def __init__(self, value):
        super().__init__('stub', (('x', value),))

    def roll(self):
        return self._faces[0][1]


class TestDie:
    """Direct tests of the base Die class (not routed through a subclass)."""

    faces = (('+', 1), ('', 0), ('-', -1))

    def test_init_bad_faces(self):
        with pytest.raises(ValueError, match='Invalid faces'):
            die.die.Die('name', [])

    def test_init_bad_notation(self):
        for notation in (None, '', ' ', '  '):
            with pytest.raises(ValueError, match='Invalid notation'):
                die.die.Die(notation, self.faces)

    def test_init_notation_coerced_to_str(self):
        assert die.die.Die(34, self.faces).notation == '34'
        assert die.die.Die(' bob ', self.faces).notation == 'bob'

    def test_init_good(self):
        t = die.die.Die('name', self.faces)
        assert t.notation == 'name'
        assert t.faces == ['+', '', '-']
        assert t.values == [1, 0, -1]
        assert t.items == [('+', 1), ('', 0), ('-', -1)]
        assert t.sides == 3

    def test_init_copies_faces(self):
        faces = [('a', 1), ('b', 2)]
        t = die.die.Die('name', faces)
        faces.append(('c', 3))
        assert t.sides == 2
        assert t.faces == ['a', 'b']

    def test_read_only_properties(self):
        t = die.die.Die('name', self.faces)
        for attr in (
            'notation',
            'description',
            'faces',
            'items',
            'values',
            'sides',
            'result',
            'face',
            'value',
        ):
            with pytest.raises(AttributeError):
                setattr(t, attr, 'nope')

    def test_result_face_value_raise_before_roll(self):
        t = die.die.Die('name', self.faces)
        with pytest.raises(RuntimeError, match='roll\\(\\) has not been called'):
            t.result  # noqa: B018
        with pytest.raises(RuntimeError, match='roll\\(\\) has not been called'):
            t.face  # noqa: B018
        with pytest.raises(RuntimeError, match='roll\\(\\) has not been called'):
            t.value  # noqa: B018

    def test_result_face_value_after_roll(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        t.roll()
        assert t.result == ('+', 1)
        assert t.face == '+'
        assert t.value == 1

    def test_result_face_value_after_rolls(self):
        t = die.die.Die('name', self.faces, rng=StubRng(2))
        t.roll(3, func=list)
        assert t.result == ('-', -1)

    def test_subscript_yields_values_in_order(self):
        t = die.die.Die('name', self.faces, rng=SequenceRng([1, 0, -1]))
        t.roll(3, func=list)
        assert t[0] == 1
        assert t[1] == 0
        assert t[2] == -1
        assert t[-1] == t.value

    def test_subscript_accumulates_across_calls(self):
        t = die.die.Die('name', self.faces, rng=SequenceRng([1, 0, -1, 1, 0]))
        t.roll(3, func=list)
        t.roll(2, func=list)
        assert t[:] == [1, 0, -1, 1, 0]
        assert t[-1] == t.value

    def test_subscript_slice_and_iter_do_not_roll(self):
        rng = SequenceRng([1, 0, -1])
        t = die.die.Die('name', self.faces, rng=rng)
        t.roll(2, func=list)
        assert t[0:2] == [1, 0]
        assert list(t) == [1, 0]
        assert rng.values == [-1]  # slicing/iterating consumed no rolls

    def test_history_records_results_in_order(self):
        t = die.die.Die('name', self.faces, rng=SequenceRng([1, 0, -1]))
        assert t.history == []
        t.roll(3, func=list)
        assert t.history == [('+', 1), ('', 0), ('-', -1)]
        assert t.history[-1] == t.result

    def test_history_is_a_copy(self):
        t = die.die.Die('name', self.faces, rng=SequenceRng([1]))
        t.roll()
        t.history.clear()
        assert len(t) == 1
        with pytest.raises(AttributeError):
            t.history = []

    def test_subscript_before_roll_raises_indexerror(self):
        t = die.die.Die('name', self.faces)
        with pytest.raises(IndexError):
            t[0]
        assert t[:] == []

    def test_len_counts_history_without_rolling(self):
        rng = SequenceRng([1, 0, -1])
        t = die.die.Die('name', self.faces, rng=rng)
        assert len(t) == 0
        t.roll(3, func=list)
        assert len(t) == 3
        assert rng.values == []  # len consumed no rolls

    def test_clear_empties_history(self):
        t = die.die.Die('name', self.faces, rng=SequenceRng([1, 0]))
        t.roll(2, func=list)
        t.clear()
        assert len(t) == 0
        with pytest.raises(RuntimeError, match=r'roll\(\) has not been called'):
            t.result  # noqa: B018

    def test_name_attribute(self):
        t = die.die.Die('d6ish', self.faces)
        assert t.name == ''
        t.name = 'lucky'
        assert t.name == 'lucky'
        assert 'lucky' in repr(t)

    def test_str_rolls(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        assert str(t) == '1'

    def test_repr(self):
        t = die.die.Die('name', self.faces)
        r = repr(t)
        assert r.startswith('<Die(')
        assert 'name' in r
        assert str(self.faces) in r

    def test_unhashable(self):
        t = die.die.Die('name', self.faces)
        with pytest.raises(TypeError):
            hash(t)
        with pytest.raises(TypeError):
            {t}  # noqa: B018

    def test_index(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        seq = list(range(10))
        assert operator.index(t) == 1
        assert seq[t] == 1

    def test_roll_count_func_list_returns_individual_results(self):
        t = die.die.Die('name', self.faces)
        result = t.roll(3, func=list)
        assert len(result) == 3
        assert all(v in t.values for v in result)

    def test_equality_rolls(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        assert (t == 1) is True
        assert (t != 1) is False
        assert (t == 0) is False
        assert (t != 0) is True

    def test_structural_equality_via_items(self):
        # ==/!= roll; identical faces are compared structurally via items.
        spec = (('a', 1, 1), ('b', 2, 1))
        w = die.die.Symbolic('w', spec)
        n = die.die.NumericBased('n', spec)
        assert w.items == n.items

    def test_default_rng_is_random_module(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'choice', lambda seq: seq[1])
        t = die.die.Die('name', self.faces)
        assert t.roll() == 0

    def test_seeded_rng_reproducible(self):
        a = die.die.Die('name', self.faces, rng=random.Random(7)).roll(10, func=list)
        b = die.die.Die('name', self.faces, rng=random.Random(7)).roll(10, func=list)
        assert a == b

    def test_class_rng_affects_existing_die(self, monkeypatch):
        t = die.die.Die('name', self.faces)
        monkeypatch.setattr(die.die.Die, 'rng', StubRng(2))
        assert t.roll() == -1
        assert t.roll(3, func=list) == [-1, -1, -1]

    def test_class_rng_affects_subclasses(self, monkeypatch):
        monkeypatch.setattr(die.die.Die, 'rng', StubRng(2))
        assert die.die.Standard(6).roll() == 3
        w = die.die.Symbolic('w', (('a', 'x', 1), ('b', 'y', 1), ('c', 'z', 1)))
        assert w.roll(func=lambda values: values[0]) == 'z'

    def test_instance_rng_overrides_class_rng(self, monkeypatch):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        monkeypatch.setattr(die.die.Die, 'rng', StubRng(2))
        assert t.roll() == 1

    def test_deterministic_roll(self):
        t = die.die.Die('name', self.faces, rng=StubRng(1))
        assert t.roll() == 0
        assert t.roll(3, func=list) == [0, 0, 0]

    def test_deterministic_coercion(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        assert t() == 1
        assert int(t) == 1
        assert float(t) == 1.0

    def test_deterministic_operators(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        assert t + 1 == 2
        assert 1 + t == 2
        assert t - 1 == 0
        assert 3 - t == 2
        assert t * 3 == 3
        assert 3 * t == 3
        assert t / 2 == 0.5
        assert 2 / t == 2
        assert t // 2 == 0
        assert 4 // t == 4
        assert t % 2 == 1
        assert 3 % t == 0
        assert t**3 == 1
        assert 3**t == 3

    def test_deterministic_comparisons(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        assert (t > 0) is True
        assert (t >= 1) is True
        assert (t < 0) is False
        assert (t <= 1) is True

    def test_roll_count_sums_by_default(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        assert t.roll(3) == 3
        assert t(3) == 3

    def test_roll_count_applies_func(self):
        t = die.die.Die('name', self.faces, rng=StubRng(0))
        assert t.roll(3, func=list) == [1, 1, 1]

    def test_symbolic_default_func_is_count_aware(self):
        t = die.die.Symbolic('coin', (('H', 'heads', 1),))
        assert t.roll() == 'heads'
        assert t() == 'heads'
        assert t.roll(3) == ['heads', 'heads', 'heads']


# This class is reused for other test cases below
class TestNumericBased:
    die_class = die.die.NumericBased
    get_face = lambda self, face: face[0]
    get_value = lambda self, face: face[1]
    get_count = lambda self, face: face[2]
    good_notations = ('dTest', 34, ' bob ')
    good_notation = good_notations[0]
    bad_notations = ('', ' ', '  ', None)
    bad_spec = (None, 1, (), ('+', 3), ('', 1, 0), ('', 0, -2), ('', 't', 1))
    good_spec = (('+', 1, 2), ('-', -1.45, 2), ('', 3, 1), (' ', 4, 1))
    expected_faces = ('+', '+', '-', '-', '', ' ')
    expected_values = (1, 1, -1.45, -1.45, 3, 4)

    def test_init(self):
        for notation in self.good_notations:
            self.die_class(notation, self.good_spec)
        for notation in self.bad_notations:
            with pytest.raises(ValueError, match='Invalid notation'):
                self.die_class(notation, self.good_spec)
        for i in range(len(self.bad_spec)):
            faces = [
                self.bad_spec[i],
            ]
            faces.extend(self.good_spec)
            with pytest.raises(ValueError, match='Bad die specification'):
                self.die_class(self.good_notation, faces)

    def test_init_bad_spec_not_iterable(self):
        with pytest.raises(ValueError, match='Bad die specification'):
            self.die_class(self.good_notation, 123)

    def test_init_empty_spec(self):
        with pytest.raises(ValueError, match='Invalid faces'):
            self.die_class(self.good_notation, ())

    def test_minimal(self):
        t = self.die_class(self.good_notation, self.good_spec)
        t.roll(func=lambda values: values[0])
        str(t)
        repr(t)
        assert len(t.roll(3, func=list)) == 3

    def test_coercion(self):
        t = self.die_class(self.good_notation, self.good_spec)
        t(func=lambda values: values[0])
        if t.numeric:
            int(t)
            float(t)

    def test_operators(self):
        t = self.die_class(self.good_notation, self.good_spec)
        if t.numeric:
            t + 1
            1 + t
            1 - t
            t - 1
            t * 1
            1 * t
            t / 1
            1 / t
            t // 1
            1 // t
            t % 1
            1 % t
            t**1
            1**t

    def test_comparisons(self):
        t = self.die_class(self.good_notation, self.good_spec)
        if t.numeric:
            assert isinstance(t > 1, bool)
            assert isinstance(t >= 1, bool)
            assert isinstance(t < 1, bool)
            assert isinstance(t <= 1, bool)

    def test_deterministic_roll(self):
        t = self.die_class(self.good_notation, self.good_spec, rng=StubRng(0))
        expected_face = self.expected_faces[0]
        expected_value = self.expected_values[0]
        assert t.roll() == expected_value
        assert t.result == (expected_face, expected_value)
        if t.numeric:
            assert t() == expected_value
            assert t + 1 == expected_value + 1
            assert 1 + t == expected_value + 1
            assert (t > expected_value - 1) is True
            assert (t <= expected_value) is True

    def test_equality_rolls(self):
        # Index 0 face value is numeric for every subclass, so sum-of-one works even on Symbolic.
        t = self.die_class(self.good_notation, self.good_spec, rng=StubRng(0))
        expected = self.expected_values[0]
        assert (t == expected) is True
        assert (t != expected) is False

    def test_structural_equality(self):
        t1 = self.die_class(self.good_notation, self.good_spec)
        t2 = self.die_class(self.good_notation, self.good_spec)
        t3 = die.die.Standard(6)
        assert t1.items == t2.items
        assert t1.items != t3.items

    def test_properties(self):
        for i in range(40):
            sides = 0
            spec = list()
            expected_faces = list()
            expected_values = list()
            spec_idx = i % len(self.good_spec)
            for _ in range(i % 8):
                face = self.good_spec[spec_idx]
                spec.append(face)
                for _ in range(self.get_count(face)):
                    sides += 1
                    expected_faces.append(str(self.get_face(face)))
                    expected_values.append(self.get_value(face))
            if not spec:
                continue
            t = self.die_class(self.good_notation, spec)
            assert isinstance(t.description, str)
            assert t.description
            assert t.notation == self.good_notation
            assert t.numeric == all(isinstance(v, numbers.Number) for v in expected_values)
            assert t.sides == sides
            assert t.faces == expected_faces
            assert t.values == expected_values


class TestConstant:
    def test_init(self):
        t = die.die.Constant(2)
        assert t.notation == '2'
        assert t.description == 'Constant 2.'
        assert t.sides == 1
        assert t.items == [('2', 2)]
        assert t.numeric

    def test_init_bad_value(self):
        for value in ('x', None, [1], (2,)):
            with pytest.raises(ValueError, match='Bad die specification'):
                die.die.Constant(value)

    def test_roll_always_value(self):
        t = die.die.Constant(3)
        assert t.roll() == 3
        assert t.roll(4) == 12
        assert t.result == ('3', 3)
        assert t.face == '3'
        assert t.value == 3

    def test_history(self):
        t = die.die.Constant(3)
        t.roll(2)
        assert list(t) == [3, 3]
        assert t.history == [('3', 3), ('3', 3)]

    def test_no_randomness_consumed(self):
        rng = random.Random(42)
        expected = random.Random(42).random()
        t = die.die.Constant(5, rng)
        t.roll(10)
        assert rng.random() == expected

    def test_negative_value(self):
        t = die.die.Constant(-2)
        assert t.notation == '-2'
        assert t.roll() == -2

    def test_negated_stays_constant(self):
        t = die.die.Constant(2)._negated()
        assert isinstance(t, die.die.Constant)
        assert t.notation == '-2'
        assert t.roll() == -2


class TestStandardDie:
    good = (1, 5, 80, 99, 2000)
    bad = (0, -1, 'what', None, '6', 6.9)

    def test_init(self):
        for i in self.bad:
            with pytest.raises(ValueError, match='Bad number of sides'):
                die.die.Standard(i)

    def test_init_integral_sides(self):
        assert die.die.Standard(6.0).sides == 6
        assert die.die.Standard(True).sides == 1

    def test_minimal(self):
        t = die.die.Standard(6)
        t.roll()
        assert len(t.roll(2, func=list)) == 2

    def test_properties(self):
        for i in self.good:
            t = die.die.Standard(i)
            assert t.description == f'Numeric die with {i} faces numbered 1 through {i}.'
            assert len(t.faces) == i
            assert len(t.values) == i
            assert t.sides == i
            assert t.numeric

    def test_coercion(self):
        t = die.die.Standard(6)
        t()
        int(t)
        float(t)

    def test_operators(self):
        t = die.die.Standard(6)
        t + 1
        1 + t
        1 - t
        t - 1
        t * 1
        1 * t
        t / 1
        1 / t
        t // 1
        1 // t
        t % 1
        1 % t
        t**1
        1**t

    def test_comparisons(self):
        t = die.die.Standard(6)
        assert isinstance(t > 1, bool)
        assert isinstance(t >= 1, bool)
        assert isinstance(t < 1, bool)
        assert isinstance(t <= 1, bool)

    def test_equality_rolls(self):
        t = die.die.Standard(6, rng=StubRng(2))
        assert (t == 3) is True
        assert (t != 3) is False
        assert (t == 6) is False

    def test_structural_equality(self):
        assert die.die.Standard(6).items == die.die.Standard(6).items
        assert die.die.Standard(6).items != die.die.Standard(8).items

    def test_deterministic_roll(self):
        t = die.die.Standard(6, rng=StubRng(2))
        assert t.roll() == 3
        assert t + 1 == 4
        assert (t > 2) is True
        assert (t <= 3) is True


class TestExploding:
    def test_init_bad_sides(self):
        with pytest.raises(ValueError, match='Bad number of sides'):
            die.die.Exploding(0)

    def test_init_bad_explode_to(self):
        for explode_to in (6, 'nope', 2.5):
            with pytest.raises(ValueError, match='explode_to must be a Die instance'):
                die.die.Exploding(6, explode_to=explode_to)

    def test_init_bad_explode_range_vs_sides(self):
        with pytest.raises(ValueError, match='explode_range must be < sides'):
            die.die.Exploding(6, explode_range=6)

    def test_init_bad_explode_range_low_negative(self):
        with pytest.raises(ValueError, match='explode_range_low must be >= 0'):
            die.die.Exploding(6, explode_range_low=-1)

    def test_init_bad_combined_explode_range_overlap(self):
        with pytest.raises(
            ValueError,
            match='explode_range and explode_range_low combined must be < sides',
        ):
            die.die.Exploding(6, explode_range=3, explode_range_low=3)

    def test_init_bad_math_correct_with_low_explosion(self):
        with pytest.raises(ValueError, match='math_correct is not supported with low-end'):
            die.die.Exploding(6, explode_range_low=1, math_correct=True)

    def test_init_bad_explode_to_low(self):
        for explode_to_low in (6, 'nope', 2.5):
            with pytest.raises(ValueError, match='explode_to_low must be a Die instance'):
                die.die.Exploding(6, explode_to_low=explode_to_low)

    def test_init_good_defaults_explode_to_to_self(self):
        t = die.die.Exploding(6)
        assert t.sides == 6
        assert t.notation == 'd6x'
        assert t.notation in t.description

    def test_init_good_explicit_explode_to(self):
        t = die.die.Exploding(20, explode_to=die.die.Standard(6), math_correct=True)
        assert t.sides == 20
        assert t.notation == 'd20p'
        assert 'math corrected' in t.description
        assert 'd6' in t.description

    def test_is_a_standard_die(self):
        t = die.die.Exploding(6)
        assert isinstance(t, die.die.Standard)
        assert t.faces == [str(x) for x in range(1, 7)]
        assert t.values == list(range(1, 7))
        assert t.numeric
        assert t.items == die.die.Standard(6).items

    def test_roll_no_explosion(self):
        t = die.die.Exploding(6, rng=SequenceRng([3]))
        assert t.roll() == 3

    def test_roll_explodes_once(self):
        t = die.die.Exploding(6, rng=SequenceRng([6, 3]))
        assert t.roll() == 9

    def test_result_reflects_initial_face_and_final_value_on_explosion(self):
        t = die.die.Exploding(6, rng=SequenceRng([6, 3]))
        t.roll()
        assert t.face == '6'
        assert t.value == 9
        assert t.result == ('6', 9)

    def test_result_matches_value_when_no_explosion(self):
        t = die.die.Exploding(6, rng=SequenceRng([3]))
        t.roll()
        assert t.result == ('3', 3)

    def test_history_records_one_settled_entry_per_roll(self):
        # First roll explodes (6 then 3 -> 9); second does not (2). The intermediate
        # explosion sub-roll must NOT leak into history.
        t = die.die.Exploding(6, rng=SequenceRng([6, 3, 2]))
        t.roll(2, func=list)
        assert t[:] == [9, 2]
        assert t.history == [('6', 9), ('2', 2)]
        assert t.history[-1] == t.result

    def test_roll_explodes_repeatedly(self):
        t = die.die.Exploding(6, rng=SequenceRng([6, 6, 2]))
        assert t.roll() == 14

    def test_roll_math_correct_subtracts_one_from_explode_to_roll(self):
        # Forced explode_to.roll() == 5, initial roll forced to 6 (explodes): 6 + (5 - 1) == 10.
        stub = StubDie(5)
        t = die.die.Exploding(6, explode_to=stub, math_correct=True, rng=SequenceRng([6]))
        assert t.roll() == 10

    def test_roll_without_math_correct_keeps_full_explode_to_roll(self):
        # Same forced rolls, math_correct=False: 6 + 5 == 11, no subtraction.
        stub = StubDie(5)
        t = die.die.Exploding(6, explode_to=stub, math_correct=False, rng=SequenceRng([6]))
        assert t.roll() == 11

    def test_roll_math_correct_only_applies_on_explosion(self):
        # No explosion (roll is 3, not max): forced explode_to is never consulted.
        stub = StubDie(5)
        t = die.die.Exploding(6, explode_to=stub, math_correct=True, rng=SequenceRng([3]))
        assert t.roll() == 3

    def test_roll_math_correct_matches_hackmaster_rule(self):
        # Matches Hackmaster rule: d8p rolling (8, 1) totals 8, not 9.
        t = die.die.Exploding(8, math_correct=True, rng=SequenceRng([8, 1]))
        assert t.roll() == 8

    def test_roll_explodes_down_to_explode_to(self):
        sub = die.die.Exploding(6, math_correct=True, rng=SequenceRng([6, 3]))
        t = die.die.Exploding(20, explode_to=sub, math_correct=True, rng=SequenceRng([20]))
        assert t.roll() == 27


class TestRerolling:
    def test_init_bad_sides(self):
        with pytest.raises(ValueError, match='Bad number of sides'):
            die.die.Rerolling(0)

    def test_init_bad_reroll_range(self):
        for reroll_range in (0, 6, 7, -1, 2.5, 'nope', None):
            with pytest.raises(ValueError, match='reroll_range'):
                die.die.Rerolling(6, reroll_range)

    def test_init_good_notation(self):
        assert die.die.Rerolling(6).notation == 'd6r'
        assert die.die.Rerolling(6, 2).notation == 'd6r2'
        assert die.die.Rerolling(6, once=False).notation == 'd6rr'
        assert die.die.Rerolling(10, 2, once=False).notation == 'd10rr2'

    def test_init_good_description(self):
        assert die.die.Rerolling(6, 2).description == (
            'Rerolling numeric die, 6 faces numbered 1 through 6, rerolls at or below 2 once.'
        )
        assert die.die.Rerolling(6, once=False).description == (
            'Rerolling numeric die, 6 faces numbered 1 through 6, '
            'rerolls at or below 1 until above it.'
        )

    def test_is_a_standard_die(self):
        t = die.die.Rerolling(6)
        assert isinstance(t, die.die.Standard)
        assert t.values == list(range(1, 7))
        assert t.items == die.die.Standard(6).items

    def test_roll_no_reroll(self):
        t = die.die.Rerolling(6, rng=SequenceRng([3]))
        assert t.roll() == 3

    def test_roll_rerolls_once_keeping_second(self):
        t = die.die.Rerolling(6, rng=SequenceRng([1, 5]))
        assert t.roll() == 5

    def test_roll_once_keeps_second_even_in_range(self):
        t = die.die.Rerolling(6, 2, rng=SequenceRng([1, 2]))
        assert t.roll() == 2

    def test_roll_recursive_rerolls_until_out_of_range(self):
        t = die.die.Rerolling(6, 2, once=False, rng=SequenceRng([1, 2, 1, 3]))
        assert t.roll() == 3

    def test_history_records_only_kept_roll(self):
        t = die.die.Rerolling(6, rng=SequenceRng([1, 5, 4]))
        t.roll(2, func=list)
        assert t[:] == [5, 4]
        assert t.history == [('5', 5), ('4', 4)]
        assert t.history[-1] == t.result

    def test_recursive_reroll_records_only_final_kept_roll(self):
        # d6rr2 rolling/rerolling 1, 2, 1, 5 discards 1, 2, 1; history holds only 5.
        t = die.die.Rerolling(6, reroll_range=2, once=False, rng=SequenceRng([1, 2, 1, 5]))
        t.roll()
        assert len(t) == 1
        assert t[:] == [5]
        assert t.history == [('5', 5)]
        assert t.history[-1] == t.result

    def test_roll_custom_explode_range(self):
        t = die.die.Exploding(100, explode_range=5, rng=SequenceRng([96, 1]))
        assert t.roll() == 97

    def test_init_good_defaults_explode_to_low_to_self(self):
        t = die.die.Exploding(100, explode_range_low=5)
        assert t.sides == 100
        assert t.notation == 'd100x'

    def test_init_double_ended_description(self):
        t = die.die.Exploding(100, explode_range=5, explode_range_low=5)
        assert 'explodes at or below 5 subtracting a roll of' in t.description

    def test_roll_no_low_explosion_by_default(self):
        t = die.die.Exploding(6, rng=SequenceRng([1]))
        assert t.roll() == 1

    def test_roll_single_low_explosion(self):
        t = die.die.Exploding(
            100,
            explode_range=5,
            explode_range_low=5,
            rng=SequenceRng([3, 20]),
        )
        assert t.roll() == -17

    def test_roll_low_explosion_recursive(self):
        t = die.die.Exploding(6, explode_range_low=2, rng=SequenceRng([1, 2, 4]))
        assert t.roll() == 3

    def test_roll_low_explosion_explicit_explode_to_low(self):
        stub = StubDie(7)
        t = die.die.Exploding(20, explode_range_low=2, explode_to_low=stub, rng=SequenceRng([1]))
        assert t.roll() == -6

    def test_coercion_and_operators(self):
        t = die.die.Exploding(6, rng=SequenceRng([3]))
        assert int(t) == 3
        t = die.die.Exploding(6, rng=SequenceRng([3]))
        assert t + 1 == 4


class TestNumeric(TestNumericBased):
    die_class = die.die.Numeric
    get_face = lambda self, face: face
    get_value = lambda self, face: face
    get_count = lambda self, face: 1
    bad_spec = (
        None,
        '+',
        (1,),
    )
    good_spec = (1, 2, 3, 1.0, 2.0, -3)
    expected_faces = ('1', '2', '3', '1.0', '2.0', '-3')
    expected_values = (1, 2, 3, 1.0, 2.0, -3)


class TestSymbolic(TestNumericBased):
    die_class = die.die.Symbolic
    bad_spec = (None, 1, (), ('+', 3), ('', 1, 0), ('', 0, -2))
    good_spec = (('+', 1, 1), ('-', -1.45, 3), ('', 3, 1), (' ', 4, 1), ('g', 't', 2))
    expected_faces = ('+', '-', '-', '-', '', ' ', 'g', 'g')
    expected_values = (1, -1.45, -1.45, -1.45, 3, 4, 't', 't')

    def test_numeric_computed_from_values(self):
        assert die.die.Symbolic('load', (('1', 1, 3), ('2', 2, 1))).numeric
        assert not die.die.Symbolic('mix', (('1', 1, 1), ('g', 't', 1))).numeric

    def test_numeric_roll_sums_by_default(self):
        t = die.die.Symbolic('load', (('1', 1, 3), ('2', 2, 1)), rng=StubRng(0))
        assert t.roll() == 1
        assert t.roll(3) == 3
        assert t(3) == 3

    def test_non_numeric_roll_scalar_or_list_by_default(self):
        t = die.die.Symbolic('coin', (('H', 'heads', 1),), rng=StubRng(0))
        assert t.roll() == 'heads'
        assert t.roll(3) == ['heads', 'heads', 'heads']
