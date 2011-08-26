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

import die.roll


class RollTestor(unittest.TestCase):
    dice = (die.die.Standard(6), die.die.Standard(6))
    def test_init(self):
        r = die.roll.Roll()
        r = die.roll.Roll(self.dice)
        self.assertEqual(map(str, self.dice), map(str, r.dice) )
        r.description
        
    def test_odds(self):
        r = die.roll.Roll(self.dice)
        proper = [(2, 1, 0.027777777777777776), (3, 2, 0.055555555555555552), (4, 3, 0.083333333333333329), (5, 4, 0.1111111111111111), (6, 5, 0.1388888888888889), (7, 6, 0.16666666666666666), (8, 5, 0.1388888888888889), (9, 4, 0.1111111111111111), (10, 3, 0.083333333333333329), (11, 2, 0.055555555555555552), (12, 1, 0.027777777777777776)]
        self.assertEqual(proper, r.odds)

    def test_summable(self):
        r = die.roll.Roll(self.dice)
        self.failUnless(r.summable)
        r = die.roll.Roll([die.die.Standard(6), die.die.Weird('Al')])
        self.failIf(r.summable)
                
    def test_addDie_removeDie(self):
        r = die.roll.Roll()
        r.addDie(die.die.Standard(8))
        r.addDie(die.die.Standard(6), 3)
        self.assertEqual(4, len(r.dice))
        r.removeDie(die.die.Standard(6))
        self.assertEqual(3, len(r.dice))

    def test_rollValues(self):
        r = die.roll.Roll(self.dice)
        r.rollValues()

    def test_rollTotal(self):
        r = die.roll.Roll(self.dice)
        r.rollTotal()

    def test_rollTotalX(self):
        r = die.roll.Roll(self.dice)
        r.rollTotalX(100)

    def test_rollTotalGenerator(self):
        r = die.roll.Roll(self.dice)
        gen = r.rollTotalGenerator()
        for i in range(100):
            gen()
