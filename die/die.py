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

import random


class Die(object):
    '''Base Die class.

    Some properties:
      - Die with identical faces are equal.
      - Die are not hashable.
      - Die is numeric if obj.numeric) == True.
      - obj(), int(obj), float(obj), obj.roll() return result of rolling die.
      - For numeric die; +, -, *, //, /, %, ^, **, operators cause die roll.
      - For numeric die; >, >=, <, <= operators cause die roll BUT NOT =, !=.  This is means Die
        are not sortable.

    Attributes (all read only):
      - name: short textual identifier.
      - description: textual description.
      - numeric: [boolean] True if all of die's faces map to numeric **values**.
      - sides: number of sides dice has.
      - items: list of (face, value) tuples.
      - faces: list of face texts.
      - values: list of face values.
    '''
    numeric = True
    sides = property(lambda s: s._sides, doc='''Number of 'sides'.''')
    items = property(
            lambda self: [x for x in self._faces],
            doc='''List of (face, value) tuples.''')
    faces = property(
            lambda self: [x[0] for x in self._faces],
            doc='''List of face texts.''')
    values = property(
            lambda self: [x[1] for x in self._faces],
            doc='''List of face values.''')

    def __init__(self, name, faces):
        '''
        :param name: Identifies Die of this type.
        :param faces: List of (text, value), one per face.
        '''
        try:
            self.name = name.strip()
            if not self.name:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError('Invalid name')
        self.description = self.name  # Subclasses are expected to set.  Not passed in as parm cause most want to use _sides, _faces to set.
        if len(faces) == 0:
            raise ValueError('Invalid faces')
        self._faces = faces
        self._sides = len(faces)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return '<%s(%s, %s)>' % (self.__class__.__name__, self.name, self._faces)

    def __call__(self):
        return self.roll()

    def __int__(self):
        return int(self.roll())

    def __float__(self):
        return float(self.roll())

    def __index__(self):
        '''Slicing.'''
        return int(self.roll())

    def __eq__(self, other):
        if not isinstance(other, Die):
            return False
        return self._sides == other._sides and self._faces == other._faces

    def __ne__(self, other):
        if not isinstance(other, Die):
            return True
        return self._sides != other._sides or self._faces != other._faces

    def __cmp__(self, other):
        return self.roll() - other

    def __add__(self, other):
        return self.roll() + other

    def __radd__(self, other):
        return self.roll() + other

    def __sub__(self, other):
        return self.roll() - other

    def __rsub__(self, other):
        return self.roll() - other

    def __mul__(self, other):
        return self.roll() * other

    def __rmul__(self, other):
        return self.roll() * other

    def __div__(self, other):
        return self.roll() / other

    def __rdiv__(self, other):
        return other / self.roll()

    def __truediv__(self, other):
        return self.roll() / other

    def __rtruediv__(self, other):
        return other / self.roll()

    def __floordiv__(self, other):
        return self.roll() // other

    def __rfloordiv__(self, other):
        return other // self.roll()

    def __mod__(self, other):
        return self.roll() % other

    def __rmod__(self, other):
        return other % self.roll()

    def __pow__(self, other):
        return self.roll() ** other

    def __rpow__(self, other):
        return other ** self.roll()

    def roll(self, count=0):
        '''One or more die rolls.
        :param count: [0] Return list of ``count`` rolls
        :return: Value of roll or list of values
        '''
        if count:
            return [self._faces[random.randint(1, self._sides) - 1][1] for i in range(count)]
        else:
            return self._faces[random.randint(1, self._sides) - 1][1]

    def iter(self, count=0):
        '''Iterator of infinite rolls.
        :param count: [0] Return list of ``count`` rolls
        '''
        while True:
            yield self.roll(count)

    def tuple_roll(self, count=0):
        '''One or more die rolls.
        :param count: [0] Return list of ``count`` rolls
        :return: (face, value) of roll or list of same
        '''
        if count:
            return [self._faces[random.randint(1, self._sides) - 1] for i in range(count)]
        else:
            return self._faces[random.randint(1, self._sides) - 1]

    def tuple_iter(self, count=0):
        '''Iterator of infinite tuple_rolls.
        :param count: [0] Return list of ``count`` tuples
        '''
        while True:
            yield self.tuple_roll(count)


class NumericBased(Die):
    '''Die with possibly non-numeric face texts, but each face has an
    associated numeric value.

    Fudge(www.fudgerpg.com) die::
        C{die.NumericBased('dF', (('+',1,2), ('',0,2), ('-',-1,2)))}
    '''
    def __init__(self, name, spec):
        '''
        :param name: Identifies dice of this type
        :param spec: List of tuples (facetext, value, count)
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
        super(NumericBased, self).__init__(str(name), faces)
        self.description = 'NumericBased die with %i faces, [%s].' % (self._sides, ','.join('"%s"=%s' % (x[0], str(x[1])) for x in self._faces))


class Standard(NumericBased):
    '''Die with sequencial, numeric faces.

    The common six sided die would be::
        C{die.Standard(6)}
    '''
    def __init__(self, sides):
        ''':param sides: number of faces die has.'''
        try:
            if int(sides) <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError('Bad number of sides')
        name = 'd%i' % sides
        spec = [(x, x, 1) for x in range(1, sides + 1)]
        super(Standard, self).__init__(name, spec)
        self.description = 'Numeric die with %i faces numbered 1 through %i.' % (self._sides, self._sides)


class Numeric(NumericBased):
    '''Die with non-sequential, numeric faces, possibly repeating.

    Ex. A backgammon die::
        C{die.Numeric('backgammon', (2,4,8,16,32,64))}
    '''
    def __init__(self, name, spec):
        '''
        :param name: Uniquely identifies dice of this type.
        :param spec: List of numbers one per face of die.
        '''
        super(Numeric, self).__init__(str(name), [(x, x, 1) for x in spec])
        self.description = 'Numeric die with %i faces [%s].' % (self._sides, ','.join(self.faces))


class Weird(Die):
    '''Die with textual faces, and 'values' that aren't necessarly numeric.
    '''
    numeric = False

    def __init__(self, name, spec):
        '''
        :param name: Uniquely identifies dice of this type.
        :param spec: List of tuples - (facetext, facevalue, count)
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
        super(Weird, self).__init__(str(name), faces)
        self.description = 'Weird die with %i faces [%s].' % (
                self._sides,
                ','.join('" % s"=%s' % (x[0], str(x[1])) for x in self._faces)
                )
