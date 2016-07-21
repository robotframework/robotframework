from os.path import abspath, dirname, join
from fnmatch import fnmatchcase
from operator import eq

from robot.api import logger

CURDIR = dirname(abspath(__file__))


def output_should_be(actual, expected):
    actual = _read_file(actual, 'Actual')
    expected = _read_file(join(CURDIR, expected), 'Expected')
    if len(expected) != len(actual):
        raise AssertionError('Lengths differ. Expected %d lines but got %d'
                             % (len(expected), len(actual)))
    for exp, act in zip(expected, actual):
        tester = fnmatchcase if '*' in exp else eq
        if not tester(act.rstrip(), exp.rstrip()):
            raise AssertionError('Lines differ.\nExpected: %s\nActual:   %s'
                                 % (exp, act))


def _read_file(path, title):
    with open(path) as file:
        content = file.read()
    logger.debug('%s:\n%s' % (title, content))
    return content.splitlines()
