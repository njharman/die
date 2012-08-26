die
===
Dice library, for RPG and Board Game tools, games, whatever.

Flexibility over speed.


Installing
----------
Prequisites:
 - six_ Python 2/3 compatibility library.

::

  pip install -U -r requirements.pip
  python setup.py install


Testing
-------
Additional unittests prerequisites:
 - pep8_
 - unittest2_ (only Python < 2.7)

The author uses nose_ to run unittests. ::

  pip install -U -r requirements.pip --use-mirrors
  pip install -U pep8 --use-mirrors
  nosetests


Build Status
------------
.. image:: https://secure.travis-ci.org/njharman/die.png
   :align: left
   :scale: 200%

Tested against the following Python Versions using `Travis CI`_:

  - 2.5 requires unittest2_
  - 2.6 requires unittest2_
  - 2.7
  - 3.1
  - 3.2

History
-------

0.2.0
  Updated to modern style, pep8, tests, docs, travis-ci, more unittests.

0.1
  Initial release.

.. _six: http://packages.python.org/six/
.. _pep8: http://pypi.python.org/pypi/pep8/
.. _unittest2: http://pypi.python.org/pypi/unittest2/
.. _nose: http://pypi.python.org/pypi/nose/
.. _travis ci: http://travis-ci.org/#!/njharman/cuprum
