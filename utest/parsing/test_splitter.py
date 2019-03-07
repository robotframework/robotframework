import unittest

from robot.utils.asserts import assert_equal

from robot.parsing.lexer.splitter import Splitter
from robot.parsing.lexer.tokens import Token


DATA = Token.DATA
SEPA = Token.SEPARATOR
CONT = Token.CONTINUATION
COMM = Token.COMMENT


def verify_split(string, *expected_statements, **config):
    expected_data = []
    actual_statements = list(Splitter().split(string, **config))
    assert_equal(len(actual_statements), len(expected_statements))
    for actual_statement, expected_statement in zip(actual_statements,
                                                    expected_statements):
        expected_data.append([])
        assert_equal(len(actual_statement), len(expected_statement))
        for actual, expected in zip(actual_statement, expected_statement):
            if expected[0] == DATA:
                expected_data[-1].append(expected)
            expected = Token(*expected)
            assert_equal(actual.type, expected.type)
            assert_equal(actual.value, expected.value)
            assert_equal(actual.lineno, expected.lineno)
            assert_equal(actual.columnno, expected.columnno)
    if not config:
        verify_split(string, *expected_data, data_only=True)


class TestSplitFromSpaces(unittest.TestCase):

    def test_basics(self):
        verify_split('Hello    my world  !',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '    ', 1, 6),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  ', 1, 18),
                      (DATA, '!', 1, 20)])

    def test_newline(self):
        verify_split('Hello    my world  !\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '    ', 1, 6),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  ', 1, 18),
                      (DATA, '!', 1, 20),
                      (SEPA, '\n', 1, 21)])

    def test_trailing_spaces(self):
        verify_split('Hello  world   ',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '  ', 1, 6),
                      (DATA, 'world', 1, 8),
                      (SEPA, '   ', 1, 13)])

    def test_trailing_spaces_with_newline(self):
        verify_split('Hello  world   \n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '  ', 1, 6),
                      (DATA, 'world', 1, 8),
                      (SEPA, '   \n', 1, 13)])

    def test_empty(self):
        verify_split('')
        verify_split('\n', [(SEPA, '\n', 1, 1)])
        verify_split('  ', [(SEPA, '  ', 1, 1)])
        verify_split('  \n', [(SEPA, '  \n', 1, 1)])

    def test_multiline(self):
        verify_split('Hello  world\n    !!!\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '  ', 1, 6),
                      (DATA, 'world', 1, 8),
                      (SEPA, '\n', 1, 13)],
                     [(DATA, '', 2, 1),
                      (SEPA, '    ', 2, 1),
                      (DATA, '!!!', 2, 5),
                      (SEPA, '\n', 2, 8)])

    def test_multiline_with_empty_lines(self):
        verify_split('Hello\n\nworld\n    \n!!!',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (SEPA, '\n', 2, 1)],
                     [(DATA, 'world', 3, 1),
                      (SEPA, '\n', 3, 6),
                      (SEPA, '    \n', 4, 1)],
                     [(DATA, '!!!', 5, 1)])

    def test_non_ascii_spaces(self):
        spaces = (u'\N{NO-BREAK SPACE}\N{OGHAM SPACE MARK}\N{EN QUAD}'
                  u'\N{EM SPACE}\N{HAIR SPACE}\N{IDEOGRAPHIC SPACE}')
        verify_split(u'Hello{s}world\n{s}!!!{s}\n'.format(s=spaces),
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, spaces, 1, 6),
                      (DATA, 'world', 1, 12),
                      (SEPA, '\n', 1, 17)],
                     [(DATA, '', 2, 1),
                      (SEPA, spaces, 2, 1),
                      (DATA, '!!!', 2, 7),
                      (SEPA, spaces+'\n', 2, 10)])
        verify_split(u'|{s}Hello{s}|{s}world\n|{s}|{s}!!!{s}|{s}\n'.format(s=spaces),
                     [(SEPA, '|'+spaces, 1, 1),
                      (DATA, 'Hello', 1, 8),
                      (SEPA, spaces+'|'+spaces, 1, 13),
                      (DATA, 'world', 1, 26),
                      (SEPA, '\n', 1, 31)],
                     [(SEPA, '|'+spaces, 2, 1),
                      (DATA, '', 2, 8),
                      (SEPA, '|'+spaces, 2, 8),
                      (DATA, '!!!', 2, 15),
                      (SEPA, spaces+'|', 2, 18),
                      (SEPA, spaces+'\n', 2, 25)])


