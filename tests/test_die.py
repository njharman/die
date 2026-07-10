import operator

import pytest

import die.die


class TestDie:
    """Direct tests of the base Die class (not routed through a subclass)."""

    faces = (('+', 1), ('', 0), ('-', -1))

    def test_init_bad_faces(self):
        with pytest.raises(ValueError, match='Invalid faces'):
            die.die.Die('name', [])

    def test_init_bad_name(self):
        for name in (None, 0, 4.2, object()):
            with pytest.raises(ValueError, match='Invalid name'):
                die.die.Die(name, self.faces)

    def test_init_good(self):
        t = die.die.Die('name', self.faces)
        assert t.name == 'name'
        assert t.faces == ['+', '', '-']
        assert t.values == [1, 0, -1]
        assert t.sides == 3

    def test_str(self):
        t = die.die.Die('name', self.faces)
        assert str(t) == 'name'

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

    def test_index(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'randint', lambda a, b: 1)
        t = die.die.Die('name', self.faces)
        seq = list(range(10))
        assert operator.index(t) == 1
        assert seq[t] == 1

    def test_roll_count_zero_returns_scalar(self):
        t = die.die.Die('name', self.faces)
        assert t.roll(0) in t.values

    def test_roll_count_negative_returns_empty_list(self):
        t = die.die.Die('name', self.faces)
        assert t.roll(-1) == []
        assert t.tuple_roll(-1) == []

    def test_iter(self):
        t = die.die.Die('name', self.faces)
        it = t.iter()
        rolls = [next(it) for _ in range(5)]
        assert len(rolls) == 5
        assert all(r in t.values for r in rolls)

    def test_iter_with_count(self):
        t = die.die.Die('name', self.faces)
        it = t.iter(3)
        rolls = next(it)
        assert len(rolls) == 3

    def test_tuple_iter(self):
        t = die.die.Die('name', self.faces)
        it = t.tuple_iter()
        faces = [next(it) for _ in range(5)]
        assert len(faces) == 5
        assert all(f in t.items for f in faces)

    def test_equality_ignores_subclass(self):
        # __eq__ only compares _sides/_faces, not type, so a Weird die and a
        # NumericBased die with identical faces are equal.
        spec_weird = (('a', 1, 1), ('b', 2, 1))
        spec_numeric = (('a', 1, 1), ('b', 2, 1))
        w = die.die.Weird('w', spec_weird)
        n = die.die.NumericBased('n', spec_numeric)
        assert w == n
        assert not (w != n)

    def test_deterministic_roll(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'randint', lambda a, b: 2)
        t = die.die.Die('name', self.faces)
        assert t.roll() == 0
        assert t.tuple_roll() == ('', 0)
        assert t.roll(3) == [0, 0, 0]
        assert t.tuple_roll(3) == [('', 0), ('', 0), ('', 0)]

    def test_deterministic_coercion(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'randint', lambda a, b: 1)
        t = die.die.Die('name', self.faces)
        assert t() == 1
        assert int(t) == 1
        assert float(t) == 1.0

    def test_deterministic_operators(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'randint', lambda a, b: 1)
        t = die.die.Die('name', self.faces)
        assert t + 1 == 2
        assert 1 + t == 2
        assert t - 1 == 0
        assert 1 - t == 0
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

    def test_deterministic_comparisons(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'randint', lambda a, b: 1)
        t = die.die.Die('name', self.faces)
        assert (t > 0) is True
        assert (t >= 1) is True
        assert (t < 0) is False
        assert (t <= 1) is True


