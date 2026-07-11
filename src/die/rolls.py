"""Group Die instances into a single roll."""

import itertools
import math
import numbers
import operator
from collections import Counter, namedtuple

from .die import Constant, Die, _Rollable

Odds = namedtuple('Odds', ('value', 'ways', 'probability'))
Rolled = namedtuple('Rolled', ('results', 'value'))

# Operator precedence of a Roll's notation, for parenthesizing composed notation.
_PREC_ADD = 1
_PREC_MUL = 2
_PREC_ATOM = 3


def _lift(other):
    """Coerce ``other`` (Roll, Die, or number) into a ``Roll``.

    Numbers become ``Constant`` dice and ride along in the composed Roll's dice list, so
    odds/roll-state machinery handles them uniformly; consequently ``Roll.dice``
    includes constants, e.g. ``parse('(d6*2+3)/d6').dice`` is (d6, 2, 3, d6).

    :raises TypeError: If other is not a Roll, Die, or number.
    """
    if isinstance(other, Roll):
        return other
    if isinstance(other, Die):
        lifted = Roll((other,))
    elif isinstance(other, numbers.Number):
        lifted = Roll((Constant(other),))
    else:
        raise TypeError(f"cannot compose Roll with '{type(other).__name__}'")
    lifted._prec = _PREC_ATOM
    return lifted


def _plain(die):
    """True when die's rolls come straight from its faces, so negating faces negates rolls.

    False for dice with custom roll behavior (e.g. Exploding). ``Constant`` overrides
    ``_roll_once`` only to skip the rng; it still rolls straight from its face.
    """
    return type(die)._roll_once in (Die._roll_once, Constant._roll_once)


def _rounded(value, rounding, ndigits):
    """Round ``value`` to ``ndigits`` decimal places (see ``Roll.div`` for full behavior)."""
    if ndigits is None:
        return value
    scale = 10**ndigits
    scaled = value * scale
    if rounding == 'up':
        result = math.ceil(scaled)
    elif rounding == 'down':
        result = math.floor(scaled)
    else:
        result = math.floor(scaled + 0.5)
    if ndigits:
        return result / scale
    return result


