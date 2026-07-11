"""Parse standard dice notation into ``Roll`` objects."""

import re

from .die import Constant, Exploding, NumericBased, Rerolling, Standard
from .rolls import _PREC_ATOM, Roll

_token = re.compile(
    r'(\d*)[dD](\d+|[fF])([xXpP]|[rR]{1,2}\d*)?|([dDkK][hHlL])(\d*)|(\d+)|(//|>=|<=|[-+*/%()])',
)


def _fudge_die(rng):
    return NumericBased('dF', (('+', 1, 2), (' ', 0, 2), ('-', -1, 2)), rng)


def _tokenize(notation, text):
    tokens = list()
    pos = 0
    while pos < len(text):
        if text[pos].isspace():
            pos += 1
            continue
        match = _token.match(text, pos)
        if match is None:
            raise ValueError(f'Bad dice notation: {notation!r}')
        count, sides, explode, suffix, suffix_count, constant, op = match.groups()
        if sides is not None:
            tokens.append(('die', count, sides, explode))
        elif suffix is not None:
            tokens.append(('suffix', suffix.lower(), suffix_count))
        elif constant is not None:
            tokens.append(('int', int(constant)))
        else:
            tokens.append((op,))
        pos = match.end()
    return tokens


class _Parser:
    def __init__(self, notation, tokens, rng):
        """Recursive descent over tokens, standard operator precedence.

        expr := term (('+' | '-') term)*
        term := unary (('*' | '/' | '//' | '%') unary)*
        unary := ('+' | '-')? atom
        atom := primary (SUFFIX)*
        primary := NdS | NdF | integer | '(' expr ')'
        NdS := N? 'd' sides ('x' | 'p' | 'r' integer? | 'rr' integer?)?
        SUFFIX := ('kh' | 'kl' | 'dh' | 'dl') integer? | ('>=' | '<=') integer
        """
        self.notation = notation
        self.tokens = tokens
        self.pos = 0
        self.rng = rng

    def bad(self):
        return ValueError(f'Bad dice notation: {self.notation!r}')

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def take(self):
        token = self.peek()
        if token is None:
            raise self.bad()
        self.pos += 1
        return token

    def expr(self):
        roll = self.term()
        while True:
            token = self.peek()
            if token is None or token[0] not in ('+', '-'):
                return roll
            self.pos += 1
            if token[0] == '+':
                roll = roll.plus(self.term())
            else:
                roll = roll.minus(self.term())

    def term(self):
        roll = self.unary()
        while True:
            token = self.peek()
            if token is None or token[0] not in ('*', '/', '//', '%'):
                return roll
            self.pos += 1
            operand = self.unary()
            if token[0] == '*':
                roll = roll.times(operand)
            elif token[0] == '/':
                roll = roll.div(operand)
            elif token[0] == '//':
                roll = roll.div(operand, rounding='down')
            else:
                roll = roll.mod(operand)

    def unary(self):
        token = self.peek()
        if token is not None and token[0] == '+':
            self.pos += 1
            return self.atom()
        if token is not None and token[0] == '-':
            self.pos += 1
            nxt = self.peek()
            if nxt is not None and nxt[0] == 'int':
                self.pos += 1
                return self.constant(-nxt[1])
            return self.atom()._negated()
        return self.atom()

    def atom(self):
        roll = self.primary()
        while True:
            token = self.peek()
            if token is None:
                return roll
            if token[0] == 'suffix':
                self.pos += 1
                _, suffix, count = token
                if count:
                    n = int(count)
                else:
                    n = 1
                methods = {
                    'kh': roll.keep_highest,
                    'kl': roll.keep_lowest,
                    'dh': roll.drop_highest,
                    'dl': roll.drop_lowest,
                }
                try:
                    roll = methods[suffix](n)
                except TypeError, ValueError:
                    raise self.bad() from None
            elif token[0] in ('>=', '<='):
                self.pos += 1
                target = self.peek()
                if target is None or target[0] != 'int':
                    raise self.bad()
                self.pos += 1
                if token[0] == '>=':
                    method = roll.successes
                else:
                    method = roll.failures
                try:
                    roll = method(target[1])
                except TypeError:
                    raise self.bad() from None
            else:
                return roll

    def primary(self):
        token = self.take()
        kind = token[0]
        if kind == '(':
            roll = self.expr()
            if self.take()[0] != ')':
                raise self.bad()
            return roll
        if kind == 'die':
            return self.dice(token)
        if kind == 'int':
            return self.constant(token[1])
        raise self.bad()

    def constant(self, value):
        roll = Roll((Constant(value, self.rng),))
        roll._prec = _PREC_ATOM
        return roll

    def dice(self, token):
        _, count, sides, explode = token
        if count:
            count = int(count)
        else:
            count = 1
        if count < 1:
            raise self.bad()
        if sides in ('f', 'F'):
            if explode:
                raise self.bad()
            die = _fudge_die(self.rng)
        else:
            sides = int(sides)
            if sides < 1:
                raise self.bad()
            explode = (explode or '').lower()
            try:
                if explode == 'x':
                    die = Exploding(sides, rng=self.rng)
                elif explode == 'p':
                    die = Exploding(sides, math_correct=True, rng=self.rng)
                elif explode.startswith('rr'):
                    die = Rerolling(sides, int(explode[2:] or 1), once=False, rng=self.rng)
                elif explode.startswith('r'):
                    die = Rerolling(sides, int(explode[1:] or 1), rng=self.rng)
                else:
                    die = Standard(sides, self.rng)
            except ValueError:
                raise self.bad() from None
        roll = Roll([die] * count)
        roll._prec = _PREC_ATOM
        return roll


