"""Die classes: base, standard, numeric, constant, exploding, and symbolic."""

import numbers
import random
from collections import namedtuple

_UNSET = object()

Result = namedtuple('Result', ('face', 'value'))


class _Rollable:
    """Shared rolling behavior of ``Die`` and ``Roll``: operators and ``roll()``.

    Single source of truth for the operator semantics both document: every operator
    rolls (via subclass ``_roll_once()``) and uses that result.
    """

    def __call__(self, count=1, func=_UNSET):
        """Roll ``count`` times, combining results with ``func``.

        Defers to ``roll()``'s own default when ``func`` isn't given, so subclasses only
        need to override ``roll()`` to change their default ``func``.
        """
        if func is _UNSET:
            return self.roll(count)
        return self.roll(count, func)

    def __str__(self):
        return str(self.roll())

    def __int__(self):
        """Rolls."""
        return int(self.roll())

    def __float__(self):
        """Rolls."""
        return float(self.roll())

    def __index__(self):
        """Rolls. This is called for alist[d6]."""
        return int(self.roll())

    def __gt__(self, other):
        """Rolls."""
        return self.roll() > other

    def __ge__(self, other):
        """Rolls."""
        return self.roll() >= other

    def __lt__(self, other):
        """Rolls."""
        return self.roll() < other

    def __le__(self, other):
        """Rolls."""
        return self.roll() <= other

    def __add__(self, other):
        """Rolls."""
        return self.roll() + other

    def __radd__(self, other):
        """Rolls."""
        return self.roll() + other

    def __sub__(self, other):
        """Rolls."""
        return self.roll() - other

    def __rsub__(self, other):
        """Rolls."""
        return other - self.roll()

    def __mul__(self, other):
        """Rolls."""
        return self.roll() * other

    def __rmul__(self, other):
        """Rolls."""
        return self.roll() * other

    def __truediv__(self, other):
        """Rolls."""
        return self.roll() / other

    def __rtruediv__(self, other):
        """Rolls."""
        return other / self.roll()

    def __floordiv__(self, other):
        """Rolls."""
        return self.roll() // other

    def __rfloordiv__(self, other):
        """Rolls."""
        return other // self.roll()

    def __mod__(self, other):
        """Rolls."""
        return self.roll() % other

    def __rmod__(self, other):
        """Rolls."""
        return other % self.roll()

    def __pow__(self, other):
        """Rolls."""
        return self.roll() ** other

    def __rpow__(self, other):
        """Rolls."""
        return other ** self.roll()

    __hash__ = None

    def __eq__(self, other):
        """Rolls."""
        return self.roll() == other

    def __ne__(self, other):
        """Rolls."""
        return self.roll() != other

    def __getitem__(self, index):
        """Value(s) of past rolls, by index into the roll history; does NOT roll.

        ``obj[-1]`` is the most recent roll's value, ``obj[0]`` the first's; a slice gives a
        list of values, and iteration yields them in roll order. Empty until the first roll,
        so ``obj[0]`` raises IndexError before then. Full (face, value)/(results, value)
        records are on ``history``.
        """
        if isinstance(index, slice):
            return [rolled.value for rolled in self._history[index]]
        return self._history[index].value

    @property
    def history(self):
        """List of full roll records, in roll order; does NOT roll.

        Each is a namedtuple: ``Result(face, value)`` for a ``Die``, ``Rolled(results, value)``
        for a ``Roll``; ``history[-1]`` matches the most-recent-roll properties. Empty until
        the first roll. A copy: mutating it does not affect the retained history.
        """
        return list(self._history)

    def __len__(self):
        """Number of rolls in the roll history; does NOT roll."""
        return len(self._history)

    def _check_rolled(self):
        if not self._history:
            raise RuntimeError('roll() has not been called')

    def clear(self):
        """Empty the roll history.

        Afterward the roll-state properties raise RuntimeError again, as before the
        first roll.
        """
        self._history.clear()

    def roll(self, count=1, func=sum):
        """Roll ``count`` times.

        :param count: [1] Number of times to roll.
        :param func: [sum] Applied to the list of ``count`` rolled values.
        :return: func applied to list of roll values.
        """
        values = [self._roll_once() for _ in range(count)]
        return func(values)


