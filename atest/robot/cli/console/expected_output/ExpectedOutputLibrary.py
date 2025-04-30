from fnmatch import fnmatchcase
from operator import eq
from os.path import abspath, dirname, join

from robot.api import logger
from robot.api.deco import keyword

ROBOT_AUTO_KEYWORDS = False
CURDIR = dirname(abspath(__file__))


@keyword
def output_should_be(actual, expected, **replaced):
    actual = _read_file(actual, "Actual")
    expected = _read_file(join(CURDIR, expected), "Expected", replaced)
    if len(expected) != len(actual):
        raise AssertionError(
            f"Lengths differ. Expected {len(expected)} lines, got {len(actual)}."
        )
    for exp, act in zip(expected, actual):
        tester = fnmatchcase if "*" in exp else eq
        if not tester(act.rstrip(), exp.rstrip()):
            raise AssertionError(f"Lines differ.\nExpected: {exp}\nActual:   {act}")


def _read_file(path, title, replaced=None):
    with open(path, encoding="UTF-8") as file:
        content = file.read()
    if replaced:
        for item in replaced:
            content = content.replace(item, replaced[item])
    logger.debug(f"{title}:\n{content}")
    return content.splitlines()
