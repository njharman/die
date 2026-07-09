import pytest

import die.die


class TestStandardDie:
    good = (1, 5, 80, 99, 2000)
    bad = (0, -1, 'what', None)

    def test_init(self):
        for i in self.bad:
            with pytest.raises(ValueError, match='Bad number of sides'):
                die.die.Standard(i)

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


# This class is reused for other test cases below
class TestNumericBased:
    numeric = True
    die_class = die.die.NumericBased
    get_face = lambda self, face: face[0]
    get_value = lambda self, face: face[1]
    get_count = lambda self, face: face[2]
    good_names = ('dTest', 34, ' bob ')
    good_name = good_names[0]
    bad_names = ('', ' ', '  ')
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

    def test_equality(self):
        t1 = self.die_class(self.good_name, self.good_spec)
        t2 = self.die_class(self.good_name, self.good_spec)
        t3 = die.die.Standard(6)
        assert t1 == t1
        assert t1 == t2
        assert t1 != t3
        assert t1 != 1
        assert t1 != repr(t1)

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
