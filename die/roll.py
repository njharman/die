__copyright__="Copyright (c) 2003 Norman J. Harman Jr."
__license__="""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""
__doc__ = """%(name)s
 
%(copyright)s
%(license)s
""" % {'name':__name__, 'copyright':__copyright__, 'license':__license__} 


class Roll(object):
    """
    Groups a set of die instances into a single roll
    """
    def __init__(self, dice=None):
        """@param dice: list of dice this roll is composed of"""
        object.__init__(self)
        self._name = ""
        self._dice = dict()
        self._odds = None
        if dice is not None:
            map(self.add_die, dice)

    def __str__(self):
        return self.description

    name = property(lambda s: s._name, lambda s, v: setattr(s,'_name', v), doc="Name of this roll")

    def _prop_get_description(self):
        return "%s Roll" % (', '.join( ["%i%s" % (v[0], v[1]) for v in self._dice.values()]))
    description = property(_prop_get_description, doc="longish description of roll")

    def _prop_get_dice(self):
        l = []
        for count, die in self._dice.values():
            for i in range(count):
                l.append(die)
        return l
    dice = property(_prop_get_dice, doc="list of dice")

    def _prop_get_summable(self):
        for (count, die) in self._dice.values():
            if not die.numeric:
                return False
        return True
    summable = property(_prop_get_summable, doc="True if all dice can be numerically added")

    def _prop_get_odds(self):
        if self._odds is None:
            self._calcOdds()
        return self._odds
    odds = property(_prop_get_odds, doc="odd structure")

    def _calcOdds(self):
        """Calculates the absolute probability of all posible rolls"""
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
        h = {}
        dice = []
        for (count, die) in self._dice.values():
            for i in range(0, count):
                dice.append(die.values)

        combinations = recur(start, h, dice, 0.0)
        self._odds = [(x, h[x], h[x]/combinations) for x in h.keys()]
        self._odds.sort()
    
    def add_die(self, die, count=1):
        """
        Add die to roll.
        @param die: die instance
        @param count: number of times die is rolled
        """
        roll = self._dice.setdefault(str(die), [0, die])
        roll[0] += count
        self._odds = None

    def remove_die(self, die):
        """
        Remove die (first matching) from roll.
        @param die: die instance
        """
        roll = self._dice.get(str(die), [40, 'dummy'])
        roll[0] -= 1
        if roll[0] == 0:
            del self._dice[str(die)]
        self._odds = None

    def roll_Values(self):
        """@return: A dice roll, list of individual rolls"""
        l = []
        for (count, die) in self._dice.values():
            l.extend(die.rolls(count))
        return l

    def roll_total(self):
        "@return: A dice roll, one numeric total"
        return reduce(lambda x, y: x+y, self.roll_Values())

    def roll_totalX(self, count):
        """
        @param count: Number of rolls to make.
        @return: List of dice rolls, one numeric total per roll.
        """
        # some lameness for supposed speed (unprofiled)
        dice = self._dice.values()
        if len(dice) == 1:
            (rolls, die) = dice[0]
            if rolls == 1:
                oneroll = lambda: die.roll()
            else:
                oneroll = lambda: reduce(lambda x, y: x+y, die.rolls(rolls))
        else:
            oneroll = self.roll_total
        return [ oneroll() for x in xrange(0, count) ]

    def roll_totalGenerator(self):
        """
        @return: generator that will produce roll_total forever
        """
        def generator():
            yield self.roll_total()
        return generator