class Die(_Rollable):
    rng = random

    def __init__(self, notation, faces, rng=None):
        """Base Die class.

        A standard six sided die::
            die.Die('d6', (('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6)))

        Rolling:
          - obj.roll() and obj() roll the die ``count`` times (default 1) and return
            ``func`` (default ``sum``) applied to the list of rolled values.
          - The default ``sum`` raises TypeError on a non-numeric die (``numeric`` is True
            when every face value is a number); pass a ``func`` that handles the values, or
            use ``Symbolic``, which overrides the default (see ``Symbolic.roll``).
          - The die retains every roll. Subscript it to reach older rolls' values
            (``obj[-1]`` is the most recent, matching ``value``, ``obj[0]`` the first);
            slicing and iteration (``for value in obj``, ``list(obj)``, ``sum(obj)``) yield
            them in roll order. The ``history`` property holds the full ``Result(face, value)``
            namedtuples instead. Empty until the first roll, so ``obj[0]`` raises IndexError
            before then. ``len(obj)`` is the number of retained rolls; ``clear()`` empties
            the history.

        Operators (every one rolls):
          - str(obj), int(obj), float(obj) roll the die and return the coerced result.
          - +, -, *, /, //, %, ** roll the die and use that result; they only reliably
            succeed when the die is numeric.
          - >, >=, <, <=, ==, != also roll — equality included. Consequences: Die are not
            hashable; comparing or sorting dice gives unstable, unrepeatable results.
            Compare ``items`` for structural (identical faces) equality.

        Composing (does NOT roll):
          - ``plus``, ``minus``, ``times``, ``div``, ``mod`` each return a new ``Roll``
            combining this die with a Die, Roll, or number, e.g.
            ``d6.times(2).plus(3).div(d6)`` is the Roll ((d6*2)+3)/d6. Chains bind tight,
            left to right. See ``Roll`` for details.
          - ``keep_highest``, ``keep_lowest``, ``drop_highest``, ``drop_lowest`` each return a new
            ``Roll`` keeping/dropping the ``n`` (default 1) highest/lowest die values and
            summing the kept. See ``Roll`` for details.
          - ``successes``, ``failures`` each return a new ``Roll`` counting rolled values
            >= / <= a target. See ``Roll`` for details.
          - ``chance`` returns the cumulative percentage chance of a roll at or above
            (``gte=``) / at or below (``lte=``) a value. See ``Roll.chance``.

        Properties (all read only):
          - notation: short textual identifier; use this, not str(obj), for the notation
            text, since str(obj) rolls.
          - description: textual description.
          - faces: list of face texts.
          - items: list of (face, value) tuples.
          - numeric: [boolean] True if all of die's faces map to numeric **values**.
          - sides: number of sides die has.
          - values: list of face values.
          - history: list of past-roll ``Result(face, value)`` records, empty until the
            first roll.

        Properties tracking the most recent roll (all read only, raise RuntimeError until
        ``roll()`` or any operator that implicitly rolls has been called):

          - result: (face, value) of the most recently rolled face.
          - face: face text of the most recently rolled face.
          - value: value of the most recently rolled face.

        Attributes:
          - name: free-text label (plain read/write attribute, default ''); shown by
            repr(), never parsed, independent of notation.

        Class attributes:
          - rng: Source of randomness shared by every Die instance; default is the
            ``random`` module. Assign e.g. ``die.Die.rng = random.Random(seed)`` to affect
            every die at once. Overridden per-instance by the ``rng`` constructor param;
            ``del obj.rng`` reverts an overridden die to the class-wide ``rng``.

        :param notation: Identifies Die of this type.
        :param faces: List of (text, value), one per face.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        :raises ValueError: If notation is empty/None or faces is empty.
        """
        if notation is None:
            raise ValueError('Invalid notation')
        self._notation = str(notation).strip()
        if not self._notation:
            raise ValueError('Invalid notation')
        self._faces = tuple(faces)
        if not self._faces:
            raise ValueError('Invalid faces')
        self._numeric = all(isinstance(v, numbers.Number) for v in self.values)
        if rng is not None:
            self.rng = rng
        # Description is not passed as parameter because it's likely to be dynamically set by
        # subclasses based on faces.
        faces_str = ','.join(f'"{x[0]}"={x[1]}' for x in self._faces)
        self._description = f'Die with {self.sides} faces [{faces_str}].'
        self._history = []
        self.name = ''

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.name or self.notation}, {self._faces})>'

    @property
    def numeric(self):
        """True if all of die's faces map to numeric values."""
        return self._numeric

    @property
    def notation(self):
        """Human readable expression of die."""
        return self._notation

    @property
    def description(self):
        """Textual description of die faces."""
        return self._description

    @property
    def sides(self):
        """Count of die faces."""
        return len(self._faces)

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
    def face(self):
        """Face text of the most recently rolled face."""
        self._check_rolled()
        return self._history[-1][0]

    @property
    def value(self):
        """Value of the most recently rolled face."""
        self._check_rolled()
        return self._history[-1][1]

    @property
    def result(self):
        """``Result(face, value)`` of the most recently rolled face."""
        self._check_rolled()
        return self._history[-1]

    def _roll_once(self):
        """Roll die once, appending (face, value) to history.

        :return: Value of roll.
        """
        item = self.rng.choice(self._faces)
        self._history.append(Result(*item))
        return item[1]

    def _negated(self):
        """New die with the same faces but negated values; notation sign-toggles ('d6'/'-d6')."""
        if self._notation.startswith('-'):
            notation = self._notation[1:]
        else:
            notation = f'-{self._notation}'
        spec = [(text, -value, 1) for text, value in self._faces]
        return NumericBased(notation, spec, self.__dict__.get('rng'))

    def _as_roll(self):
        """Lift this die into a single-die ``Roll``."""
        from .rolls import Roll  # noqa: PLC0415 (circular import: rolls imports Die)

        return Roll((self,))

    def plus(self, other):
        """Compose new Roll: this die's roll plus ``other`` (Die, Roll, or number)."""
        return self._as_roll().plus(other)

    def minus(self, other):
        """Compose new Roll: this die's roll minus ``other`` (Die, Roll, or number)."""
        return self._as_roll().minus(other)

    def times(self, other):
        """Compose new Roll: this die's roll multiplied by ``other`` (Die, Roll, or number)."""
        return self._as_roll().times(other)

    def div(self, other, rounding='half', ndigits=0):
        """Compose new Roll: this die's roll divided by ``other`` (Die, Roll, or number).

        Float division then rounding; see ``Roll.div`` for rounding/ndigits behavior.
        """
        return self._as_roll().div(other, rounding, ndigits)

    def mod(self, other):
        """Compose new Roll: this die's roll modulo ``other`` (Die, Roll, or number)."""
        return self._as_roll().mod(other)

    def keep_highest(self, n=1):
        """Compose new Roll keeping the ``n`` highest of this die's rolled values, summed."""
        return self._as_roll().keep_highest(n)

    def keep_lowest(self, n=1):
        """Compose new Roll keeping the ``n`` lowest of this die's rolled values, summed."""
        return self._as_roll().keep_lowest(n)

    def drop_highest(self, n=1):
        """Compose new Roll dropping the ``n`` highest of this die's values, summing the rest."""
        return self._as_roll().drop_highest(n)

    def drop_lowest(self, n=1):
        """Compose new Roll dropping the ``n`` lowest of this die's values, summing the rest."""
        return self._as_roll().drop_lowest(n)

    def successes(self, target):
        """Compose new Roll counting this die's rolled values >= ``target``."""
        return self._as_roll().successes(target)

    def failures(self, target):
        """Compose new Roll counting this die's rolled values <= ``target``."""
        return self._as_roll().failures(target)

    def chance(self, gte=None, lte=None):
        """Cumulative percentage (0.0-100.0) chance of a roll >= ``gte`` or <= ``lte``.

        Exactly one of ``gte``/``lte`` must be given. See ``Roll.chance``.
        """
        return self._as_roll().chance(gte, lte)


