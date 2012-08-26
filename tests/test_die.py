import unittest

import die.die


class StandardDieTestCase(unittest.TestCase):
    good = (1, 5, 80, 99, 2000)
    bad = (0, -1, 'what', None)

    def test_init(self):
        for i in self.bad:
            self.assertRaises(ValueError, die.die.Standard, i)

    def test_minimal(self):
        t = die.die.Standard(6)
        t.roll()
        t.tuple_roll()
        self.assertEqual(2, len(t.rolls(2)))
        self.assertEqual(2, len(t.tuple_rolls(2)))

    def test_properties(self):
        for i in self.good:
            t = die.die.Standard(i)
            t.description
            self.assertEqual(i, len(t.faces))
            self.assertEqual(i, len(t.values))
            self.assertEqual(i, t.sides)
            self.failUnless(t.numeric)


# This class is reused for other test cases below
class NumericBasedTestCase(unittest.TestCase):
    numeric = True
    test_class = die.die.NumericBased
    get_face = lambda self, face: face[0]
    get_value = lambda self, face: face[1]
    get_count = lambda self, face: face[2]
    good_names = ('dTest', 34, ' bob ')
    good_name = good_names[0]
    bad_names = ('', None, (), ' ', '  ')
    bad_spec = (None, 1, (), ('+', 3), ('', 1, 0), ('', 0, -2), ('', 't', 1))
    good_spec = (('+', 1, 2), ('-', -1.45, 2), ('', 3, 1), (' ', 4, 1))
    expected_faces = ('+', '+', '-', '-', '', ' ')
    expected_values = (1, 1, -1.45, -1.45, 3, 4)

    def test_init(self):
        for name in self.good_names:
            self.test_class(name, self.good_spec)
        for name in self.bad_names:
            self.assertRaises(ValueError, self.test_class, name, self.good_spec)
        for i in range(len(self.bad_spec)):
            faces = [self.bad_spec[i], ]
            faces.extend(self.good_spec)
            self.assertRaises(ValueError, self.test_class, self.good_name, faces)

    def test_minimal(self):
        t = self.test_class(self.good_name, self.good_spec)
        t.roll()
        t.tuple_roll()
        self.assertEqual(2, len(t.rolls(2)))
        self.assertEqual(2, len(t.tuple_rolls(2)))

    def test_properties(self):
        for i in range(40):
            sides = 0
            spec = list()
            expected_faces = list()
            expected_values = list()
            spec_idx = i % len(self.good_spec)
            for f in range(i % 8):
                face = self.good_spec[spec_idx]
                spec.append(face)
                for x in range(self.get_count(face)):
                    sides += 1
                    expected_faces.append(str(self.get_face(face)))
                    expected_values.append(self.get_value(face))
            if not spec:
                continue
            t = self.test_class(self.good_name, spec)
            t.description
            self.assertEqual(str(t), self.good_name)
            self.assertEqual(self.numeric, t.numeric)
            self.assertEqual(sides, t.sides)
            self.assertEqual(expected_faces, t.faces)
            self.assertEqual(expected_values, t.values)


class NumericTestCase(NumericBasedTestCase):
    test_class = die.die.Numeric
    get_face = lambda self, face: face
    get_value = lambda self, face: face
    get_count = lambda self, face: 1
    bad_spec = (None, '+', (1, ), )
    good_spec = (1, 2, 3, 1.0, 2.0, -3)
    expected_faces = ('1', '2', '3', '1.0', '2.0', '-3')
    expected_values = (1, 2, 3, 1.0, 2.0, -3)


class WeirdTestCase(NumericBasedTestCase):
    numeric = False
    test_class = die.die.Weird
    bad_spec = (None, 1, (), ('+', 3), ('', 1, 0), ('', 0, -2))
    good_spec = (('+', 1, 1), ('-', -1.45, 3), ('', 3, 1), (' ', 4, 1), ('g', 't', 2))
    expected_faces = ('+', '-', '-', '-', '', ' ', 'g', 'g')
    expected_values = (1, -1.45, -1.45, -1.45, 3, 4, 't', 't')
