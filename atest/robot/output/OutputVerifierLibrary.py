from __future__ import with_statement
import os

from robot.utils import utf8open


def output_should_have_correct_line_separators(path):
    with utf8open(path) as infile:
        content = infile.read()
    content = content.replace(os.linesep, '')
    incorrect = content.count('\n')
    if incorrect:
        err = AssertionError("Output '%s' has %d incorrect line separators"
                             % (path, incorrect))
        err.ROBOT_CONTINUE_ON_FAILURE = True
        raise err