class TestSplitFromPipes(unittest.TestCase):

    def test_basics(self):
        verify_split('| Hello | my world  |   ! |',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25),
                      (SEPA, ' |', 1, 26)])

    def test_newline(self):
        verify_split('| Hello | my world  |   ! |\n',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25),
                      (SEPA, ' |', 1, 26),
                      (SEPA, '\n', 1, 28)])

    def test_trailing_spaces(self):
        verify_split('| Hello | my world  |   ! |      ',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25),
                      (SEPA, ' |', 1, 26),
                      (SEPA, '      ', 1, 28)])

    def test_trailing_spaces_with_newline(self):
        verify_split('| Hello | my world  |   ! |      \n',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25),
                      (SEPA, ' |', 1, 26),
                      (SEPA, '      \n', 1, 28)])

    def test_empty(self):
        verify_split('|',
                     [(SEPA, '|', 1, 1)])
        verify_split('|\n',
                     [(SEPA, '|', 1, 1),
                      (SEPA, '\n', 1, 2)])
        verify_split('|  ',
                     [(SEPA, '|', 1, 1),
                      (SEPA, '  ', 1, 2)])
        verify_split('|  \n',
                     [(SEPA, '|', 1, 1),
                      (SEPA, '  \n', 1, 2)])
        verify_split('| |  |        |',
                     [(SEPA, '| ', 1, 1),
                      (SEPA, '|  ', 1, 3),
                      (SEPA, '|        ', 1, 6),
                      (SEPA, '|', 1, 15)])

    def test_no_pipe_at_end(self):
        verify_split('| Hello | my world  |   !',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25)])

    def test_no_pipe_at_end_with_trailing_spaces(self):
        verify_split('| Hello | my world  |   !    ',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25),
                      (SEPA, '    ', 1, 26)])

    def test_no_pipe_at_end_with_newline(self):
        verify_split('| Hello | my world  |   !\n',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25),
                      (SEPA, '\n', 1, 26)])

    def test_no_pipe_at_end_with_trailing_spaces_and_newline(self):
        verify_split('| Hello | my world  |   !    \n',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'my world', 1, 11),
                      (SEPA, '  |   ', 1, 19),
                      (DATA, '!', 1, 25),
                      (SEPA, '    \n', 1, 26)])

    def test_empty_internal_data(self):
        verify_split('| Hello |    | | world |',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' |    ', 1, 8),
                      (DATA, '', 1, 14),
                      (SEPA, '| ', 1, 14),
                      (DATA, '', 1, 16),
                      (SEPA, '| ', 1, 16),
                      (DATA, 'world', 1, 18),
                      (SEPA, ' |', 1, 23)])

    def test_trailing_empty_data_is_filtered(self):
        verify_split('| Hello |  |    | |    \n',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' |  ', 1, 8),
                      (SEPA, '|    ', 1, 12),
                      (SEPA, '| ', 1, 17),
                      (SEPA, '|', 1, 19),
                      (SEPA, '    \n', 1, 20)])

    def test_multiline(self):
        verify_split('| Hello | world |\n| | !!!\n',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (DATA, 'world', 1, 11),
                      (SEPA, ' |', 1, 16),
                      (SEPA, '\n', 1, 18)],
                     [(SEPA, '| ', 2, 1),
                      (DATA, '', 2, 3),
                      (SEPA, '| ', 2, 3),
                      (DATA, '!!!', 2, 5),
                      (SEPA, '\n', 2, 8)])

    def test_multiline_with_empty_lines(self):
        verify_split('| Hello |\n|\n|  world\n|    |\n| !!!',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' |', 1, 8),
                      (SEPA, '\n', 1, 10),
                      (SEPA, '|', 2, 1),
                      (SEPA, '\n', 2, 2)],
                     [(SEPA, '|  ', 3, 1),
                      (DATA, 'world', 3, 4),
                      (SEPA, '\n', 3, 9),
                      (SEPA, '|    ', 4, 1),
                      (SEPA, '|', 4, 6),
                      (SEPA, '\n', 4, 7)],
                     [(SEPA, '| ', 5, 1),
                      (DATA, '!!!', 5, 3)])


