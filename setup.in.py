__copyright__ ="Copyright (c) 2003-4 Norman J. Harman Jr."
__license__   ="""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
"""
__doc__ = """
%(copyright)s
%(license)s

execute 'setup.in.py'

to install locally:
    %%python setup.py install

to create a source distribution(s):
    %%python setup.py sdist --formats=zip,bztar,gztar
    %%python setup.py bdist --formats=zip,wininst
    %%python setup.py bdist --formats=rpm,srpm,
""" % {'name':__name__, 'copyright':__copyright__, 'license':__license__}


if __name__ == "__main__":
    import KLM.dotin as dotin
    import die as targetModule

    hash = {}
    hash['packageName']      = "die"
    hash['packages']         = "['die',]"
    hash['name']             = "Die"
    hash['version']          = str(targetModule.__version__)
    hash['description']      = "Classes for simulating dice, dice rolls, and stats on dice."
    hash['long_description'] = targetModule.__doc__.strip()
    hash['copyright']        = targetModule.__copyright__
    hash['author']           = targetModule.__author__
    hash['author_email']     = targetModule.__email__
    hash['url']              = targetModule.__url__
    hash['platforms']        = "all, os-x(tested), linux(tested)"
    hash['documentation']    = "Epydoc compatible docstrings. \nSee http://epydoc.sourceforge.net/epytext.html"
    hash['testing']          = "python runall.py"
    hash['version_history']  = "0.1 - initial release\n"
    if targetModule.__license__.find('LGPL')>=0:
        dotin.createLGPL(filename='LICENSE')
        hash['license'] = "LGPL - Lessor GNU Public License"
    elif targetModule.__license__.find('GPL')>=0 or targetModule.__license__.find('GNU General Public License')>=0:
        dotin.createGPL(filename='LICENSE')
        hash['license'] = "GPL - GNU Public License"
    else:
        raise StandardError, "Don't know what sort of license to create."

    dotin.createReadme(hash, filename='README')
    dotin.createSetup(hash)
