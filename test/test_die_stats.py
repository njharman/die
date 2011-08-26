__copyright__="Copyright (c) 2003-4 Norman J. Harman Jr. njharman@knoggin.com"
__license__="""Licensed under the FSF GPL

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
__doc__ = """
%(copyright)s
%(license)s
""" % {'copyright':__copyright__, 'license':__license__} 

import unittest

import die
import die.stats


class StatsTestor(unittest.TestCase):
    def test_minimal(self):
        roll = die.Roll((die.Standard(6),))
        s = die.stats.Statistic(roll)
        s.doSum()
        s.doBucket(2)
        s.doRun(2)
