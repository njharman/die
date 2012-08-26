from __future__ import with_statement
import unittest
import re
import os
import sys

from six.moves import cStringIO
StringIO = cStringIO

from distutils.version import LooseVersion

import pep8

PEP8_VERSION = LooseVersion(pep8.__version__)
PEP8_MAX_OLD_VERSION = LooseVersion('1.0.1')
PEP8_MIN_NEW_VERSION = LooseVersion('1.3.3')

# Check for supported version of the pep8 library,
# which is anything <= 1.0.1, or >= 1.3.3. (yes, there is a gap)
if (PEP8_VERSION > PEP8_MAX_OLD_VERSION and PEP8_VERSION < PEP8_MIN_NEW_VERSION):
    raise ImportError('Bad pep8 version, must be >= %s or <= %s.' % (PEP8_MIN_NEW_VERSION, PEP8_MAX_OLD_VERSION))

# Skip these pep8 errors/warnings
PEP8_IGNORE = (
    'E123', 'E126', 'E127', 'E128', 'E501',
    )

# Any file or directory(including subdirectories) matching regex will be skipped.
NAMES_TO_SKIP = (
    '.svn',
    '.git',
    'docs',
    'dist',
    'build',
    )
NAMES_TO_SKIP = [re.compile('^%s' % n) for n in NAMES_TO_SKIP]


class RedirectIO(object):
    '''Contextmanager to redirect stdout/stderr.'''
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        sys.stdout.flush()
        sys.stderr.flush()
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        self._stderr.flush()
        sys.stdout, sys.stderr = self.old_stdout, self.old_stderr


class Pep8TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # set up newer pep8 options
        if PEP8_VERSION >= PEP8_MIN_NEW_VERSION:
            self.options = pep8.StyleGuide().options
            self.options.ignore = self.options.ignore + PEP8_IGNORE
        else:
            self.options = None

# Populate pep8 test methods, one per non-skipped .py file found.
ROOT = os.getcwd()
for (dirpath, dirnames, filenames) in os.walk(ROOT, followlinks=True):
    for regex in NAMES_TO_SKIP:
        paths = dirnames[:]  # lame list copy
        for path in paths:
            if regex.match(path):
                dirnames.remove(path)
        files = filenames[:]  # lame list copy
    for filename in [f for f in filenames if not regex.match(f)]:
        if not filename.endswith('.py'):
            continue
        fullpath = os.path.join(dirpath, filename)
        if PEP8_VERSION < PEP8_MIN_NEW_VERSION:
            def closure(self, fullpath=fullpath):
                pep8.process_options([
                    '--first', fullpath,
                    '--ignore', ','.join(PEP8_IGNORE)],
                    )
                pep8.input_file(fullpath)
                if len(pep8.get_statistics()):
                    self.fail('PEP8 issue in "%s"' % fullpath)
        else:
            def closure(self, fullpath=fullpath):
                checker = pep8.Checker(fullpath, options=self.options)
                capture = StringIO()
                with RedirectIO(capture):
                    errors = checker.check_all()
                if errors > 0:
                    capture.seek(0)
                    errors = list()
                    for error in capture.readlines():
                        errors.append('./%s' % error[len(ROOT) + 1:].strip())
                    self.fail('PEP8 issue in "%s"\n%s' % (fullpath, '\n'.join(errors)))
        relativepath = fullpath[len(ROOT) + 1:]
        func_name = 'test_pep8./%s' % relativepath  # Surprised invalid identifiers work.
        closure.__name__ = func_name
        setattr(Pep8TestCase, func_name, closure)
        del closure  # Necessary so nosetests doesn't make testcase out of it.