def parse(notation, rng=None):
    """Parse dice notation into a ``Roll`` instance.

    Notation is arithmetic over dice terms with standard operator precedence: ``*``, ``/``,
    ``//``, ``%`` bind tighter than ``+``, ``-``; parentheses override. A term is ``NdS``
    (N S-sided dice), ``NdF`` (N Fudge dice), or an integer constant. ``NdS`` may carry an
    ``x`` (exploding) or ``p`` (penetrating) suffix, building an ``Exploding`` instead of
    ``Standard``, or an ``r`` (reroll once) or ``rr`` (reroll until out of range) suffix
    with optional range (default 1), building a ``Rerolling``; none are valid on Fudge
    dice. A keep/drop suffix ``kh``, ``kl``, ``dh``, ``dl`` with optional count (default 1)
    may follow a dice term or parenthesized group, keeping/dropping the N highest/lowest
    die values and summing the kept. A counting suffix ``>=N`` or ``<=N`` may likewise
    follow, counting die values >= / <= N (``successes``/``failures``) instead of summing.
    Suffixes bind tightest::

        parse('3d6')
        parse('2d10+5')
        parse('3d6+2d4-1')
        parse('(d6*2+3)/d6')
        parse('4d6dl')     # 4d6 drop lowest
        parse('2d20kh')    # 2d20 keep highest
        parse('(3d6+2d4)kh2')
        parse('d6x')       # exploding d6
        parse('3d6p')      # three penetrating (Hackmaster math-corrected) d6, summed
        parse('4d6xkh3')   # four exploding d6, keep highest 3
        parse('4d6r')      # four d6, each rerolling 1s once
        parse('d10rr2')    # d10, rerolling 1s and 2s until it rolls 3+
        parse('6d10>=7')   # six d10, count of dice rolling 7 or higher
        parse('6d10<=1')   # six d10, count of dice rolling 1

    ``/`` is ``Roll.div()`` with defaults (float division rounded half up to an int);
    ``//`` is ``Roll.div(rounding='down')`` (floor division). ``d`` and ``f`` are
    case-insensitive,
    whitespace is tolerated. The result is built with the ``Roll`` compose methods, so it is
    identical to the equivalent method chain, e.g. ``parse('(d6*2+3)/d6')`` and
    ``d6.times(2).plus(3).div(d6)``.

    :param notation: Dice notation string.
    :param rng: Source of randomness given to created dice, overriding class-wide ``Die.rng``.
    :return: ``Roll`` whose ``notation`` is the normalized notation string.
    :raises ValueError: If notation cannot be parsed.
    """
    try:
        text = notation.strip()
    except AttributeError:
        raise ValueError(f'Bad dice notation: {notation!r}') from None
    parser = _Parser(notation, _tokenize(notation, text), rng)
    if parser.peek() is None:
        raise parser.bad()
    roll = parser.expr()
    if parser.peek() is not None:
        raise parser.bad()
    return roll


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
