import random


class Die:
    """Base Die class.

    Some properties:
      - Die are not hashable.
      - Die are not sortable.
      - obj(), int(obj), float(obj), obj.roll() return result of rolling die.
      - Two Die with identical faces are equal.
      - Die are numeric if obj.numeric == True.
      - For numeric Die; +, -, *, //, /, %, ^, **, operators cause die roll.
      - For numeric Die; >, >=, <, <= operators cause die roll.
      - =, != do NOT cause die roll.

    Attributes (all read only):
      - name: short textual identifier.
      - description: textual description.
    Properties (all read only):
      - faces: list of face texts.
      - items: list of (face, value) tuples.
      - numeric: [boolean] True if all of die's faces map to numeric **values**.
      - sides: number of sides dice has.
      - values: list of face values.
    """

    faces = property(lambda self: [x[0] for x in self._faces], doc="""List of face texts.""")
    items = property(lambda self: [x for x in self._faces], doc="""List of (face, value) tuples.""")
    numeric = True
    sides = property(lambda s: s._sides, doc="""Number of 'sides'.""")
    values = property(lambda self: [x[1] for x in self._faces], doc="""List of face values.""")

    def __init__(self, name, faces):
        """
        :param name: Identifies Die of this type.
        :param faces: List of (text, value), one per face.
        """

        def _clean_name(name):
            name = name.strip()
            if not name:
                raise ValueError
            return name

        try:
            self.name = _clean_name(name)
        except AttributeError, TypeError, ValueError:
            raise ValueError('Invalid name') from None
        # Subclasses are expected to set description.
        # Not passed as parameter because it's likely to dynamically set based on _sides, _faces.
        self.description = self.name
        if len(faces) == 0:
            raise ValueError('Invalid faces')
        self._faces = faces
        self._sides = len(faces)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.name}, {self._faces})>'

    def __call__(self):
        return self.roll()

    def __int__(self):
        return int(self.roll())

    def __float__(self):
        return float(self.roll())

    def __index__(self):
        """Slicing."""
        return int(self.roll())

    __hash__ = None

    def __eq__(self, other):
        if not isinstance(other, Die):
            return False
        return self._sides == other._sides and self._faces == other._faces

    def __ne__(self, other):
        if not isinstance(other, Die):
            return True
        return self._sides != other._sides or self._faces != other._faces

    def __gt__(self, other):
        return self.roll() > other

    def __ge__(self, other):
        return self.roll() >= other

    def __lt__(self, other):
        return self.roll() < other

    def __le__(self, other):
        return self.roll() <= other

    def __add__(self, other):
        return self.roll() + other

    def __radd__(self, other):
        return self.roll() + other

    def __sub__(self, other):
        return self.roll() - other

    def __rsub__(self, other):
        return self.roll() - other

    def __mul__(self, other):
        return self.roll() * other

    def __rmul__(self, other):
        return self.roll() * other

    def __truediv__(self, other):
        return self.roll() / other

    def __rtruediv__(self, other):
        return other / self.roll()

    def __floordiv__(self, other):
        return self.roll() // other

    def __rfloordiv__(self, other):
        return other // self.roll()

    def __mod__(self, other):
        return self.roll() % other

    def __rmod__(self, other):
        return other % self.roll()

    def __pow__(self, other):
        return self.roll() ** other

    def __rpow__(self, other):
        return other ** self.roll()

    def roll(self, count=0):
        """One or more die rolls.
        :param count: [0] Return list of ``count`` rolls
        :return: Value of roll or list of values
        """
        if count:
            return [self._faces[random.randint(1, self._sides) - 1][1] for i in range(count)]
        return self._faces[random.randint(1, self._sides) - 1][1]

    def iter(self, count=0):
        """Iterator of infinite rolls.
        :param count: [0] Return list of ``count`` rolls
        """
        while True:
            yield self.roll(count)

    def tuple_roll(self, count=0):
        """One or more die rolls.
        :param count: [0] Return list of ``count`` rolls
        :return: (face, value) of roll or list of same
        """
        if count:
            return [self._faces[random.randint(1, self._sides) - 1] for i in range(count)]
        return self._faces[random.randint(1, self._sides) - 1]

    def tuple_iter(self, count=0):
        """Iterator of infinite tuple_rolls.
        :param count: [0] Return list of ``count`` tuples
        """
        while True:
            yield self.tuple_roll(count)


class NumericBased(Die):
    """Die with possibly non-numeric face texts, but each face has an
    associated numeric value.

    Fudge(www.fudgerpg.com) die::
        C{die.NumericBased('dF', (('+',1,2), ('',0,2), ('-',-1,2)))}
    """

    def __init__(self, name, spec):
        """
        :param name: Identifies dice of this type
        :param spec: List of tuples (facetext, value, count)
        """
        if name is None:
            raise ValueError('Invalid name')

        def _check_face(text, value, count):
            if count < 1:
                raise ValueError
            1 - value  # must be better way to check if value numeric
            return str(text), value

        faces = list()
        try:
            for text, value, count in spec:
                face = _check_face(text, value, count)
                faces.extend(face for x in range(count))
        except TypeError, ValueError:
            raise ValueError('Bad spec') from None
        super().__init__(str(name), faces)
        faces_str = ','.join(f'"{x[0]}"={x[1]}' for x in self._faces)
        self.description = f'NumericBased die with {self._sides} faces, [{faces_str}].'


class Standard(NumericBased):
    """Die with sequential, numeric faces.

    The common six sided die would be::
        C{die.Standard(6)}
    """

    def __init__(self, sides):
        """:param sides: number of faces die has."""

        def _check_sides(sides):
            sides = int(sides)
            if sides <= 0:
                raise ValueError
            return sides

        try:
            sides = _check_sides(sides)
        except TypeError, ValueError:
            raise ValueError('Bad number of sides') from None
        name = f'd{sides}'
        spec = [(x, x, 1) for x in range(1, sides + 1)]
        super().__init__(name, spec)
        self.description = f'Numeric die with {self._sides} faces numbered 1 through {self._sides}.'


class Numeric(NumericBased):
    """Die with non-sequential, numeric faces, possibly repeating.

    Ex. A backgammon die::
        C{die.Numeric('backgammon', (2,4,8,16,32,64))}
    """

    def __init__(self, name, spec):
        """
        :param name: Uniquely identifies dice of this type.
        :param spec: List of numbers one per face of die.
        """
        if name is None:
            raise ValueError('Invalid name')
        try:
            faces = [(x, x, 1) for x in spec]
        except TypeError:
            raise ValueError('Bad spec') from None
        super().__init__(str(name), faces)
        self.description = f'Numeric die with {self._sides} faces [{",".join(self.faces)}].'


class Weird(Die):
    """Die with textual faces, and 'values' that aren't necessarily numeric."""

    numeric = False

    def __init__(self, name, spec):
        """
        :param name: Uniquely identifies dice of this type.
        :param spec: List of tuples - (facetext, facevalue, count)
                    facevalue must be convertible into string but
                    otherwise is free to get funky. count is number
                    of faces with these text/value.
        """

        def _check_count(count):
            if count < 1:
                raise ValueError
            return count

        if name is None:
            raise ValueError('Invalid name')
        faces = list()
        try:
            for text, value, count in spec:
                faces.extend((text, value) for x in range(_check_count(count)))
        except TypeError, ValueError:
            raise ValueError('Bad spec') from None
        super().__init__(str(name), faces)
        faces_str = ','.join(f'"{x[0]}"={x[1]}' for x in self._faces)
        self.description = f'Weird die with {self._sides} faces [{faces_str}].'
