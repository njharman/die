die
===
.. image:: https://secure.travis-ci.org/njharman/die.png
   :target: https://secure.travis-ci.org/njharman/die
   :alt: Build status
   :scale: 200%

About
-----
die is a dice library, for RPG and Board Game games, tools, whatever.

Emphasizes flexibility over speed.


Installing
----------
via source::

    python setup.py install

via pip::

    pip install --upgrade die


Testing
-------
unittest prerequisites:
    - pep8_
    - unittest2_ (only Python < 2.7)

Author uses nose_ to run unittests, YMMV. ::

    pip install --upgrade pep8 --use-mirrors
    nosetests


Unittests run against the following Python versions using `Travis CI`_:

  - 2.5 requires unittest2_
  - 2.6 requires unittest2_
  - 2.7
  - 3.1
  - 3.2


Using
-----
Until some docs are written have a look at ``demo.py``.


History
-------

0.2.0
  Updated to modern style, pep8, tests, docs, travis-ci, more unittests.
  Py3.x support.

0.1.0
  Initial release.


.. _pep8: http://pypi.python.org/pypi/pep8/
.. _unittest2: http://pypi.python.org/pypi/unittest2/
.. _nose: http://pypi.python.org/pypi/nose/
.. _travis ci: http://travis-ci.org/#!/njharman/die