class TestContinuation(unittest.TestCase):

    def test_spaces(self):
        verify_split('Hello\n...    world',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (CONT, '...', 2, 1),
                      (SEPA, '    ', 2, 4),
                      (DATA, 'world', 2, 8)])

    def test_pipes(self):
        verify_split('| Hello |\n| ... | world',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' |', 1, 8),
                      (SEPA, '\n', 1, 10),
                      (SEPA, '| ', 2, 1),
                      (CONT, '...', 2, 3),
                      (SEPA, ' | ', 2, 6),
                      (DATA, 'world', 2, 9)])

    def test_mixed(self):
        verify_split('Hello\n| ... | world\n...   ...',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (SEPA, '| ', 2, 1),
                      (CONT, '...', 2, 3),
                      (SEPA, ' | ', 2, 6),
                      (DATA, 'world', 2, 9),
                      (SEPA, '\n', 2, 14),
                      (CONT, '...', 3, 1),
                      (SEPA, '   ', 3, 4),
                      (DATA, '...', 3, 7)])

    def test_leading_empty_with_spaces(self):
        verify_split('    Hello\n        ...    world',
                     [(DATA, '', 1, 1),
                      (SEPA, '    ', 1, 1),
                      (DATA, 'Hello', 1, 5),
                      (SEPA, '\n', 1, 10),
                      (SEPA, '        ', 2, 1),
                      (CONT, '...', 2, 9),
                      (SEPA, '    ', 2, 12),
                      (DATA, 'world', 2, 16)])

    def test_leading_empty_with_pipes(self):
        verify_split('|  | Hello |\n| |  | ... | world',
                     [(SEPA, '|  ', 1, 1),
                      (DATA, '', 1, 4),
                      (SEPA, '| ', 1, 4),
                      (DATA, 'Hello', 1, 6),
                      (SEPA, ' |', 1, 11),
                      (SEPA, '\n', 1, 13),
                      (SEPA, '| ', 2, 1),
                      (SEPA, '|  ', 2, 3),
                      (SEPA, '| ', 2, 6),
                      (CONT, '...', 2, 8),
                      (SEPA, ' | ', 2, 11),
                      (DATA, 'world', 2, 14)])

    def test_pipes_with_empty_data(self):
        verify_split('| Hello |\n| ... |  | | world',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' |', 1, 8),
                      (SEPA, '\n', 1, 10),
                      (SEPA, '| ', 2, 1),
                      (CONT, '...', 2, 3),
                      (SEPA, ' |  ', 2, 6),
                      (DATA, '', 2, 10),
                      (SEPA, '| ', 2, 10),
                      (DATA, '', 2, 12),
                      (SEPA, '| ', 2, 12),
                      (DATA, 'world', 2, 14)])

    def test_multiple_lines(self):
        verify_split('1st\n...  continues\n2nd\n3rd\n    ...    3.1\n...  3.2',
                     [(DATA, '1st', 1, 1),
                      (SEPA, '\n', 1, 4),
                      (CONT, '...', 2, 1),
                      (SEPA, '  ', 2, 4),
                      (DATA, 'continues', 2, 6),
                      (SEPA, '\n', 2, 15)],
                     [(DATA, '2nd', 3, 1),
                      (SEPA, '\n', 3, 4)],
                     [(DATA, '3rd', 4, 1),
                      (SEPA, '\n', 4, 4),
                      (SEPA, '    ', 5, 1),
                      (CONT, '...', 5, 5),
                      (SEPA, '    ', 5, 8),
                      (DATA, '3.1', 5, 12),
                      (SEPA, '\n', 5, 15),
                      (CONT, '...', 6, 1),
                      (SEPA, '  ', 6, 4),
                      (DATA, '3.2', 6, 6)])

    def test_empty_lines_between(self):
        verify_split('Data\n\n\n...    continues',
                     [(DATA, 'Data', 1, 1),
                      (SEPA, '\n', 1, 5),
                      (SEPA, '\n', 2, 1),
                      (SEPA, '\n', 3, 1),
                      (CONT, '...', 4, 1),
                      (SEPA, '    ', 4, 4),
                      (DATA, 'continues', 4, 8)])

    def test_commented_lines_between(self):
        verify_split('Data\n# comment\n...    more data',
                     [(DATA, 'Data', 1, 1),
                      (SEPA, '\n', 1, 5),
                      (COMM, '# comment', 2, 1),
                      (SEPA, '\n', 2, 10),
                      (CONT, '...', 3, 1),
                      (SEPA, '    ', 3, 4),
                      (DATA, 'more data', 3, 8)])
        verify_split('Data\n        # comment\n...    more data',
                     [(DATA, 'Data', 1, 1),
                      (SEPA, '\n', 1, 5),
                      (SEPA, '        ', 2, 1),
                      (COMM, '# comment', 2, 9),
                      (SEPA, '\n', 2, 18),
                      (CONT, '...', 3, 1),
                      (SEPA, '    ', 3, 4),
                      (DATA, 'more data', 3, 8)])

    def test_commented_and_empty_lines_between(self):
        verify_split('Data\n# comment\n  \n|  |\n...  more\n#\n\n...   data',
                     [(DATA, 'Data', 1, 1),
                      (SEPA, '\n', 1, 5),
                      (COMM, '# comment', 2, 1),
                      (SEPA, '\n', 2, 10),
                      (SEPA, '  \n', 3, 1),
                      (SEPA, '|  ', 4, 1),
                      (SEPA, '|', 4, 4),
                      (SEPA, '\n', 4, 5),
                      (CONT, '...', 5, 1),
                      (SEPA, '  ', 5, 4),
                      (DATA, 'more', 5, 6),
                      (SEPA, '\n', 5, 10),
                      (COMM, '#', 6, 1),
                      (SEPA, '\n', 6, 2),
                      (SEPA, '\n', 7, 1),
                      (CONT, '...', 8, 1),
                      (SEPA, '   ', 8, 4),
                      (DATA, 'data', 8, 7)])

    def test_no_continuation_in_arguments(self):
        verify_split('Keyword    ...',
                     [(DATA, 'Keyword', 1, 1),
                      (SEPA, '    ', 1, 8),
                      (DATA, '...', 1, 12)])
        verify_split('Keyword\n...    ...',
                     [(DATA, 'Keyword', 1, 1),
                      (SEPA, '\n', 1, 8),
                      (CONT, '...', 2, 1),
                      (SEPA, '    ', 2, 4),
                      (DATA, '...', 2, 8)])

    def test_no_continuation_in_comment(self):
        verify_split('#    ...',
                     [(COMM, '#', 1, 1),
                      (SEPA, '    ', 1, 2),
                      (COMM, '...', 1, 6)])

    def test_line_with_only_continuation_marker_yields_empty_data_token(self):
        verify_split('Hello\n...\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (CONT, '...', 2, 1),
                      (DATA, '', 2, 4),    # this "virtual" token added
                      (SEPA, '\n', 2, 4)])
        verify_split('''\
Documentation    1st line.    Second column.
...              2nd line.
...
...              2nd paragraph.''',
                     [(DATA, 'Documentation', 1, 1),
                      (SEPA, '    ', 1, 14),
                      (DATA, '1st line.', 1, 18),
                      (SEPA, '    ', 1, 27),
                      (DATA, 'Second column.', 1, 31),
                      (SEPA, '\n', 1, 45),
                      (CONT, '...', 2, 1),
                      (SEPA, '              ', 2, 4),
                      (DATA, '2nd line.', 2, 18),
                      (SEPA, '\n', 2, 27),
                      (CONT, '...', 3, 1),
                      (DATA, '', 3, 4),
                      (SEPA, '\n', 3, 4),
                      (CONT, '...', 4, 1),
                      (SEPA, '              ', 4, 4),
                      (DATA, '2nd paragraph.', 4, 18)
                      ])
        verify_split('''\
Keyword
   ...
...    argh
...
''',
                     [(DATA, 'Keyword', 1, 1),
                      (SEPA, '\n', 1, 8),
                      (SEPA, '   ', 2, 1),
                      (CONT, '...', 2, 4),
                      (DATA, '', 2, 7),
                      (SEPA, '\n', 2, 7),
                      (CONT, '...', 3, 1),
                      (SEPA, '    ', 3, 4),
                      (DATA, 'argh', 3, 8),
                      (SEPA, '\n', 3, 12),
                      (CONT, '...', 4, 1),
                      (DATA, '', 4, 4),
                      (SEPA, '\n', 4, 4)])

    def test_line_with_only_continuation_marker_with_pipes(self):
        verify_split('Hello\n| ...\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (SEPA, '| ', 2, 1),
                      (CONT, '...', 2, 3),
                      (DATA, '', 2, 6),
                      (SEPA, '\n', 2, 6)])
        verify_split('Hello\n| ... |\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (SEPA, '| ', 2, 1),
                      (CONT, '...', 2, 3),
                      (DATA, '', 2, 6),
                      (SEPA, ' |', 2, 6),
                      (SEPA, '\n', 2, 8)])
        verify_split('Hello\n| ... | |\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (SEPA, '| ', 2, 1),
                      (CONT, '...', 2, 3),
                      (DATA, '', 2, 6),
                      (SEPA, ' | ', 2, 6),
                      (SEPA, '|', 2, 9),
                      (SEPA, '\n', 2, 10)])
        verify_split('Hello\n| | ... | |\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '\n', 1, 6),
                      (SEPA, '| ', 2, 1),
                      (SEPA, '| ', 2, 3),
                      (CONT, '...', 2, 5),
                      (DATA, '', 2, 8),
                      (SEPA, ' | ', 2, 8),
                      (SEPA, '|', 2, 11),
                      (SEPA, '\n', 2, 12)])


