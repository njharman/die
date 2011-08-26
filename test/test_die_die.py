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

import die.die


class StandardDieTestor(unittest.TestCase):
    goodDice = (1, 5, 80, 99, 2000)
    badDice =(0, -1, 'what', None)

    def test_badInit(self):
        for i in self.badDice:
            self.assertRaises(AttributeError, die.die.Standard, i)

    def test_properties(self):
        for i in self.goodDice:
            d = die.die.Standard(i)
            self.assertEqual(i, len(d.faces))
            self.assertEqual(i, len(d.values))
            self.assertEqual(i, d.sides)
            self.failUnless(d.numeric)
            d.description

    def test_Minimal(self):
        d = die.die.Standard(6)
        d.roll()
        d.rollT()
        self.assertEqual(2, len(d.rollX(2)))
        self.assertEqual(2, len(d.rollTX(2)))
        

class NamedTestFixture(unittest.TestCase):
    "Common test code"
    badName = ('', None, (), 34)
    goodName = 'dTest'
    
    def _test_badInit(self):
        for name in self.badName:
            self.assertRaises(AttributeError, self.klas, name, self.goodFaces)
        for i in range(len(self.badFaces)):
            faces = [ self.badFaces[i], ]
            faces.extend(self.goodFaces)
            self.assertRaises(AttributeError, self.klas, self.goodName, faces)

    def _test_properties(self):
        for i in range(40):
            sides = 0
            faces = []
            for f in range(i % 8):
                face = self.goodFaces[i % len(self.goodFaces)]
                faces.append(face)
                sides += self.getSides(face)
            d = self.klas(self.goodName, faces)
            self.assertEqual(str(d), self.goodName)
            self.assertEqual(sides, len(d.faces))
            self.assertEqual(sides, len(d.values))
            self.assertEqual(sides, d.sides)
            self.assertEqual(self.numeric, d.numeric)
            d.description

    def _test_minimal(self):
        d = self.klas(self.goodName, self.goodFaces)
        d.roll()
        d.rollT()
        self.assertEqual(2, len(d.rollX(2)))
        self.assertEqual(2, len(d.rollTX(2)))
        

class NumericTestor(NamedTestFixture):
    klas = die.die.Numeric
    goodFaces = (1,2,3,1.0,2.0,-3)
    badFaces = (None, '+',(1,),)
    numeric = True
    getSides = lambda self, face: 1

    test_badInit = NamedTestFixture._test_badInit
    test_properties = NamedTestFixture._test_properties        
    test_minimal = NamedTestFixture._test_minimal        
        
        
class NumericBasedTestor(NamedTestFixture):
    klas = die.die.NumericBased
    goodFaces = (('+',1,1), ('-',-1.45,20), ('',0,2), (' ',0,2))
    badFaces = (None, 1, (), ('+',3), ('',1,0), ('',0,-2), ('','t',1))
    numeric = True
    getSides = lambda self, face: face[2]

    test_badInit = NamedTestFixture._test_badInit
    test_properties = NamedTestFixture._test_properties        
    test_minimal = NamedTestFixture._test_minimal        
        

class WeirdDieTestor(NamedTestFixture):
    klas = die.die.Weird
    goodFaces = (('+',1,1), ('-',-1.45,20), ('',0,2), (' ',0,2), ('g','t',2))
    badFaces = (None, 1, (), ('+',3), ('',1,0), ('',0,-2) )
    numeric = False
    getSides = lambda self, face: face[2]

    test_badInit = NamedTestFixture._test_badInit
    test_properties = NamedTestFixture._test_properties        
    test_minimal = NamedTestFixture._test_minimal        
    
