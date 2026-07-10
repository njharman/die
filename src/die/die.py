import numbers
import random


class Die:
    """Base Die class.

    Some properties:
      - Die are not hashable.
      - Die are not sortable.
      - obj(), int(obj), float(obj), obj.roll() return result of rolling die.
      - Two Die with identical faces are equal.
      - Die are numeric if obj.numeric == True.
      - For numeric Die; +, -, *, //, /, %, ** operators cause die roll.
      - For numeric Die; >, >=, <, <= operators cause die roll.
      - ==, != do NOT cause die roll.

    Properties (all read only):
      - name: short textual identifier.
      - description: textual description.
      - faces: list of face texts.
      - items: list of (face, value) tuples.
      - numeric: [boolean] True if all of die's faces map to numeric **values**.
      - sides: number of sides die has.
      - values: list of face values.
    """

    numeric = True
    # Source of randomness shared by every die; assign e.g. die.Die.rng = random.Random(seed).
    rng = random

    def __init__(self, name, faces, rng=None):
        """
        :param name: Identifies Die of this type.
        :param faces: List of (text, value), one per face.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        """
        if name is None:
            raise ValueError('Invalid name')
        self._name = str(name).strip()
        if not self._name:
            raise ValueError('Invalid name')
        self._faces = tuple(faces)
        if not self._faces:
            raise ValueError('Invalid faces')
        if rng is not None:
            self.rng = rng
        # Not passed as parameter because it's likely to be dynamically set based on faces.
        # Subclasses are expected to set _description.
        self._description = name

    def __str__(self):
        return self._name

    def __repr__(self):
        return f'<{self.__class__.__name__}({self._name}, {self._faces})>'

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
            return NotImplemented
        return self._faces == other._faces

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

    @property
    def name(self):
        """Short textual identifier."""
        return self._name

    @property
    def description(self):
        """Textual description."""
        return self._description

    @property
    def faces(self):
        """List of face texts."""
        return [x[0] for x in self._faces]

    @property
    def items(self):
        """List of (face, value) tuples."""
        return list(self._faces)

    @property
    def values(self):
        """List of face values."""
        return [x[1] for x in self._faces]

    @property
    def sides(self):
        """Number of 'sides'."""
        return len(self._faces)

    def roll(self):
        """Roll die.
        :return: Value of roll.
        """
        return self.rng.choice(self._faces)[1]

    def rolls(self, count):
        """Roll die ``count`` times.
        :param count: Number of rolls.
        :return: List of roll values.
        """
        return [face[1] for face in self.rng.choices(self._faces, k=count)]

    def roll_item(self):
        """Roll die.
        :return: (face, value) of roll.
        """
        return self.rng.choice(self._faces)

    def roll_items(self, count):
        """Roll die ``count`` times.
        :param count: Number of rolls.
        :return: List of (face, value) tuples.
        """
        return list(self.rng.choices(self._faces, k=count))


class NumericBased(Die):
    """Die with possibly non-numeric face texts, but each face has an
    associated numeric value.

    Fudge (www.fudgerpg.com) die::
        die.NumericBased('dF', (('+', 1, 2), ('', 0, 2), ('-', -1, 2)))
    """

    def __init__(self, name, spec, rng=None):
        """
        :param name: Identifies dice of this type.
        :param spec: List of tuples (facetext, value, count).
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        """

        def _check_face(text, value, count):
            if count < 1 or not isinstance(value, numbers.Number):
                raise ValueError
            return str(text), value

        faces = list()
        try:
            for text, value, count in spec:
                face = _check_face(text, value, count)
                faces.extend(face for _ in range(count))
        except TypeError, ValueError:
            raise ValueError('Bad spec') from None
        super().__init__(name, faces, rng)
        faces_str = ','.join(f'"{x[0]}"={x[1]}' for x in self._faces)
        self._description = f'NumericBased die with {self.sides} faces, [{faces_str}].'


class Standard(NumericBased):
    """Die with sequential, numeric faces.

    The common six sided die::
        die.Standard(6)
    """

    def __init__(self, sides, rng=None):
        """
        :param sides: Number of faces die has, integral and > 0.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        """

        def _check_sides(sides):
            if sides != int(sides) or sides < 1:
                raise ValueError
            return int(sides)

        try:
            sides = _check_sides(sides)
        except TypeError, ValueError:
            raise ValueError('Bad number of sides') from None
        spec = [(x, x, 1) for x in range(1, sides + 1)]
        super().__init__(f'd{sides}', spec, rng)
        self._description = f'Numeric die with {self.sides} faces numbered 1 through {self.sides}.'


class Numeric(NumericBased):
    """Die with non-sequential, numeric faces, possibly repeating.

    A backgammon doubling die::
        die.Numeric('backgammon', (2, 4, 8, 16, 32, 64))
    """

    def __init__(self, name, spec, rng=None):
        """
        :param name: Uniquely identifies dice of this type.
        :param spec: List of numbers, one per face of die.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        """
        try:
            faces = [(x, x, 1) for x in spec]
        except TypeError:
            raise ValueError('Bad spec') from None
        super().__init__(name, faces, rng)
        self._description = f'Numeric die with {self.sides} faces [{",".join(self.faces)}].'


class Symbolic(Die):
    """Die with textual faces, and 'values' that aren't necessarily numeric."""

    numeric = False

    def __init__(self, name, spec, rng=None):
        """
        :param name: Uniquely identifies dice of this type.
        :param spec: List of tuples (facetext, facevalue, count).
                    facevalue must be convertible into string but
                    otherwise is free to get funky. count is number
                    of faces with these text/value.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        """

        def _check_count(count):
            if count < 1:
                raise ValueError
            return count

        faces = list()
        try:
            for text, value, count in spec:
                faces.extend((text, value) for _ in range(_check_count(count)))
        except TypeError, ValueError:
            raise ValueError('Bad spec') from None
        super().__init__(name, faces, rng)
        faces_str = ','.join(f'"{x[0]}"={x[1]}' for x in self._faces)
        self._description = f'Symbolic die with {self.sides} faces [{faces_str}].'