class Roll(_Rollable):
    def __init__(self, dice=(), func=sum, name=''):
        """Groups a set of Die instances into a single roll.

        Two six-sided dice, summed::
            die.Roll([die.Standard(6), die.Standard(6)])

        One six-sided die, multiplied by 2, composed from a ready-made die::
            die.d6.times(2)

        A Roll's dice are fixed at construction; there is no in-place mutation. To change the dice,
        compose a new Roll (``obj.plus(die)``) or rebuild one (``Roll(obj.dice + (die,))`` — but
        note that only carries over ``dice``, not ``func``/``name``, and a compose-built Roll
        rebuilt this way loses its operator structure, e.g. rebuilding a ``times(2)`` Roll yields
        a plain summed Roll).

        obj() and obj.roll(count, func ) both roll every die ``count`` times (default 1) and return
        the outer ``func`` (default ``sum``) applied to the list of ``count`` results, each of which
        is the constructor's ``func`` applied to that roll's individual die values.

        Roll retains every roll. Subscript it to reach older rolls' aggregate values
        (``obj[-1]`` is the most recent, matching ``value``, ``obj[0]`` the first); slicing and
        iteration (``for value in obj``, ``list(obj)``, ``sum(obj)``) yield them in roll order.
        The ``history`` property holds the full ``Rolled(results, value)`` namedtuples instead
        (``results`` the per-die (face, value) tuple, ``value`` the aggregate;
        ``history[-1]`` matches the ``results``/``value`` properties). Empty until the first
        roll, so ``obj[0]`` raises IndexError before then. ``len(obj)`` is the number of
        retained rolls; ``clear()`` empties the history.

        Compose methods ``plus``, ``minus``, ``times``, ``div``, ``mod`` (on ``Die`` too)
        each return a NEW Roll combining this roll with a Die, Roll, or number; chains bind
        tight, left to right::

            die.d6.times(2).plus(3).div(die.d6)  # ((d6*2)+3)/d6

        Keep/drop compose methods ``keep_highest``, ``keep_lowest``, ``drop_highest``,
        ``drop_lowest`` each return a NEW Roll over the same dice keeping/dropping the
        ``n`` (default 1) highest/lowest die values and summing the kept::

            die.parse('4d6').drop_lowest()   # 4d6dl, sum of the 3 highest
            die.d20.plus(die.d20).keep_highest()  # (d20+d20)kh, single highest

        Counting compose methods ``successes``, ``failures`` each return a NEW Roll over
        the same dice counting die values >= / <= a target (dice pools)::

            die.parse('6d10').successes(7)   # 6d10>=7, count of dice rolling 7+
            die.parse('6d10').failures(1)    # 6d10<=1, count of dice rolling 1

        ``chance`` (on ``Die`` too) reports the cumulative percentage (0.0-100.0) chance of
        a roll at or above / at or below a value; exactly one of ``gte``/``lte`` is given::

            die.parse('2d6').chance(gte=10)  # percent chance of rolling 10 or higher
            die.d20.chance(lte=5)            # percent chance of rolling 5 or lower

        Operators (every one rolls, same as ``Die``):
          - str(obj), int(obj), float(obj) roll all dice and return the coerced result.
          - +, -, *, /, //, %, ** roll all dice and use that result; they only reliably
            succeed when the Roll is numeric (``numeric`` is True when every die is).
          - >, >=, <, <=, ==, != also roll — equality included. Consequences: Roll are not
            hashable; comparing or sorting rolls gives unstable, unrepeatable results.
            Compare ``dice``/``notation`` for structural equality.

        Properties (all read only):
          - notation: dice notation derived from the Roll's contents; use this, not
            str(obj), for the notation text, since str(obj) rolls. For a plain summed Roll
            it is composed from the contained dice, grouped (e.g. '3d6+2'); for a Roll
            built by the compose methods it is the composed expression (e.g.
            '(d6*2+3)/d6'). ``'<unsupported>'`` when underivable: an empty Roll, or a
            constructor-supplied custom ``func``. When every die's notation is itself
            parseable, ``Roll.from_notation(obj.notation)`` recreates an equivalent Roll
            (same dice multiset and odds), with caveats: dice may be reordered by
            grouping, and dice with custom configuration behind a standard notation (e.g.
            ``Exploding`` with a custom ``explode_to``) are recreated with defaults.
          - description: textual description composed from the contained dice descriptions.
          - dice: tuple of ``Die`` instances in Roll.
          - numeric: [boolean] True if all Die in Roll can be numerically summed.
          - odds: list of ``Odds(value, ways, probability)``, one per distinct result.
          - history: list of past-roll ``Rolled(results, value)`` records, empty until the
            first roll.

        Attributes:
          - name: free-text label (plain read/write attribute, default ''); shown by
            repr(), never parsed, independent of notation.

        Properties tracking the most recent roll (all read only, raise RuntimeError until
        ``roll()``, or any operator that implicitly rolls has been called):

          - results: tuple of (face, value), one per die, from the most recent roll.
          - value: aggregated (``func``-applied) result of the most recent roll.

        Differences from ``Die``:
          - No ``faces``, ``values``, ``items``, or ``sides`` properties (all possible
            results); use ``dice`` (tuple of component ``Die`` instances) instead.
          - ``__init__`` does not raise on an empty/default ``dice=()``, unlike ``Die`` which
            requires at least one face.

        :param dice: List of dice this roll is composed of.
        :param func: [sum] Combines this roll's rolled dice values into one result, func([...]).
        :param name: [''] Free-text label.
        """
        self.name = name
        self._func = func
        # Immutable: dice never change after construction, so the derived notation, the
        # compose-stashed _notation, and the cached _odds can never go stale.
        self._dice = tuple(dice)
        self._notation = None
        self._odds = None
        self._history = []
        self._prec = None

    @classmethod
    def from_notation(cls, notation):
        """Create a ``Roll`` from standard dice notation.

        :param notation: Dice notation string, e.g. ``'3d6+2'``.
        :return: New ``Roll`` instance.
        :raises ValueError: If notation cannot be parsed.
        """
        from .notation import parse  # noqa: PLC0415 (circular import: notation imports Roll)

        return parse(notation)

    def __repr__(self):
        label = self.name or self.notation
        return f'<{self.__class__.__name__}({label}, {self._dice})>'

    @property
    def notation(self):
        """Dice notation derived from the Roll's contents; '<unsupported>' when underivable."""
        if self._notation is not None:
            return self._notation
        if self._func is not sum or not self._dice:
            return '<unsupported>'
        return self._group_notation()

    @property
    def description(self):
        """Textual description composed from the contained ``Die`` descriptions."""
        if not self._dice:
            return 'Roll of no dice.'
        bits = [f'{count} x {die.description.rstrip(".")}' for die, count in self._die_groups()]
        return f'Roll of {"; ".join(bits)}.'

    def _die_groups(self):
        """List of [die, count] pairs, consecutive-insensitive, grouped by identical dice.

        Identical means same faces AND same notation; the latter separates dice whose faces
        match but whose roll behavior differs (d6 vs exploding d6x vs penetrating d6p).
        """
        # Can't use Counter (Die is deliberately unhashable) nor ==/sorting (both roll).
        groups = list()
        for die in self._dice:
            for group in groups:
                if group[0] is die or (
                    group[0].notation == die.notation and group[0].items == die.items
                ):
                    group[1] += 1
                    break
            else:
                groups.append([die, 1])
        return groups

    def _operand(self):
        """(text, precedence) of this Roll when embedded in composed notation."""
        if self._prec is not None:
            prec = self._prec
        elif len(self._dice) <= 1:
            prec = _PREC_ATOM
        else:
            prec = _PREC_ADD
        if self._notation is not None:
            text = self._notation
        else:
            text = self._group_notation()
        return text, prec

    def _group_notation(self):
        """Parseable additive notation synthesized from dice, e.g. '3d6+2d4-1'.

        Negated dice (notation '-X') join with '-'; constants repeat ('2+2') rather than
        count-prefix ('22').
        """
        parts = list()
        for die, count in self._die_groups():
            text = die.notation
            sign = '+'
            if text.startswith('-'):
                sign = '-'
                text = text[1:]
            if count > 1 and isinstance(die, Constant):
                parts.extend([(sign, text)] * count)
            elif count > 1:
                parts.append((sign, f'{count}{text}'))
            else:
                parts.append((sign, text))
        if not parts:
            return '0'
        sign, text = parts[0]
        bits = [text if sign == '+' else f'-{text}']
        bits.extend(f'{sign}{text}' for sign, text in parts[1:])
        return ''.join(bits)

    @property
    def numeric(self):
        """True if all ``Die`` in Roll are numeric, and so can be numerically summed."""
        return all(die.numeric for die in self._dice)

    @property
    def dice(self):
        """Tuple of ``Die`` instances in Roll.

        Includes composed-in constants (``Constant`` dice): ``d6.plus(2).dice`` is (d6, 2).
        """
        return self._dice

    @property
    def odds(self):
        """List of ``Odds(value, ways, probability)``, one per distinct result.

        Computed from each die's face values, so odds are wrong for dice whose rolls
        don't come straight from their faces (``Exploding``, ``Rerolling``).
        """
        if self._odds is None:
            self._calc_odds()
        return self._odds

    def _calc_odds(self):
        """Calculate the absolute probability of every possible result."""
        if not self._dice:
            self._odds = []
            return
        counts = Counter(
            self._func(list(combo))
            for combo in itertools.product(*(die.values for die in self._dice))
        )
        total = counts.total()
        self._odds = sorted(Odds(value, ways, ways / total) for value, ways in counts.items())

    @property
    def value(self):
        """Aggregated (``func``-applied) result of the most recent roll."""
        self._check_rolled()
        return self._history[-1].value

    @property
    def results(self):
        """Tuple of (face, value), one per die, from the most recent roll."""
        self._check_rolled()
        return self._history[-1].results

    def _roll_once(self):
        """Roll all the dice once.

        :return: func (constructor param) applied to list of individual die roll values.
        """
        values = list()
        results = list()
        # Capture each die's result immediately: the same Die instance may appear more than
        # once in _dice (e.g. parse('3d6')), and result only reports its most recent roll.
        for die in self._dice:
            values.append(die.roll())
            results.append(die.result)
        value = self._func(values)
        self._history.append(Rolled(tuple(results), value))
        return value

    def _binop_notation(self, other, symbol, prec, right_tight):
        """Notation of ``self symbol other``, parenthesizing operands that bind looser.

        right_tight parenthesizes an equal-precedence right operand, for non-associative
        operators (-, /, //, %, and * over rounded division).
        """
        left, left_prec = self._operand()
        right, right_prec = other._operand()
        if left_prec < prec:
            left = f'({left})'
        if right_prec < prec or (right_tight and right_prec == prec):
            right = f'({right})'
        return f'{left}{symbol}{right}'

    def _merge_sum(self, dice):
        """New summed Roll of this roll's dice plus ``dice``; notation derives from the dice."""
        result = Roll(list(self._dice) + list(dice))
        result._prec = _PREC_ADD
        return result

    def _wrap(self, other, op, notation, prec):
        """New Roll of both rolls' dice whose func applies ``op`` to the two rolls' results."""
        left_func = self._func
        right_func = other._func
        split = len(self._dice)

        def func(values):
            return op(left_func(values[:split]), right_func(values[split:]))

        result = Roll(list(self._dice) + list(other._dice), func=func)
        result._notation = notation
        result._prec = prec
        return result

    def _negated(self):
        """New Roll whose result is the negation of this roll's result."""
        text, prec = self._operand()
        if prec < _PREC_ATOM:
            text = f'({text})'
        notation = f'-{text}'
        if self._func is sum and self.numeric and all(_plain(d) for d in self._dice):
            result = Roll([d._negated() for d in self._dice])
        else:
            inner = self._func

            def func(values):
                return -inner(values)

            result = Roll(list(self._dice), func=func)
        result._notation = notation
        result._prec = _PREC_ATOM
        return result

    def plus(self, other):
        """Compose new Roll: this roll's result plus ``other``'s.

        :param other: Die, Roll, or number.
        :return: New ``Roll``; neither operand is modified.
        :raises TypeError: If other is not a Die, Roll, or number.
        """
        if isinstance(other, numbers.Number) and other < 0:
            return self.minus(-other)
        other = _lift(other)
        if self._func is sum and other._func is sum:
            return self._merge_sum(other._dice)
        notation = self._binop_notation(other, '+', _PREC_ADD, right_tight=False)
        return self._wrap(other, operator.add, notation, _PREC_ADD)

    def minus(self, other):
        """Compose new Roll: this roll's result minus ``other``'s.

        :param other: Die, Roll, or number.
        :return: New ``Roll``; neither operand is modified.
        :raises TypeError: If other is not a Die, Roll, or number.
        """
        if isinstance(other, numbers.Number) and other < 0:
            return self.plus(-other)
        other = _lift(other)
        if (
            self._func is sum
            and other._func is sum
            and other.numeric
            and all(_plain(d) for d in other._dice)
        ):
            return self._merge_sum([d._negated() for d in other._dice])
        notation = self._binop_notation(other, '-', _PREC_ADD, right_tight=True)
        return self._wrap(other, operator.sub, notation, _PREC_ADD)

    def times(self, other):
        """Compose new Roll: this roll's result multiplied by ``other``'s.

        :param other: Die, Roll, or number.
        :return: New ``Roll``; neither operand is modified.
        :raises TypeError: If other is not a Die, Roll, or number.
        """
        other = _lift(other)
        notation = self._binop_notation(other, '*', _PREC_MUL, right_tight=True)
        return self._wrap(other, operator.mul, notation, _PREC_MUL)

    def div(self, other, rounding='half', ndigits=0):
        """Compose new Roll: this roll's result divided by ``other``'s, then rounded.

        Division is float (true) division; the quotient is then rounded to ``ndigits``
        decimal places per ``rounding``:

          - ``'half'`` (default): round half up. Fractions of exactly .5 round toward
            positive infinity (2.5 -> 3, -2.5 -> -2); everything else rounds to nearest.
          - ``'up'``: fractions round up; quotient is ceiled at ``ndigits`` places
            (2.01 -> 3, -2.99 -> -2 at ndigits=0).
          - ``'down'``: fractions round down; quotient is floored at ``ndigits`` places
            (2.99 -> 2, -2.01 -> -3 at ndigits=0). ``div(x, rounding='down')`` is floor
            (//) division.

        With ``ndigits=0`` (the default) results are ints; with ``ndigits > 0``, floats
        rounded to that many decimal places. ``ndigits=None`` skips rounding entirely and
        results are raw float quotients (``rounding`` is then meaningless and raises).

        :param other: Die, Roll, or number.
        :param rounding: ['half'] How fractions round: 'half', 'up', or 'down'.
        :param ndigits: [0] Decimal places rounded to; None for no rounding.
        :return: New ``Roll``; neither operand is modified.
        :raises TypeError: If other is not a Die, Roll, or number.
        :raises ValueError: If rounding is not 'half', 'up', or 'down'; rounding is not
            'half' with ndigits=None; or ndigits is not None or a non-negative integer.
        """
        if rounding not in ('half', 'up', 'down'):
            raise ValueError(f"rounding must be 'half', 'up', or 'down', got {rounding!r}")
        if ndigits is None:
            if rounding != 'half':
                raise ValueError(
                    "ndigits=None skips rounding, incompatible with rounding='up'/'down'",
                )
        else:
            try:
                valid = ndigits == int(ndigits) and ndigits >= 0
            except TypeError, ValueError:
                valid = False
            if not valid:
                raise ValueError(f'ndigits must be a non-negative integer or None, got {ndigits!r}')
            ndigits = int(ndigits)
        other = _lift(other)
        if rounding == 'down' and ndigits == 0:
            symbol = '//'
        else:
            symbol = '/'
        notation = self._binop_notation(other, symbol, _PREC_MUL, right_tight=True)

        def op(left, right):
            return _rounded(left / right, rounding, ndigits)

        return self._wrap(other, op, notation, _PREC_MUL)

    def mod(self, other):
        """Compose new Roll: this roll's result modulo ``other``'s.

        :param other: Die, Roll, or number.
        :return: New ``Roll``; neither operand is modified.
        :raises TypeError: If other is not a Die, Roll, or number.
        """
        other = _lift(other)
        notation = self._binop_notation(other, '%', _PREC_MUL, right_tight=True)
        return self._wrap(other, operator.mod, notation, _PREC_MUL)

    def _keep_drop(self, suffix, n):
        """New Roll over the same dice, keep/drop the ``n`` highest/lowest values, sum the kept."""
        if not self.numeric:
            raise TypeError('cannot keep/drop on a non-numeric Roll')
        if self._func is not sum:
            raise TypeError('keep/drop requires a plain summed Roll')
        try:
            valid = n == int(n) and n >= 1
        except TypeError, ValueError:
            valid = False
        if not valid:
            raise ValueError(f'n must be a positive integer, got {n!r}')
        n = int(n)
        count = len(self._dice)
        if suffix in ('kh', 'kl') and n > count:
            raise ValueError(f'cannot keep {n} of {count} dice')
        if suffix in ('dh', 'dl') and n >= count:
            raise ValueError(f'cannot drop {n} of {count} dice')
        if suffix == 'kh':
            kept = slice(count - n, None)
        elif suffix == 'kl':
            kept = slice(None, n)
        elif suffix == 'dh':
            kept = slice(None, count - n)
        else:
            kept = slice(n, None)

        def func(values):
            return sum(sorted(values)[kept])

        text, prec = self._operand()
        if prec < _PREC_ATOM:
            text = f'({text})'
        notation = f'{text}{suffix}'
        if n > 1:
            notation = f'{notation}{n}'
        result = Roll(list(self._dice), func=func)
        result._notation = notation
        result._prec = _PREC_ATOM
        return result

    def keep_highest(self, n=1):
        """Compose new Roll: the ``n`` highest of this roll's die values, summed.

        ``results`` of the new Roll still reports every die; ``value`` is the
        kept sum.

        :param n: [1] Number of dice kept.
        :return: New ``Roll``; this roll is not modified.
        :raises TypeError: If Roll is non-numeric or not a plain summed pool.
        :raises ValueError: If n is not a positive integer or exceeds the number of dice.
        """
        return self._keep_drop('kh', n)

    def keep_lowest(self, n=1):
        """Compose new Roll: the ``n`` lowest of this roll's die values, summed.

        ``results`` of the new Roll still reports every die; ``value`` is the
        kept sum.

        :param n: [1] Number of dice kept.
        :return: New ``Roll``; this roll is not modified.
        :raises TypeError: If Roll is non-numeric or not a plain summed pool.
        :raises ValueError: If n is not a positive integer or exceeds the number of dice.
        """
        return self._keep_drop('kl', n)

    def drop_highest(self, n=1):
        """Compose new Roll: this roll's die values with the ``n`` highest dropped, summed.

        ``results`` of the new Roll still reports every die; ``value`` is the
        kept sum.

        :param n: [1] Number of dice dropped.
        :return: New ``Roll``; this roll is not modified.
        :raises TypeError: If Roll is non-numeric or not a plain summed pool.
        :raises ValueError: If n is not a positive integer or not fewer than the number of dice.
        """
        return self._keep_drop('dh', n)

    def drop_lowest(self, n=1):
        """Compose new Roll: this roll's die values with the ``n`` lowest dropped, summed.

        ``results`` of the new Roll still reports every die; ``value`` is the
        kept sum.

        :param n: [1] Number of dice dropped.
        :return: New ``Roll``; this roll is not modified.
        :raises TypeError: If Roll is non-numeric or not a plain summed pool.
        :raises ValueError: If n is not a positive integer or not fewer than the number of dice.
        """
        return self._keep_drop('dl', n)

    def _count_test(self, symbol, target, test):
        """New Roll over the same dice whose result counts die values passing ``test``."""
        if not self.numeric:
            raise TypeError('cannot count successes/failures on a non-numeric Roll')
        if self._func is not sum:
            raise TypeError('success/failure counting requires a plain summed Roll')
        if not isinstance(target, numbers.Number):
            raise TypeError(f'target must be a number, got {target!r}')

        def func(values):
            return sum(1 for value in values if test(value))

        text, prec = self._operand()
        if prec < _PREC_ATOM:
            text = f'({text})'
        result = Roll(list(self._dice), func=func)
        result._notation = f'{text}{symbol}{target}'
        result._prec = _PREC_ATOM
        return result

    def successes(self, target):
        """Compose new Roll: how many of this roll's die values are >= ``target``.

        The success-counting dice pool of World of Darkness, Shadowrun, and kin.
        ``results`` of the new Roll still reports every die; ``value`` is the count.

        :param target: Number a die value must equal or exceed to count.
        :return: New ``Roll``; this roll is not modified.
        :raises TypeError: If Roll is non-numeric, not a plain summed pool, or target is
            not a number.
        """
        return self._count_test('>=', target, lambda value: value >= target)

    def failures(self, target):
        """Compose new Roll: how many of this roll's die values are <= ``target``.

        Counterpart of ``successes`` for counting botches/failures.
        ``results`` of the new Roll still reports every die; ``value`` is the count.

        :param target: Number a die value must equal or fall below to count.
        :return: New ``Roll``; this roll is not modified.
        :raises TypeError: If Roll is non-numeric, not a plain summed pool, or target is
            not a number.
        """
        return self._count_test('<=', target, lambda value: value <= target)

    def chance(self, gte=None, lte=None):
        """Cumulative percentage (0.0-100.0) chance of a roll at or beyond a bound.

        Exactly one of ``gte``/``lte`` must be given: ``gte`` is the chance of rolling that
        value or higher, ``lte`` that value or lower. Computed from ``odds``, so it carries
        the same caveat: probabilities come from the dice's face values and are wrong for
        dice whose rolls don't (``Exploding``, ``Rerolling``). An empty Roll has no
        outcomes, so its chance is 0.0.

        :param gte: Chance a roll is >= this value ("value or higher").
        :param lte: Chance a roll is <= this value ("value or lower").
        :return: Percentage, a float in 0.0-100.0.
        :raises ValueError: If neither or both of gte/lte are given.
        :raises TypeError: If the given bound is not a number, or the Roll is non-numeric.
        """
        if (gte is None) == (lte is None):
            raise ValueError('exactly one of gte, lte must be given')
        bound = gte if gte is not None else lte
        if not isinstance(bound, numbers.Number):
            raise TypeError(f'bound must be a number, got {bound!r}')
        if not self.numeric:
            raise TypeError('cannot compute chance on a non-numeric Roll')
        if gte is not None:
            total = sum(o.probability for o in self.odds if o.value >= gte)
        else:
            total = sum(o.probability for o in self.odds if o.value <= lte)
        return total * 100
