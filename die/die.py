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

import types
import random


class Die(object):
    '''Base Die class.

    If str(dieA) == str(dieB) then dieA == dieB.
    '''
    numeric = True
    description = property(
            lambda s: s._description,
            lambda s, value: setattr(s, '_description', value),
            )
    name = property(lambda s: s._name)
    sides = property(lambda s: s._sides, doc='''Number of 'sides'.''')
    faces = property(
            lambda self: [x[0] for x in self._faces],
            doc='''List of face texts.''')
    values = property(
            lambda self: [x[1] for x in self._faces],
            doc='''List of face values.''')

    def __init__(self, name, faces):
        '''
        @param name: Identifies dice of this type.
        @param faces: List of (text, value), one per face.
        '''
        try:
            if not name:
                raise ValueError
            self._name = str(name).strip()
            if not self._name:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError('Invalid name')
        if len(faces) == 0:
            raise ValueError('Invalid faces')
        self._faces = faces
        self._sides = len(faces)

    def __str__(self):
        return self._name

    def roll(self):
        '''@return: value, one roll'''
        return self._faces[random.randint(1, self._sides) - 1][1]

    def rolls(self, x):
        '''@return: values, list of 'x' rolls'''
        return [self._faces[random.randint(1, self._sides) - 1][1] for i in range(x)]

    def tuple_roll(self):
        '''@return: (face, value) tuple, one roll'''
        return self._faces[random.randint(1, self._sides) - 1]

    def tuple_rolls(self, x):
        '''@return: (face, value) tuple, list of 'x' rolls'''
        l = list()
        for i in range(x):
            value = random.randint(1, self._sides)
            l.append((str(value), value))
        return l

    def iter(self):
        '''@return: generator of infinite rolls'''
        while True:
            yield self.roll()


class NumericBased(Die):
    '''Die with possibly non-numeric face texts, but each face has an
    associated numeric value.

    Fudge(www.fudgerpg.com) die::
        C{die.NumericBased('dF', (('+',1,2), ('',0,2), ('-',-1,2)))}
    '''
    def __init__(self, name, spec):
        '''
        @param name: Identifies dice of this type
        @param spec: list of tuple (facetext, value, count)
        '''
        faces = list()
        try:
            for (text, value, count) in spec:
                if count < 1:
                    raise ValueError
                1 - value  # must be better way to check if value numeric
                faces.extend((str(text), value) for x in range(count))
        except (TypeError, ValueError):
            raise ValueError('Bad spec')
        super(NumericBased, self).__init__(name, faces)

        self._description = 'NumericBased die with %i faces, [%s].' % (self._sides, ','.join('"%s"=%s' % (x[0], str(x[1])) for x in self._faces))


class Standard(NumericBased):
    '''Die with sequencial, numeric faces.

    The common six sided die would be::
        C{die.Standard(6)}
    '''
    def __init__(self, sides):
        '''@param sides: number of faces die has.'''
        try:
            if int(sides) <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError('Bad number of sides')
        name = 'd%i' % sides
        spec = [(x, x, 1) for x in range(1, sides + 1)]
        super(Standard, self).__init__(name, spec)
        self._description = 'Numeric die with %i faces numbered 1 through %i.' % (self._sides, self._sides)

    def roll(self):
        '''@return: value, one roll'''
        return random.randint(1, self._sides)

    def rolls(self, x):
        '''@return: values, list of 'x' rolls'''
        return [random.randint(1, self._sides) for i in range(x)]

    def tuple_roll(self):
        '''@return: (face, value) tuple, one roll'''
        value = random.randint(1, self._sides)
        return (str(value), value)

    def tuple_rolls(self, x):
        '''@return: (face, value) tuple, list of 'x' rolls'''
        l = list()
        for i in range(x):
            value = random.randint(1, self._sides)
            l.append((str(value), value))
        return l


class Numeric(NumericBased):
    '''Die with non-sequential, numeric faces, possibly repeating.

    Backgammon die::
        C{die.Numeric('backgammon', (2,4,8,16,32,64))}
    '''
    def __init__(self, name, spec):
        '''
        @param name: Uniquely identifies dice of this type.
        @param spec: List of numbers one per face of die.
        '''
        super(Numeric, self).__init__(name, [(x, x, 1) for x in spec])
        self._description = 'Numeric die with %i faces [%s].' % (self._sides, ','.join(self.faces))


class Weird(Die):
    '''Die with textual faces, and 'values' that aren't necessarly numeric.
    '''
    numeric = False

    def __init__(self, name, spec):
        '''
        @param name: Uniquely identifies dice of this type.
        @param spec: List of tuples - (facetext, facevalue, count)
                      facevalue must be convertable into string but
                      otherwise is free to get funky. count is number
                      of faces with these text/value.
        '''
        faces = list()
        try:
            for text, value, count in spec:
                if count < 1:
                    raise ValueError
                faces.extend((text, value) for x in range(count))
        except (TypeError, ValueError):
            raise ValueError('Bad spec')
        super(Weird, self).__init__(name, faces)
        self._description = 'Weird die with %i faces [%s].' % (
                self._sides,
                ','.join('" % s"=%s' % (x[0], str(x[1])) for x in self._faces)
                )
