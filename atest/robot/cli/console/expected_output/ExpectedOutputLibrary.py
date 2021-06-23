from os.path import abspath, dirname, join
from fnmatch import fnmatchcase
from operator import eq

from robot.api import logger
from robot.api.deco import keyword


ROBOT_AUTO_KEYWORDS = False
CURDIR = dirname(abspath(__file__))


@keyword
def output_should_be(actual, expected, **replaced):
    actual = _read_file(actual, 'Actual')
    expected = _read_file(join(CURDIR, expected), 'Expected', replaced)
    if len(expected) != len(actual):
        raise AssertionError('Lengths differ. Expected %d lines but got %d'
                             % (len(expected), len(actual)))
    for exp, act in zip(expected, actual):
        tester = fnmatchcase if '*' in exp else eq
        if not tester(act.rstrip(), exp.rstrip()):
            raise AssertionError('Lines differ.\nExpected: %s\nActual:   %s'
                                 % (exp, act))


def _read_file(path, title, replaced=None):
    with open(path) as file:
        content = file.read()
    if replaced:
        for item in replaced:
            content = content.replace(item, replaced[item])
    logger.debug('%s:\n%s' % (title, content))
    return content.splitlines()
