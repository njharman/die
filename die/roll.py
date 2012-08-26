__copyright__ = '''Copyright (c) 2003-4,2012 Norman J. Harman Jr.'''
__license__ = '''This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA'''
__doc__ = '''%(name)s

%(copyright)s
%(license)s
''' % {'name': __name__, 'copyright': __copyright__, 'license': __license__}


class Roll(object):
    '''Groups a set of die instances into a single roll.'''
    def __init__(self, dice=None):
        '''@param dice: list of dice this roll is composed of'''
        self._name = ''
        self._dice = dict()
        self._odds = None
        if dice is not None:
            for d in dice:
                self.add_die(d)

    def __str__(self):
        return self.description

    name = property(
            lambda s: s._name,
            lambda s, v: setattr(s, '_name', v),
            )

    @property
    def description(self):
        bits = ['%i%s' % (v[0], v[1]) for v in self._dice.values()]
        return '%s Roll' % (', '.join(bits))

    @property
    def dice(self):
        '''List of ``Die`` in Roll.'''
        l = list()
        for count, die in self._dice.values():
            for i in range(count):
                l.append(die)
        return l

    @property
    def summable(self):
        '''True if all ``Die`` in Roll can be numerically added.'''
        for count, die in self._dice.values():
            if not die.numeric:
                return False
        return True

    @property
    def odds(self):
        '''Odd Structure.'''
        if self._odds is None:
            self._calc_odds()
        return self._odds

    def add_die(self, die, count=1):
        '''Add ``Die`` to Roll.
        @param die: Die instance
        @param count: number of times die is rolled
        '''
        roll = self._dice.setdefault(str(die), [0, die])
        roll[0] += count
        self._odds = None

    def remove_die(self, die):
        '''Remove ``Die`` (first matching) from Roll.
        @param die: Die instance
        '''
        roll = self._dice.get(str(die), [40, 'dummy'])
        roll[0] -= 1
        if roll[0] == 0:
            del self._dice[str(die)]
        self._odds = None

    def roll_values(self):
        '''@return: List of individual Die rolls.'''
        l = list()
        for count, die in self._dice.values():
            l.extend(die.rolls(count))
        return l

    def roll_total(self):
        '@return: Sum of rolling Dice.'
        return sum(self.roll_values())

    def roll_totalX(self, count):
        '''
        @param count: Number of rolls to make.
        @return: List of count dice rolls, one sum per roll.
        '''
        # some lameness for supposed speed (unprofiled)
        dice = list(self._dice.values())
        if len(dice) == 1:
            rolls, die = dice[0]
            if rolls == 1:
                oneroll = lambda: die.roll()
            else:
                oneroll = lambda: sum(die.rolls(rolls))
        else:
            oneroll = self.roll_total
        return [oneroll() for x in range(0, count)]

    def roll_totalGenerator(self):
        '''
        @return: generator that will produce roll_total forever
        '''
        def generator():
            yield self.roll_total()
        return generator

    def _calc_odds(self):
        '''Calculates the absolute probability of all posible rolls.'''
        def recur(val, h, dice, combinations):
            for pip in dice[0]:
                tot = val + pip
                if len(dice) > 1:
                    combinations = recur(tot, h, dice[1:], combinations)
                else:
                    combinations += 1
                    count = h.get(tot, 0)
                    h[tot] = count + 1
            return combinations
        if self.summable:
            start = 0
        else:
            start = ''
        h = dict()
        dice = list()
        for (count, die) in self._dice.values():
            for i in range(0, count):
                dice.append(die.values)
        combinations = recur(start, h, dice, 0.0)
        self._odds = [(x, h[x], h[x] / combinations) for x in h.keys()]
        self._odds.sort()
