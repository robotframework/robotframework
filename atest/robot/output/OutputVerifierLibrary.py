from __future__ import with_statement
import os
import codecs


def output_should_have_correct_line_separators(path):
    with codecs.open(path, encoding='UTF-8') as infile:
        content = infile.read()
    content = content.replace(os.linesep, '')
    incorrect = content.count('\n')
    if incorrect:
        err = AssertionError("Output '%s' has %d incorrect line separators"
                             % (path, incorrect))
        err.ROBOT_CONTINUE_ON_FAILURE = True
        raise err