class NumericBased(Die):
    def __init__(self, notation, spec, rng=None):
        """Die with possibly non-numeric face texts, but each face has an associated numeric value.

        Fudge (www.fudgerpg.com) die::
            die.NumericBased('dF', (('+', 1, 2), ('', 0, 2), ('-', -1, 2)))

        :param notation: Identifies dice of this type.
        :param spec: List of tuples (facetext, value, count).
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        :raises ValueError: If spec is malformed or any value is non-numeric or count < 1.
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
            raise ValueError('Bad die specification') from None
        super().__init__(notation, faces, rng)
        faces_str = ','.join(f'"{x[0]}"={x[1]}' for x in self._faces)
        self._description = f'NumericBased die with {self.sides} faces, [{faces_str}].'


class Numeric(NumericBased):
    def __init__(self, notation, spec, rng=None):
        """Die with non-sequential, numeric faces, possibly repeating.

        A backgammon doubling die::
            die.Numeric('backgammon', (2, 4, 8, 16, 32, 64))

        :param notation: Uniquely identifies dice of this type.
        :param spec: List of numbers, one per face of die.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        :raises ValueError: If spec is not iterable of numbers.
        """
        try:
            faces = [(x, x, 1) for x in spec]
        except TypeError:
            raise ValueError('Bad die specification') from None
        super().__init__(notation, faces, rng)
        self._description = f'Numeric die with {self.sides} faces [{",".join(self.faces)}].'


class Constant(Numeric):
    def __init__(self, value, rng=None):
        """One-faced die that always rolls ``value``; never consumes randomness.

        The "2" in 'd6+2'::
            die.Constant(2)

        Composed and parsed numeric constants (``d6.plus(2)``, ``parse('d6+2')``) are
        ``Constant`` instances.

        :param value: Number the die always rolls; also its notation.
        :param rng: Source of randomness, accepted for signature consistency; never used.
        :raises ValueError: If value is not a number.
        """
        super().__init__(str(value), (value,), rng)
        self._description = f'Constant {value}.'

    def _roll_once(self):
        """Roll die once, appending (face, value) to history; no randomness involved.

        :return: Value of roll.
        """
        item = self._faces[0]
        self._history.append(Result(*item))
        return item[1]

    def _negated(self):
        """New ``Constant`` with negated value (base would degrade to ``NumericBased``)."""
        return Constant(-self._faces[0][1], self.__dict__.get('rng'))


class Standard(Numeric):
    def __init__(self, sides, rng=None):
        """Die with sequential, numeric faces.

        The common six sided die::
            die.Standard(6)

        :param sides: Number of faces die has, integral and > 0.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        :raises ValueError: If sides is not a positive integer.
        """

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


class Exploding(Standard):
    def __init__(
        self,
        sides,
        explode_range=1,
        explode_to=None,
        math_correct=False,
        explode_range_low=0,
        explode_to_low=None,
        rng=None,
    ):
        """Die that explodes: rolling into the explode range rolls ``explode_to`` again, recursing.

        A d6 that explodes on 6, rolling itself again::
            die.Exploding(6)

        Hackmaster style "math corrected" dice subtract one from every rolled-again value,
        and may explode down to a smaller die::

            die.Exploding(
                20, explode_to=die.Exploding(6, math_correct=True), math_correct=True,
            )

        Rolemaster style double-ended (open-ended) d100 explodes up on 96-100 (add) and down
            on 1-5 (subtract), recursively::
            die.Exploding(100, explode_range=5, explode_range_low=5)

        :param sides: Number of faces on die, integral and > 0.
        :param explode_range: [1] Explode when roll is > (sides - explode_range).
        :param explode_to: [None] ``Die`` rolled (recursively) again on explosion. ``None``
            means roll this die again.
        :param math_correct: [False] Subtract 1 from every rolled-again (not initial) value.
            Incompatible with ``explode_range_low``.
        :param explode_range_low: [0] Explode (subtracting) when roll is <= explode_range_low.
            ``0`` disables low-end explosion.
        :param explode_to_low: [None] ``Die`` rolled (recursively) again, and subtracted, on
            low-end explosion. ``None`` means roll this die again.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        :raises ValueError: If sides isn't an integer > 0; explode_to or explode_to_low isn't a
            Die or None; explode_range >= sides; explode_range_low < 0; explode_range and
            explode_range_low combined >= sides; or math_correct is True with
            explode_range_low > 0.
        """
        super().__init__(sides, rng)
        if explode_range >= self.sides:
            raise ValueError(f'explode_range must be < sides, got {explode_range} >= {self.sides}')
        if explode_range_low < 0:
            raise ValueError(f'explode_range_low must be >= 0, got {explode_range_low}')
        if explode_range + explode_range_low >= self.sides:
            raise ValueError(
                'explode_range and explode_range_low combined must be < sides, got '
                f'{explode_range} + {explode_range_low} >= {self.sides}',
            )
        if math_correct and explode_range_low > 0:
            raise ValueError('math_correct is not supported with low-end (double-ended) explosion')
        if explode_to is not None and not isinstance(explode_to, Die):
            raise ValueError(f'explode_to must be a Die instance or None, got {explode_to!r}')
        if explode_to_low is not None and not isinstance(explode_to_low, Die):
            raise ValueError(
                f'explode_to_low must be a Die instance or None, got {explode_to_low!r}',
            )
        if explode_to is None:
            explode_to = self
        if explode_to_low is None:
            explode_to_low = self
        self._explode_range = explode_range
        self._explode_to = explode_to
        self._math_correct = math_correct
        self._explode_range_low = explode_range_low
        self._explode_to_low = explode_to_low
        if math_correct:
            self._notation = f'd{self.sides}p'
            correction = ' (math corrected)'
        else:
            self._notation = f'd{self.sides}x'
            correction = ''
        self._description = (
            f'Exploding numeric die, {self.sides} faces numbered 1 through {self.sides}, '
            f'explodes past {self.sides - explode_range} rolling {explode_to.notation}{correction}'
        )
        if explode_range_low > 0:
            self._description += (
                f', and explodes at or below {explode_range_low} subtracting a roll of '
                f'{explode_to_low.notation}'
            )
        self._description += '.'

    def _roll_once(self):
        """Roll die; if roll is in the explode range, roll ``explode_to``/``explode_to_low`` again.

        ``result``/``face`` reflect the initial face rolled; ``value``/``result[1]`` reflect the
        total after any explosions (what this method returns).

        :return: Sum (or difference, on low-end explosion) of the initial roll and any explosions.
        """
        item = self.rng.choice(self._faces)
        value = item[1]
        # Explosions recurse through explode_to.roll(); when explode_to is this die, those
        # sub-rolls append to its own history. Discard them and record just the settled result,
        # so history keeps one (initial face, final value) entry per roll, matching result.
        start = len(self._history)
        if value <= self._explode_range_low:
            final = value - self._explode_to_low.roll()
        elif value + self._explode_range <= self.sides:
            final = value
        else:
            extra = self._explode_to.roll()
            if self._math_correct:
                extra -= 1
            final = value + extra
        del self._history[start:]
        self._history.append(Result(item[0], final))
        return final


class Rerolling(Standard):
    def __init__(self, sides, reroll_range=1, once=True, rng=None):
        """Die that rerolls low values: rolling into the reroll range rolls again.

        A d6 that rerolls 1s once, keeping the second roll (D&D Great Weapon Fighting)::
            die.Rerolling(6)

        A d6 that rerolls 1s and 2s until it rolls a 3 or better::
            die.Rerolling(6, reroll_range=2, once=False)

        Only the kept roll enters the roll history; rerolled-away values are discarded, so
        each ``roll()`` adds exactly one entry. ``die.Rerolling(6, reroll_range=2, once=False)``
        that rolls/rerolls 1, 2, 1, 5 keeps only 5 -- ``len(obj) == 1``, ``obj[-1]`` is ``5``,
        and ``obj.history[-1]`` is ``('5', 5)``.

        :param sides: Number of faces on die, integral and > 0.
        :param reroll_range: [1] Reroll when roll is <= reroll_range.
        :param once: [True] Reroll a single time, keeping the second roll even if it is
            also in the reroll range; False rerolls until the roll is out of the range.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        :raises ValueError: If sides isn't an integer > 0, or reroll_range isn't an integer
            with 1 <= reroll_range < sides.
        """
        super().__init__(sides, rng)
        try:
            valid = reroll_range == int(reroll_range) and 1 <= reroll_range < self.sides
        except TypeError, ValueError:
            valid = False
        if not valid:
            raise ValueError(
                f'reroll_range must be an integer, >= 1 and < sides, got {reroll_range!r}',
            )
        self._reroll_range = int(reroll_range)
        self._once = once
        suffix = 'r' if once else 'rr'
        self._notation = f'd{self.sides}{suffix}'
        if self._reroll_range > 1:
            self._notation += str(self._reroll_range)
        again = 'once' if once else 'until above it'
        self._description = (
            f'Rerolling numeric die, {self.sides} faces numbered 1 through {self.sides}, '
            f'rerolls at or below {self._reroll_range} {again}.'
        )

    def _roll_once(self):
        """Roll die; while roll is in the reroll range, roll again (once, or until out of it).

        Only the kept roll enters the history; rerolled-away values are discarded.

        :return: Value of the kept roll.
        """
        item = self.rng.choice(self._faces)
        while item[1] <= self._reroll_range:
            item = self.rng.choice(self._faces)
            if self._once:
                break
        self._history.append(Result(*item))
        return item[1]


class Symbolic(Die):
    def __init__(self, notation, spec, rng=None):
        """Die with "faces", and "values" that aren't necessarily numeric.

        A coin flip::
            die.Symbolic('coin', (('H', 'heads', 1), ('T', 'tails', 1)))

        :param notation: Uniquely identifies dice of this type.
        :param spec: die specification; list of tuples (face_text, face_value, count).
             face_value must be convertible into string but otherwise is free to get funky,
             count is number of faces with these text/value.
        :param rng: Source of randomness for this die only, overriding class-wide ``Die.rng``.
        :raises ValueError: If spec is malformed or any count < 1.
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
            raise ValueError('Bad die specification') from None
        super().__init__(notation, faces, rng)
        faces_str = ','.join(f'"{x[0]}"={x[1]}' for x in self._faces)
        self._description = f'Symbolic die with {self.sides} faces [{faces_str}].'

    @staticmethod
    def _scalar_or_list(values):
        if len(values) == 1:
            return values[0]
        return list(values)

    def roll(self, count=1, func=None):
        """Roll ``count`` times.

        When the die is numeric, behaves exactly like ``Die.roll()`` (``func`` defaults to
        ``sum``). When it isn't, ``func`` instead defaults to returning the single value at
        ``count=1``, or a list of values otherwise, since the values aren't summable.

        :param count: [1] Number of times to roll.
        :param func: [None] Applied to the list of ``count`` rolled values.
        :return: func applied to list of roll values.
        """
        if func is None:
            func = sum if self.numeric else self._scalar_or_list
        return super().roll(count, func)
