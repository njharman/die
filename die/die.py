__copyright__= "Copyright (c) 2003-4 Norman J. Harman Jr."
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

import types
import random


class Base(object):
    """
    Abstract Base die class

    If str(dieA) == str(dieB) then dieA == dieB.
    """
    numeric = True
    description = property(
            lambda s: s._longDescription, 
            lambda s, value: setattr(s, '_longDescription', value), 
            doc="longish description of die")
    name   = property(lambda s: s._name, doc="name of die")
    sides  = property(lambda s: s._sides, doc="number of 'sides' the die has")
    faces  = property(lambda s: [], doc="list of face texts")
    values = property(lambda s: [], doc="list of face values")

    def __str__(self):
        return self._name

    def roll(self):
        """@return: value, one roll"""
        return self._faces[random.randint(1, self._sides)-1][1]

    def rolls(self, x):
        """@return: values, list of 'x' rolls"""
        return [self._faces[random.randint(1, self._sides)-1][1] for i in range(x)]

    def tuple_roll(self):
        """@return: (face, value) tuple, one roll"""
        return self._faces[random.randint(1, self._sides)-1]

    def tuple_rolls(self, x):
        """@return: (face, value) tuple, list of 'x' rolls"""
        l = []
        for i in range(x):
            value = random.randint(1, self._sides)
            l.append((str(value), value))
        return l

    def iter(self):
        """@return: generator of infinate rolls"""
        while True:
            yield self.roll()


class NumericBased(Base):
    """
    A die with possibly non-numeric face texts, but each face has a numeric value

    A Fudge(www.fudgerpg.com) die::
        C{die.NumericBased('dF', (('+',1,2), ('',0,2), ('-',-1,2)))}
    """
    def __init__(self, name, faces=()):
        """
        @param name:  uniquely identifies dice of this type
        @param faces: list of tuple (facetext, value, numberOfFaces)
        """
        if type(name) not in (types.StringType, types.UnicodeType) or len(name) == 0:
            raise AttributeError, "Invalid name [%s]" % str(name)
        self._name = name
        self._faces = []
        self._sides = 0
        try:
            for (text, value, count) in faces:
                if count < 1:
                    raise ValueError
                1 - value # mustbe better way to check if value numeric
                self._sides += count
                self._faces.extend([(text, value) for x in range(count)])
        except (TypeError, ValueError):
            raise AttributeError, "Bad faces"
            
        self._longDescription = "NumericBased die with %i faces, [%s]." % (
            self._sides, ','.join(["'%s'=%s" % (x[0], str(x[1])) for x in self._faces]))

    faces  = property(lambda self: [x[0] for x in self._faces], doc="list of face texts")
    values = property(lambda self: [x[1] for x in self._faces], doc="list of face values")


class Standard(Base):
    """
    A die with sequencial, numeric faces.

    The common six sided die would be::
        C{die.Standard(6)}
    """
    def __init__(self, sides):
        """@param sides: number of 'sides' this die has"""
        if type(sides) is not types.IntType or sides <= 0:
            raise AttributeError, "Must have positive integer number of sides, not [%s]." % (sides)
        self._sides = sides
        self._longDescription = "Numeric die with %i faces, numbered 1 through %i." % (self._sides, self._sides)
        self._name = "d%i" % self._sides

    faces  = property(lambda self: [str(i) for i in range(1, self._sides+1)], doc="list of face texts")
    values = property(lambda self: range(1, self._sides+1), doc="list of face values")

    def roll(self):
        """@return: value, one roll"""
        return random.randint(1, self._sides)

    def rolls(self, x):
        """@return: values, list of 'x' rolls"""
        return [ random.randint(1, self._sides) for i in range(x) ]

    def tuple_roll(self):
        """@return: (face, value) tuple, one roll"""
        value = random.randint(1, self._sides)
        return (str(value), value)

    def tuple_rolls(self, x):
        """@return: (face, value) tuple, list of 'x' rolls"""
        l = []
        for i in range(x):
            value = random.randint(1, self._sides)
            l.append((str(value), value))
        return l


class Numeric(NumericBased):
    """
    A die with numeric faces, non-sequential, possibly repeating

    Backgammon die::
        C{die.Numeric('backgammon', (2,4,8,16,32,64))}
    """
    def __init__(self, name, faces=()):
        """
        @param faces: list of numbers len(list) == sides of die
        """
        NumericBased.__init__(self, name, [(str(x), x, 1) for x in faces])
        self._longDescription = "Numeric die with %i faces, [%s]." % (self._sides, ','.join(self.faces))
        

class Weird(Base):
    """
    A die with textual faces, and 'values' that aren't necessarly numeric.
    """
    numeric = False
    def __init__(self, name, faces=()):
        """
        @param name:  uniquely identifies dice of this type
        @param faces: list of tuple (facetext, value, numberOfFaces)
        value must be convertable into string but otherwise is free to get funky
        """
        if type(name) not in (types.StringType, types.UnicodeType) or len(name) <= 0:
            raise AttributeError, "Invalid name [%s]" % str(name)
        self._name = name
        self._faces = []
        self._sides = 0
        try:
            for text, value, count in faces:
                if count < 1:
                    raise ValueError
                self._sides += count
                self._faces.extend([(text, value) for x in range(count)])
        except (TypeError, ValueError):
            raise AttributeError, "Bad faces"

        self._longDescription = "Weird die with %i faces, [%s]." % (self._sides, ','.join(["'%s'=%s" % (x[0], str(x[1])) for x in self._faces]))

    faces  = property(lambda self: [x[0] for x in self._faces], doc="list of face texts")
    values = property(lambda self: [str(x[1]) for x in self._faces], doc="list of face values")


