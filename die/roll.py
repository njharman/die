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

from collections import defaultdict


class Roll(object):
    '''Groups a set of die instances into a single roll.'''
    def __init__(self, dice=(), name=''):
        ''':param dice: list of dice this roll is composed of'''
        self.name = name
        self._dice = list()
        self._odds = None
        for d in dice:
            self.add_die(d)

    def __str__(self):
        return self.name or self.description

    def __call__(self, *args, **kwargs):
        return self.roll(*args, **kwargs)

    @property
    def description(self):
        dice = defaultdict(int)
        for die in self._dice:
            dice[die] += 1
        bits = ['%i%s' % (v[1], v[0]) for v in dice.items()]
        return '%s Roll' % (', '.join(bits))

    @property
    def dice(self):
        '''List of ``Die`` in Roll.'''
        return self._dice[:]

    @property
    def summable(self):
        '''True if all ``Die`` in Roll can be numerically added.'''
        for die in self._dice:
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
        :param die: Die instance
        :param count: number of times die is rolled
        '''
        for x in range(count):
            self._dice.append(die)
        self._odds = None

    def remove_die(self, die):
        '''Remove ``Die`` (first matching) from Roll.
        :param die: Die instance
        '''
        if die in self._dice:
            self._dice.remove(die)

    def roll(self, count=0, func=sum):
        '''Roll some dice!
        :param count: [0] Return list of sums
        :param func: [sum] Apply func to list of individual die rolls func([])
        :return: A single sum or list of ``count`` sums
        '''
        if count:
            return [func([die.roll() for die in self._dice]) for x in range(0, count)]
        else:
            return func([die.roll() for die in self._dice])

    def x_rolls(self, number, count=0, func=sum):
        '''Iterator of number dice rolls.
        :param count: [0] Return list of ``count`` sums
        :param func: [sum] Apply func to list of individual die rolls func([])
        '''
        for x in range(number):
            yield self.roll(count, func)

    def iter(self, count=0, func=sum):
        '''Iterator of infinite dice rolls.
        :param count: [0] Return list of ``count`` sums
        :param func: [sum] Apply func to list of individual die rolls func([])
        '''
        while True:
            yield self.roll(count, func)

    def _calc_odds(self):
        '''Calculates the absolute probability of all posible rolls.'''
        def recur(val, h, dice, combinations):
            for pip in dice[0]:
                tot = val + pip
                if len(dice) > 1:
                    combinations = recur(tot, h, dice[1:], combinations)
                else:
                    combinations += 1
                    h[tot] = h.get(tot, 0) + 1
            return combinations
        if self.summable:
            start = 0
        else:
            start = ''
        h = dict()
        funky = [d.values for d in self._dice]
        # count of possible results of rolling dice
        combinations = recur(start, h, funky, 0.0)
        self._odds = [(roll, h[roll], h[roll] / combinations) for roll in h.keys()]
        self._odds.sort()


class FuncRoll(Roll):
    '''Apply func to roll.'''
    def __init__(self, func, dice=(), name=''):
        '''
        :param func: Apply func to list of individual die rolls func([])
        '''
        self._func = func
        super(FuncRoll, self).__init__(dice, name)

    def roll(self, count=0):
        '''Roll some dice!
        :param count: [0] Return list of sums
        :return: A single sum or list of ``count`` sums
        '''
        return super(FuncRoll, self).roll(count, self._func)

    def x_rolls(self, number, count=0):
        '''Iterator of number dice rolls.
        :param count: [0] Return list of ``count`` sums
        '''
        for x in range(number):
            yield super(FuncRoll, self).roll(count, self._func)

    def iter(self, count=0):
        '''Iterator of infinite dice rolls.
        :param count: [0] Return list of ``count`` sums
        '''
        while True:
            yield super(FuncRoll, self).roll(count, self._func)
