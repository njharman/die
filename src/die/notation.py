"""Parse standard dice notation into ``Roll`` objects."""

import re

from .die import Numeric, NumericBased, Standard
from .rolls import Roll

_term = re.compile(r'\s*([+-])?\s*(?:(\d*)[dD](\d+|[fF])|(\d+))\s*')


def _fudge_die(negate, rng):
    if negate:
        spec = (('+', -1, 2), (' ', 0, 2), ('-', 1, 2))
    else:
        spec = (('+', 1, 2), (' ', 0, 2), ('-', -1, 2))
    return NumericBased('dF', spec, rng)


def parse(notation, rng=None):
    """Parse dice notation into a ``Roll`` instance.

    Notation is terms joined by ``+`` or ``-``. A term is ``NdS`` (N S-sided
    dice), ``NdF`` (N Fudge dice), or an integer constant::

        parse('3d6')
        parse('2d10+5')
        parse('d20')
        parse('4dF')
        parse('3d6+2d4-1')

    ``d`` and ``f`` are case-insensitive, whitespace is tolerated.

    :param notation: Dice notation string.
    :param rng: Source of randomness given to created dice, overriding class-wide ``Die.rng``.
    :return: ``Roll`` named with the normalized notation.
    :raises ValueError: If notation cannot be parsed.
    """
    try:
        text = notation.strip()
    except AttributeError:
        raise ValueError(f'Bad dice notation: {notation!r}') from None
    dice = list()
    parts = list()
    pos = 0
    while pos < len(text):
        match = _term.match(text, pos)
        if match is None or (pos > 0 and match.group(1) is None):
            raise ValueError(f'Bad dice notation: {notation!r}')
        sign, count, sides, constant = match.groups()
        negate = sign == '-'
        if negate:
            op = '-'
        else:
            op = '+'
        if constant is not None:
            value = int(constant)
            if negate:
                value = -value
            dice.append(Numeric(str(value), (value,), rng))
            parts.append(f'{op}{int(constant)}')
        else:
            if count:
                count = int(count)
            else:
                count = 1
            if count < 1:
                raise ValueError(f'Bad dice notation: {notation!r}')
            if sides in ('f', 'F'):
                die = _fudge_die(negate, rng)
                label = 'dF'
            else:
                sides = int(sides)
                if sides < 1:
                    raise ValueError(f'Bad dice notation: {notation!r}')
                if negate:
                    die = Numeric(f'd{sides}', [-x for x in range(1, sides + 1)], rng)
                else:
                    die = Standard(sides, rng)
                label = f'd{sides}'
            if count > 1:
                label = f'{count}{label}'
            parts.append(f'{op}{label}')
            dice.extend(die for _ in range(count))
        pos = match.end()
    if not dice:
        raise ValueError(f'Bad dice notation: {notation!r}')
    name = ''.join(parts).removeprefix('+')
    return Roll(dice, name=name)


def roll(notation, rng=None):
    """Parse dice notation, roll it once.

    Convenience for ``parse(notation).roll()``; parsing anew each call, prefer
    ``parse()`` when making the same roll repeatedly.

    :param notation: Dice notation string, e.g. ``'3d6+2'``.
    :param rng: Source of randomness given to created dice, overriding class-wide ``Die.rng``.
    :return: Result of the roll.
    :raises ValueError: If notation cannot be parsed.
    """
    return parse(notation, rng).roll()
