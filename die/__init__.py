__author__ = 'Norman J. Harman Jr.'
__email__ = 'njharman@gmail.com'
__version__ = '0.2.0'
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
__doc__ = '''%(name)s v%(version)s

%(copyright)s
%(license)s

About
=====

Classes to represent various dice, dice rolls, and stats on same.

Flexibility has priority over speed.

Die Classes
-----------
  - L{die.Standard}
  - L{die.Numeric}
  - L{die.NumericBased}
  - L{die.Weird}
  - L{die.Roll}

Support Classes
---------------
  - L{die.stats.Statistic}
''' % {'name': __name__, 'version': __version__, 'copyright': __copyright__,
       'license': __license__, 'email': __email__, 'author': __author__}

from .die import NumericBased, Standard, Numeric, Weird
from .roll import Roll
from .stats import Statistic
