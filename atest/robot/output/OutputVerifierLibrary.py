from __future__ import with_statement
import os

from robot.utils import utf8open


def output_should_have_correct_line_separators(path):
    with utf8open(path) as infile:
        content = infile.read()
    content = content.replace(os.linesep, '')
    extra_r = content.count('\r')
    extra_n = content.count('\n')
    if extra_r or extra_n:
        err = AssertionError("Output '%s' has %d extra \\r and %d extra \\n"
                             % (path, extra_r, extra_n))
        err.ROBOT_CONTINUE_ON_FAILURE = True
        raise err
