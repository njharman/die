"""Die classes: base, standard, numeric, and symbolic."""

import numbers
import random


class Die:
    """Base Die class.

    Constraints:
      - Die are not hashable.
      - Die are numeric if obj.numeric == True.
      - Two Die are equal if they have identical faces.
      - obj(), int(obj), float(obj), obj.roll() return result of rolling die.
      - +, -, *, //, /, %, ** and >, >=, <, <= operators cause die roll and use
        that result; they only reliably succeed when the die is numeric. On a
        non-numeric (Symbolic) die they may raise, depending on the face values.
      - ==, != do NOT cause die roll.
      - Comparisons (>, >=, <, <=) and sorting all roll the die, so results are
        not stable/repeatable between comparisons; do not rely on sorted() giving a
        consistent order.

    Properties (all read only):
      - name: short textual identifier.
      - description: textual description.
      - faces: list of face texts.
      - items: list of (face, value) tuples.
      - numeric: [boolean] True if all of die's faces map to numeric **values**.
      - sides: number of sides die has.
      - values: list of face values.

    Class attributes:
      - rng: Source of randomness shared by every Die instance; default is the
        ``random`` module. Assign e.g. ``die.Die.rng = random.Random(seed)`` to affect
        every die at once. Overridden per-instance by the ``rng`` constructor param.

    A standard six sided die::
        die.Die('d6', (('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6)))

    :param name: Identifies Die of this type.
    :param faces: List of (text, value), one per face.
    :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
    :raises ValueError: If name is empty/None or faces is empty.
    """

    # TODO: numeric is documented as a read-only property above but is a plain class
    # attribute, so nothing prevents `some_die.numeric = ...` shadowing it per-instance.
    # Reconsider making it a real property in a future (API-changing) commit.
    numeric = True
    rng = random

    def __init__(self, name, faces, rng=None):
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
        # Not passed as parameter because it's likely to be dynamically set by subclasses based on faces.
        self._description = name

    def __str__(self):
        return self._name

    def __repr__(self):
        return f'<{self.__class__.__name__}({self._name}, {self._faces})>'

    def __call__(self):
        """Roll die."""
        return self.roll()

    def __int__(self):
        """Rolls die."""
        return int(self.roll())

    def __float__(self):
        """Rolls die."""
        return float(self.roll())

    def __index__(self):
        """Rolls die."""
        return int(self.roll())

    def __gt__(self, other):
        """Rolls die."""
        return self.roll() > other

    def __ge__(self, other):
        """Rolls die."""
        return self.roll() >= other

    def __lt__(self, other):
        """Rolls die."""
        return self.roll() < other

    def __le__(self, other):
        """Rolls die."""
        return self.roll() <= other

    def __add__(self, other):
        """Rolls die."""
        return self.roll() + other

    def __radd__(self, other):
        """Rolls die."""
        return self.roll() + other

    def __sub__(self, other):
        """Rolls die."""
        return self.roll() - other

    def __rsub__(self, other):
        """Rolls die."""
        return self.roll() - other

    def __mul__(self, other):
        """Rolls die."""
        return self.roll() * other

    def __rmul__(self, other):
        """Rolls die."""
        return self.roll() * other

    def __truediv__(self, other):
        """Rolls die."""
        return self.roll() / other

    def __rtruediv__(self, other):
        """Rolls die."""
        return other / self.roll()

    def __floordiv__(self, other):
        """Rolls die."""
        return self.roll() // other

    def __rfloordiv__(self, other):
        """Rolls die."""
        return other // self.roll()

    def __mod__(self, other):
        """Rolls die."""
        return self.roll() % other

    def __rmod__(self, other):
        """Rolls die."""
        return other % self.roll()

    def __pow__(self, other):
        """Rolls die."""
        return self.roll() ** other

    def __rpow__(self, other):
        """Rolls die."""
        return other ** self.roll()

    __hash__ = None

    def __eq__(self, other):
        if not isinstance(other, Die):
            return NotImplemented
        return self._faces == other._faces

    @property
    def name(self):
        """Short textual identifier."""
        return self._name

    @property
    def description(self):
        """Textual description of die faces."""
        return self._description

    @property
    def faces(self):
        """List of face texts."""
        return [x[0] for x in self._faces]

    @property
    def values(self):
        """List of face values."""
        return [x[1] for x in self._faces]

    @property
    def items(self):
        """List of face (text, value) tuples."""
        return list(self._faces)

    @property
    def sides(self):
        """Count of die faces."""
        return len(self._faces)

    def roll(self):
        """Roll die.

        :return: Value of roll.
        """
        return self.rng.choice(self._faces)[1]

    def rolls(self, count):
        """Roll die ``count`` times.

        :param count: Number of rolls.
        :return: List of rolled values.
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
    """Die with possibly non-numeric face texts, but each face has an associated numeric value.

    Fudge (www.fudgerpg.com) die::
        die.NumericBased('dF', (('+', 1, 2), ('', 0, 2), ('-', -1, 2)))

    :param name: Identifies dice of this type.
    :param spec: List of tuples (facetext, value, count).
    :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
    :raises ValueError: If spec is malformed or any value is non-numeric or count < 1.
    """

    def __init__(self, name, spec, rng=None):
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


class Numeric(NumericBased):
    """Die with non-sequential, numeric faces, possibly repeating.

    A backgammon doubling die::
        die.Numeric('backgammon', (2, 4, 8, 16, 32, 64))

    :param name: Uniquely identifies dice of this type.
    :param spec: List of numbers, one per face of die.
    :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
    :raises ValueError: If spec is not iterable of numbers.
    """

    def __init__(self, name, spec, rng=None):
        try:
            faces = [(x, x, 1) for x in spec]
        except TypeError:
            raise ValueError('Bad spec') from None
        super().__init__(name, faces, rng)
        self._description = f'Numeric die with {self.sides} faces [{",".join(self.faces)}].'


class Standard(Numeric):
    """Die with sequential, numeric faces.

    The common six sided die::
        die.Standard(6)

    :param sides: Number of faces die has, integral and > 0.
    :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
    :raises ValueError: If sides is not a positive integer.
    """

    def __init__(self, sides, rng=None):
        def _check_sides(sides):
            if sides != int(sides) or sides < 1:
                raise ValueError
            return int(sides)

        try:
            sides = _check_sides(sides)
        except TypeError, ValueError:
            raise ValueError('Bad number of sides') from None
        super().__init__(f'd{sides}', range(1, sides + 1), rng)
        self._description = f'Numeric die with {self.sides} faces numbered 1 through {self.sides}.'


class Symbolic(Die):
    """Die with "faces", and "values" that aren't necessarily numeric.

    A coin flip::
        die.Symbolic('coin', (('H', 'heads', 1), ('T', 'tails', 1)))

    :param name: Uniquely identifies dice of this type.
    :param spec: List of tuples (facetext, facevalue, count).
                facevalue must be convertible into string but
                otherwise is free to get funky, count is number
                of faces with these text/value.
    :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
    :raises ValueError: If spec is malformed or any count < 1.
    """

    numeric = False

    def __init__(self, name, spec, rng=None):
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