# This class is reused for other test cases below
class TestNumericBased:
    numeric = True
    die_class = die.die.NumericBased
    get_face = lambda self, face: face[0]
    get_value = lambda self, face: face[1]
    get_count = lambda self, face: face[2]
    good_names = ('dTest', 34, ' bob ')
    good_name = good_names[0]
    bad_names = ('', ' ', '  ', None)
    bad_spec = (None, 1, (), ('+', 3), ('', 1, 0), ('', 0, -2), ('', 't', 1))
    good_spec = (('+', 1, 2), ('-', -1.45, 2), ('', 3, 1), (' ', 4, 1))
    expected_faces = ('+', '+', '-', '-', '', ' ')
    expected_values = (1, 1, -1.45, -1.45, 3, 4)

    def test_init(self):
        for name in self.good_names:
            self.die_class(name, self.good_spec)
        for name in self.bad_names:
            with pytest.raises(ValueError, match='Invalid name'):
                self.die_class(name, self.good_spec)
        for i in range(len(self.bad_spec)):
            faces = [
                self.bad_spec[i],
            ]
            faces.extend(self.good_spec)
            with pytest.raises(ValueError, match='Bad spec'):
                self.die_class(self.good_name, faces)

    def test_init_bad_spec_not_iterable(self):
        with pytest.raises(ValueError, match='Bad spec'):
            self.die_class(self.good_name, 123)

    def test_init_empty_spec(self):
        with pytest.raises(ValueError, match='Invalid faces'):
            self.die_class(self.good_name, ())

    def test_minimal(self):
        t = self.die_class(self.good_name, self.good_spec)
        t.roll()
        str(t)
        repr(t)
        assert len(t.tuple_roll()) == 2
        assert len(t.roll(3)) == 3
        assert len(t.tuple_roll(3)) == 3

    def test_coercion(self):
        t = self.die_class(self.good_name, self.good_spec)
        t()
        if t.numeric:
            int(t)
            float(t)

    def test_operators(self):
        t = self.die_class(self.good_name, self.good_spec)
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
        t = self.die_class(self.good_name, self.good_spec)
        if t.numeric:
            assert isinstance(t > 1, bool)
            assert isinstance(t >= 1, bool)
            assert isinstance(t < 1, bool)
            assert isinstance(t <= 1, bool)

    def test_deterministic_roll(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'randint', lambda a, b: 1)
        t = self.die_class(self.good_name, self.good_spec)
        expected_face = self.expected_faces[0]
        expected_value = self.expected_values[0]
        assert t.roll() == expected_value
        assert t.tuple_roll() == (expected_face, expected_value)
        if t.numeric:
            assert t() == expected_value
            assert t + 1 == expected_value + 1
            assert 1 + t == expected_value + 1
            assert (t > expected_value - 1) is True
            assert (t <= expected_value) is True

    def test_equality(self):
        t1 = self.die_class(self.good_name, self.good_spec)
        t2 = self.die_class(self.good_name, self.good_spec)
        t3 = die.die.Standard(6)
        assert t1 == t1
        assert t1 == t2
        assert t1 != t3
        assert t1 != 1
        assert t1 != repr(t1)
        assert not (t1 == None)  # noqa: E711 - exercises __eq__ directly

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
            t = self.die_class(self.good_name, spec)
            assert isinstance(t.description, str)
            assert t.description
            assert str(t) == self.good_name
            assert t.numeric == self.numeric
            assert t.sides == sides
            assert t.faces == expected_faces
            assert t.values == expected_values


class TestStandardDie:
    good = (1, 5, 80, 99, 2000)
    bad = (0, -1, 'what', None)

    def test_init(self):
        for i in self.bad:
            with pytest.raises(ValueError, match='Bad number of sides'):
                die.die.Standard(i)

    def test_init_sides_coercion(self):
        assert die.die.Standard(6.9).sides == 6
        assert die.die.Standard('6').sides == 6
        assert die.die.Standard(True).sides == 1

    def test_minimal(self):
        t = die.die.Standard(6)
        t.roll()
        t.tuple_roll()
        assert len(t.roll(2)) == 2
        assert len(t.tuple_roll(2)) == 2

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

    def test_equality(self):
        t1 = die.die.Standard(6)
        t2 = die.die.Standard(6)
        t3 = die.die.Standard(8)
        assert t1 == t1
        assert t1 == t2
        assert t1 != t3
        assert t1 != 1

    def test_deterministic_roll(self, monkeypatch):
        monkeypatch.setattr(die.die.random, 'randint', lambda a, b: 3)
        t = die.die.Standard(6)
        assert t.roll() == 3
        assert t + 1 == 4
        assert (t > 2) is True
        assert (t <= 3) is True


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


class TestWeird(TestNumericBased):
    numeric = False
    die_class = die.die.Weird
    bad_spec = (None, 1, (), ('+', 3), ('', 1, 0), ('', 0, -2))
    good_spec = (('+', 1, 1), ('-', -1.45, 3), ('', 3, 1), (' ', 4, 1), ('g', 't', 2))
    expected_faces = ('+', '-', '-', '-', '', ' ', 'g', 'g')
    expected_values = (1, -1.45, -1.45, -1.45, 3, 4, 't', 't')
