__copyright__= "Copyright (c) 2003 Norman J. Harman Jr."
__license__ = """
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


class Statistic(object):
    """
    Roll lots of dice
    """
    def __init__(self, roll):
        """
        @param roll: Roll instance
        """
        self.roll = roll
        self._sum = 0
        self._avr = 0
        self._bucket = {}

    def _prop_get_bucket(self):
        result = map(None, self._bucket.keys(), self._bucket.values())
        result.sort()
        return result
    bucket = property(_prop_get_bucket)

    sum = property(lambda s: s._sum)
    avr = property(lambda s: s._avr)

    def do_sum(self, count=1):
        """
        set self.sum, self.avr and return sum of count dice rolls
        @param count: Number of rolls to make.
        @return: total (numeric) of 'count' dice rolls, 0 if not summable
        """
        if not self.roll.summable:
            return 0
        self._sum = reduce(lambda x, y: x+y, self.roll.tuple_rollotalX(count))
        self._avr = self._sum / count
        return self.sum
        
    def do_bucket(self, count=1):
        """
        set self.bucket and return results
        @param count: Number of rolls to make.
        @return: list of tuples (tuple_rollotal, times it was rolled) 
        """
        h = {}
        for roll in self.roll.tuple_rollotalX(count):
            count = h.get(roll, 0)
            h[roll] = count + 1
        self._bucket = h
        return self.bucket

    def do_run(self, count=1):
        """
        Roll count dice, store results. Does all stats so might be slower 
        than specific doFoo methods. But, it is proly faster than running 
        each of those seperately to get same stats.

        Sets the following properties:
          - stats.bucket
          - stats.sum
          - stats.avr

        @param count: Number of rolls to make.
        """
        if not self.roll.summable:
            raise Exception, "Roll is not summable"
        h = {}
        total = 0
        for roll in self.roll.tuple_rollotalX(count):
            total += roll
            hit = h.get(roll, 0)
            h[roll] = hit + 1
        self._bucket = h
        self._sum = total
        self._avr = total / count