class TestComments(unittest.TestCase):

    def test_trailing_comment(self):
        verify_split('H#llo  # world',
                     [(DATA, 'H#llo', 1, 1),
                      (SEPA, '  ', 1, 6),
                      (COMM, '# world', 1, 8)])
        verify_split('| H#llo | # world',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'H#llo', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (COMM, '# world', 1, 11)])

    def test_separators(self):
        verify_split('Hello  # world    !!!\n',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '  ', 1, 6),
                      (COMM, '# world', 1, 8),
                      (SEPA, '    ', 1, 15),
                      (COMM, '!!!', 1, 19),
                      (SEPA, '\n', 1, 22)])
        verify_split('| Hello | # world | !!! |',
                     [(SEPA, '| ', 1, 1),
                      (DATA, 'Hello', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (COMM, '# world', 1, 11),
                      (SEPA, ' | ', 1, 18),
                      (COMM, '!!!', 1, 21),
                      (SEPA, ' |', 1, 24)])

    def test_empty_values(self):
        verify_split('| | Hello | | # world | | !!! |  |',
                     [(SEPA, '| ', 1, 1),
                      (DATA, '', 1, 3),
                      (SEPA, '| ', 1, 3),
                      (DATA, 'Hello', 1, 5),
                      (SEPA, ' | ', 1, 10),
                      (SEPA, '| ', 1, 13),
                      (COMM, '# world', 1, 15),
                      (SEPA, ' | ', 1, 22),
                      (SEPA, '| ', 1, 25),
                      (COMM, '!!!', 1, 27),
                      (SEPA, ' |  ', 1, 30),
                      (SEPA, '|', 1, 34)])

    def test_whole_line_comment(self):
        verify_split('# this is a comment',
                     [(COMM, '# this is a comment', 1, 1)])
        verify_split('#\n',
                     [(COMM, '#', 1, 1),
                      (SEPA, '\n', 1, 2)])
        verify_split('| #this | too',
                     [(SEPA, '| ', 1, 1),
                      (COMM, '#this', 1, 3),
                      (SEPA, ' | ', 1, 8),
                      (COMM, 'too', 1, 11)])

    def test_empty_data_before_whole_line_comment_removed(self):
        verify_split('    # this is a comment',
                     [(SEPA, '    ', 1, 1),
                      (COMM, '# this is a comment', 1, 5)])
        verify_split('  #\n',
                     [(SEPA, '  ', 1, 1),
                      (COMM, '#', 1, 3),
                      (SEPA, '\n', 1, 4)])
        verify_split('| | #this | too',
                     [(SEPA, '| ', 1, 1),
                      (SEPA, '| ', 1, 3),
                      (COMM, '#this', 1, 5),
                      (SEPA, ' | ', 1, 10),
                      (COMM, 'too', 1, 13)])

    def test_trailing_comment_with_continuation(self):
        verify_split('Hello    # comment\n...    world  # another comment',
                     [(DATA, 'Hello', 1, 1),
                      (SEPA, '    ', 1, 6),
                      (COMM, '# comment', 1, 10),
                      (SEPA, '\n', 1, 19),
                      (CONT, '...', 2, 1),
                      (SEPA, '    ', 2, 4),
                      (DATA, 'world', 2, 8),
                      (SEPA, '  ', 2, 13),
                      (COMM, '# another comment', 2, 15)])

    def test_multiline_comment(self):
        verify_split('# first\n# second\n    # third',
                     [(COMM, '# first', 1, 1),
                      (SEPA, '\n', 1, 8),
                      (COMM, '# second', 2, 1),
                      (SEPA, '\n', 2, 9),
                      (SEPA, '    ', 3, 1),
                      (COMM, '# third', 3, 5)])


if __name__ == '__main__':
    unittest.main()
