import unittest

from robot.utils.asserts import assert_equal

from robot.parsing.lexer.tokenizer import Tokenizer
from robot.parsing.lexer.tokens import Token


DATA = None
SEPA = Token.SEPARATOR
EOL = Token.EOL
CONT = Token.CONTINUATION
COMM = Token.COMMENT


def verify_split(string, *expected_statements, **config):
    expected_data = []
    actual_statements = list(Tokenizer().tokenize(string, **config))
    assert_equal(len(actual_statements), len(expected_statements))
    for tokens, expected in zip(actual_statements, expected_statements):
        expected_data.append([])
        assert_equal(len(tokens), len(expected),
                     'Expected %d tokens:\n%s\n\nGot %d tokens:\n%s'
                     % (len(expected), expected, len(tokens), tokens),
                     values=False)
        for act, exp in zip(tokens, expected):
            if exp[0] == DATA:
                expected_data[-1].append(exp)
            assert_equal(act, Token(*exp), formatter=repr)
    if not config:
        verify_split(string, *expected_data, data_only=True)


class TestSplitFromSpaces(unittest.TestCase):

    def test_basics(self):
        verify_split('Hello    world  !',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, '    ', 1, 5),
                      (DATA, 'world', 1, 9),
                      (SEPA, '  ', 1, 14),
                      (DATA, '!', 1, 16),
                      (EOL, '', 1, 17)])

    def test_newline(self):
        verify_split('Hello    my world  !\n',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, '    ', 1, 5),
                      (DATA, 'my world', 1, 9),
                      (SEPA, '  ', 1, 17),
                      (DATA, '!', 1, 19),
                      (EOL, '\n', 1, 20)])

    def test_internal_spaces(self):
        verify_split('I n t e r n a l  S p a c e s',
                     [(DATA, 'I n t e r n a l', 1, 0),
                      (SEPA, '  ', 1, 15),
                      (DATA, 'S p a c e s', 1, 17),
                      (EOL, '', 1, 28)])

    def test_single_tab_is_enough_as_separator(self):
        verify_split('\tT\ta\t\t\tb\t\t',
                     [(DATA, '', 1, 0),
                      (SEPA, '\t', 1, 0),
                      (DATA, 'T', 1, 1),
                      (SEPA, '\t', 1, 2),
                      (DATA, 'a', 1, 3),
                      (SEPA, '\t\t\t', 1, 4),
                      (DATA, 'b', 1, 7),
                      (EOL, '\t\t', 1, 8)])

    def test_trailing_spaces(self):
        verify_split('Hello  world   ',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, '  ', 1, 5),
                      (DATA, 'world', 1, 7),
                      (EOL, '   ', 1, 12)])

    def test_trailing_spaces_with_newline(self):
        verify_split('Hello  world   \n',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, '  ', 1, 5),
                      (DATA, 'world', 1, 7),
                      (EOL, '   \n', 1, 12)])

    def test_empty(self):
        verify_split('', [])
        verify_split('\n', [(EOL, '\n', 1, 0)])
        verify_split('  ', [(EOL, '  ', 1, 0)])
        verify_split('  \n', [(EOL, '  \n', 1, 0)])

    def test_multiline(self):
        verify_split('Hello  world\n    !!!\n',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, '  ', 1, 5),
                      (DATA, 'world', 1, 7),
                      (EOL, '\n', 1, 12)],
                     [(DATA, '', 2, 0),
                      (SEPA, '    ', 2, 0),
                      (DATA, '!!!', 2, 4),
                      (EOL, '\n', 2, 7)])

    def test_multiline_with_empty_lines(self):
        verify_split('Hello\n\nworld\n    \n!!!',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (EOL, '\n', 2, 0)],
                     [(DATA, 'world', 3, 0),
                      (EOL, '\n', 3, 5),
                      (EOL, '    \n', 4, 0)],
                     [(DATA, '!!!', 5, 0),
                      (EOL, '', 5, 3)])


class TestSplitFromPipes(unittest.TestCase):

    def test_basics(self):
        verify_split('| Hello | my world  |   ! |',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (SEPA, ' |', 1, 25),
                      (EOL, '', 1, 27)])

    def test_newline(self):
        verify_split('| Hello | my world  |   ! |\n',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (SEPA, ' |', 1, 25),
                      (EOL, '\n', 1, 27)])

    def test_internal_spaces(self):
        verify_split('| I n t e r n a l | S p a c e s',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'I n t e r n a l', 1, 2),
                      (SEPA, ' | ', 1, 17),
                      (DATA, 'S p a c e s', 1, 20),
                      (EOL, '', 1, 31)])

    def test_internal_consecutive_spaces(self):
        verify_split('| Consecutive    Spaces |    New  in  RF 3.2',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Consecutive    Spaces', 1, 2),
                      (SEPA, ' |    ', 1, 23),
                      (DATA, 'New  in  RF 3.2', 1, 29),
                      (EOL, '', 1, 44)])

    def test_tabs(self):
        verify_split('|\tT\ta\tb\ts\t\t\t|\t!\t|\t',
                     [(SEPA, '|\t', 1, 0),
                      (DATA, 'T\ta\tb\ts', 1, 2),
                      (SEPA, '\t\t\t|\t', 1, 9),
                      (DATA, '!', 1, 14),
                      (SEPA, '\t|', 1, 15),
                      (EOL, '\t', 1, 17)])

    def test_trailing_spaces(self):
        verify_split('| Hello | my world  |   ! |      ',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (SEPA, ' |', 1, 25),
                      (EOL, '      ', 1, 27)])

    def test_trailing_spaces_with_newline(self):
        verify_split('| Hello | my world  |   ! |      \n',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (SEPA, ' |', 1, 25),
                      (EOL, '      \n', 1, 27)])

    def test_empty(self):
        verify_split('|',
                     [(SEPA, '|', 1, 0),
                      (EOL, '', 1, 1)])
        verify_split('|\n',
                     [(SEPA, '|', 1, 0),
                      (EOL, '\n', 1, 1)])
        verify_split('|  ',
                     [(SEPA, '|', 1, 0),
                      (EOL, '  ', 1, 1)])
        verify_split('|  \n',
                     [(SEPA, '|', 1, 0),
                      (EOL, '  \n', 1, 1)])
        verify_split('| |  |        |',
                     [(SEPA, '| ', 1, 0),
                      (SEPA, '|  ', 1, 2),
                      (SEPA, '|        ', 1, 5),
                      (SEPA, '|', 1, 14),
                      (EOL, '', 1, 15)])

    def test_no_space_after(self):
        # Not actually splitting from pipes in this case.
        verify_split('||',
                     [(DATA, '||', 1, 0),
                      (EOL, '', 1, 2)])
        verify_split('|foo\n',
                     [(DATA, '|foo', 1, 0),
                      (EOL, '\n', 1, 4)])
        verify_split('|x  |    |',
                     [(DATA, '|x', 1, 0),
                      (SEPA, '  ', 1, 2),
                      (DATA, '|', 1, 4),
                      (SEPA, '    ', 1, 5),
                      (DATA, '|', 1, 9),
                      (EOL, '', 1, 10)])

    def test_no_pipe_at_end(self):
        verify_split('| Hello | my world  |   !',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (EOL, '', 1, 25)])

    def test_no_pipe_at_end_with_trailing_spaces(self):
        verify_split('| Hello | my world  |   !    ',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (EOL, '    ', 1, 25)])

    def test_no_pipe_at_end_with_newline(self):
        verify_split('| Hello | my world  |   !\n',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (EOL, '\n', 1, 25)])

    def test_no_pipe_at_end_with_trailing_spaces_and_newline(self):
        verify_split('| Hello | my world  |   !    \n',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'my world', 1, 10),
                      (SEPA, '  |   ', 1, 18),
                      (DATA, '!', 1, 24),
                      (EOL, '    \n', 1, 25)])

    def test_empty_internal_data(self):
        verify_split('| Hello |    | | world |',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' |    ', 1, 7),
                      (DATA, '', 1, 13),
                      (SEPA, '| ', 1, 13),
                      (DATA, '', 1, 15),
                      (SEPA, '| ', 1, 15),
                      (DATA, 'world', 1, 17),
                      (SEPA, ' |', 1, 22),
                      (EOL, '', 1, 24)])

    def test_trailing_empty_data_is_filtered(self):
        verify_split('| Hello |  |    | |    \n',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' |  ', 1, 7),
                      (SEPA, '|    ', 1, 11),
                      (SEPA, '| ', 1, 16),
                      (SEPA, '|', 1, 18),
                      (EOL, '    \n', 1, 19)])

    def test_multiline(self):
        verify_split('| Hello | world |\n| | !!!\n',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (DATA, 'world', 1, 10),
                      (SEPA, ' |', 1, 15),
                      (EOL, '\n', 1, 17)],
                     [(SEPA, '| ', 2, 0),
                      (DATA, '', 2, 2),
                      (SEPA, '| ', 2, 2),
                      (DATA, '!!!', 2, 4),
                      (EOL, '\n', 2, 7)])

    def test_multiline_with_empty_lines(self):
        verify_split('| Hello |\n|\n|  world\n|    |\n| !!!',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' |', 1, 7),
                      (EOL, '\n', 1, 9),
                      (SEPA, '|', 2, 0),
                      (EOL, '\n', 2, 1)],
                     [(SEPA, '|  ', 3, 0),
                      (DATA, 'world', 3, 3),
                      (EOL, '\n', 3, 8),
                      (SEPA, '|    ', 4, 0),
                      (SEPA, '|', 4, 5),
                      (EOL, '\n', 4, 6)],
                     [(SEPA, '| ', 5, 0),
                      (DATA, '!!!', 5, 2),
                      (EOL, '', 5, 5)])


class TestNonAsciiSpaces(unittest.TestCase):
    spaces = ('\N{NO-BREAK SPACE}\N{OGHAM SPACE MARK}\N{EN QUAD}'
              '\N{EM SPACE}\N{HAIR SPACE}\N{IDEOGRAPHIC SPACE}')
    data = '-' + '-'.join(spaces) + '-'

    def test_as_separator(self):
        s = self.spaces
        ls = len(s)
        verify_split(f'Hello{s}world\n{s}!!!{s}\n',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, s, 1, 5),
                      (DATA, 'world', 1, 5+ls),
                      (EOL, '\n', 1, 5+ls+5)],
                     [(DATA, '', 2, 0),
                      (SEPA, s, 2, 0),
                      (DATA, '!!!', 2, ls),
                      (EOL, s+'\n', 2, ls+3)])

    def test_as_separator_with_pipes(self):
        s = self.spaces
        ls = len(s)
        verify_split(f'|{s}Hello{s}world{s}|{s}!\n|{s}|{s}!!!{s}|{s}\n',
                     [(SEPA, '|'+s, 1, 0),
                      (DATA, 'Hello'+s+'world', 1, 1+ls),
                      (SEPA, s+'|'+s, 1, 1+ls+5+ls+5),
                      (DATA, '!', 1, 1+ls+5+ls+5+ls+1+ls),
                      (EOL, '\n', 1, 1+ls+5+ls+5+ls+1+ls+1)],
                     [(SEPA, '|'+s, 2, 0),
                      (DATA, '', 2, 1+ls),
                      (SEPA, '|'+s, 2, 1+ls),
                      (DATA, '!!!', 2, 1+ls+1+ls),
                      (SEPA, s+'|', 2, 1+ls+1+ls+3),
                      (EOL, s+'\n', 2, 1+ls+1+ls+3+ls+1)])

    def test_in_data(self):
        d = self.data
        s = self.spaces
        ld = len(d)
        ls = len(s)
        verify_split(f'{d}{s}{d}{s}{d}',
                     [(DATA, d, 1, 0),
                      (SEPA, s, 1, ld),
                      (DATA, d, 1, ld+ls),
                      (SEPA, s, 1, ld+ls+ld),
                      (DATA, d, 1, ld+ls+ld+ls),
                      (EOL, '', 1, ld+ls+ld+ls+ld)])

    def test_in_data_with_pipes(self):
        d = self.data
        s = self.spaces
        ld = len(d)
        ls = len(s)
        verify_split(f'|{s}{d}{s}|{s}{d}',
                     [(SEPA, '|'+s, 1, 0),
                      (DATA, d, 1, 1+ls),
                      (SEPA, s+'|'+s, 1, 1+ls+ld),
                      (DATA, d, 1, 1+ls+ld+ls+1+ls),
                      (EOL, '', 1, 1+ls+ld+ls+1+ls+ld)])


class TestContinuation(unittest.TestCase):

    def test_spaces(self):
        verify_split('Hello\n...    world',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (CONT, '...', 2, 0),
                      (SEPA, '    ', 2, 3),
                      (DATA, 'world', 2, 7),
                      (EOL, '', 2, 12)])

    def test_pipes(self):
        verify_split('| Hello |\n| ... | world',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' |', 1, 7),
                      (EOL, '\n', 1, 9),
                      (SEPA, '| ', 2, 0),
                      (CONT, '...', 2, 2),
                      (SEPA, ' | ', 2, 5),
                      (DATA, 'world', 2, 8),
                      (EOL, '', 2, 13)])

    def test_mixed(self):
        verify_split('Hello\n| ... | world\n...   ...\n',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (SEPA, '| ', 2, 0),
                      (CONT, '...', 2, 2),
                      (SEPA, ' | ', 2, 5),
                      (DATA, 'world', 2, 8),
                      (EOL, '\n', 2, 13),
                      (CONT, '...', 3, 0),
                      (SEPA, '   ', 3, 3),
                      (DATA, '...', 3, 6),
                      (EOL, '\n', 3, 9)])

    def test_leading_empty_with_spaces(self):
        verify_split('    Hello\n        ...    world',
                     [(DATA, '', 1, 0),
                      (SEPA, '    ', 1, 0),
                      (DATA, 'Hello', 1, 4),
                      (EOL, '\n', 1, 9),
                      (SEPA, '        ', 2, 0),
                      (CONT, '...', 2, 8),
                      (SEPA, '    ', 2, 11),
                      (DATA, 'world', 2, 15),
                      (EOL, '', 2, 20)])
        verify_split('    Hello\n        ...    world      ',
                     [(DATA, '', 1, 0),
                      (SEPA, '    ', 1, 0),
                      (DATA, 'Hello', 1, 4),
                      (EOL, '\n', 1, 9),
                      (SEPA, '        ', 2, 0),
                      (CONT, '...', 2, 8),
                      (SEPA, '    ', 2, 11),
                      (DATA, 'world', 2, 15),
                      (EOL, '      ', 2, 20)])

    def test_leading_empty_with_pipes(self):
        verify_split('|  | Hello |\n| |  | ... | world',
                     [(SEPA, '|  ', 1, 0),
                      (DATA, '', 1, 3),
                      (SEPA, '| ', 1, 3),
                      (DATA, 'Hello', 1, 5),
                      (SEPA, ' |', 1, 10),
                      (EOL, '\n', 1, 12),
                      (SEPA, '| ', 2, 0),
                      (SEPA, '|  ', 2, 2),
                      (SEPA, '| ', 2, 5),
                      (CONT, '...', 2, 7),
                      (SEPA, ' | ', 2, 10),
                      (DATA, 'world', 2, 13),
                      (EOL, '', 2, 18)])
        verify_split('|  | Hello |\n| |  | ... | world       ',
                     [(SEPA, '|  ', 1, 0),
                      (DATA, '', 1, 3),
                      (SEPA, '| ', 1, 3),
                      (DATA, 'Hello', 1, 5),
                      (SEPA, ' |', 1, 10),
                      (EOL, '\n', 1, 12),
                      (SEPA, '| ', 2, 0),
                      (SEPA, '|  ', 2, 2),
                      (SEPA, '| ', 2, 5),
                      (CONT, '...', 2, 7),
                      (SEPA, ' | ', 2, 10),
                      (DATA, 'world', 2, 13),
                      (EOL, '       ', 2, 18)])

    def test_pipes_with_empty_data(self):
        verify_split('| Hello |\n| ... |  | | world',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' |', 1, 7),
                      (EOL, '\n', 1, 9),
                      (SEPA, '| ', 2, 0),
                      (CONT, '...', 2, 2),
                      (SEPA, ' |  ', 2, 5),
                      (DATA, '', 2, 9),
                      (SEPA, '| ', 2, 9),
                      (DATA, '', 2, 11),
                      (SEPA, '| ', 2, 11),
                      (DATA, 'world', 2, 13),
                      (EOL, '', 2, 18)])

    def test_multiple_lines(self):
        verify_split('1st\n...  continues\n2nd\n3rd\n    ...    3.1\n...  3.2',
                     [(DATA, '1st', 1, 0),
                      (EOL, '\n', 1, 3),
                      (CONT, '...', 2, 0),
                      (SEPA, '  ', 2, 3),
                      (DATA, 'continues', 2, 5),
                      (EOL, '\n', 2, 14)],
                     [(DATA, '2nd', 3, 0),
                      (EOL, '\n', 3, 3)],
                     [(DATA, '3rd', 4, 0),
                      (EOL, '\n', 4, 3),
                      (SEPA, '    ', 5, 0),
                      (CONT, '...', 5, 4),
                      (SEPA, '    ', 5, 7),
                      (DATA, '3.1', 5, 11),
                      (EOL, '\n', 5, 14),
                      (CONT, '...', 6, 0),
                      (SEPA, '  ', 6, 3),
                      (DATA, '3.2', 6, 5),
                      (EOL, '', 6, 8)])

    def test_empty_lines_between(self):
        verify_split('Data\n\n\n...    continues',
                     [(DATA, 'Data', 1, 0),
                      (EOL, '\n', 1, 4),
                      (EOL, '\n', 2, 0),
                      (EOL, '\n', 3, 0),
                      (CONT, '...', 4, 0),
                      (SEPA, '    ', 4, 3),
                      (DATA, 'continues', 4, 7),
                      (EOL, '', 4, 16)])

    def test_commented_lines_between(self):
        verify_split('Data\n# comment\n...    more data',
                     [(DATA, 'Data', 1, 0),
                      (EOL, '\n', 1, 4),
                      (COMM, '# comment', 2, 0),
                      (EOL, '\n', 2, 9),
                      (CONT, '...', 3, 0),
                      (SEPA, '    ', 3, 3),
                      (DATA, 'more data', 3, 7),
                      (EOL, '', 3, 16)])
        verify_split('Data\n        # comment\n...    more data',
                     [(DATA, 'Data', 1, 0),
                      (EOL, '\n', 1, 4),
                      (SEPA, '        ', 2, 0),
                      (COMM, '# comment', 2, 8),
                      (EOL, '\n', 2, 17),
                      (CONT, '...', 3, 0),
                      (SEPA, '    ', 3, 3),
                      (DATA, 'more data', 3, 7),
                      (EOL, '', 3, 16)])

    def test_commented_and_empty_lines_between(self):
        verify_split('Data\n# comment\n  \n|  |\n...  more\n#\n\n...   data',
                     [(DATA, 'Data', 1, 0),
                      (EOL, '\n', 1, 4),
                      (COMM, '# comment', 2, 0),
                      (EOL, '\n', 2, 9),
                      (EOL, '  \n', 3, 0),
                      (SEPA, '|  ', 4, 0),
                      (SEPA, '|', 4, 3),
                      (EOL, '\n', 4, 4),
                      (CONT, '...', 5, 0),
                      (SEPA, '  ', 5, 3),
                      (DATA, 'more', 5, 5),
                      (EOL, '\n', 5, 9),
                      (COMM, '#', 6, 0),
                      (EOL, '\n', 6, 1),
                      (EOL, '\n', 7, 0),
                      (CONT, '...', 8, 0),
                      (SEPA, '   ', 8, 3),
                      (DATA, 'data', 8, 6),
                      (EOL, '', 8, 10)])

    def test_no_continuation_in_arguments(self):
        verify_split('Keyword    ...',
                     [(DATA, 'Keyword', 1, 0),
                      (SEPA, '    ', 1, 7),
                      (DATA, '...', 1, 11),
                      (EOL, '', 1, 14)])
        verify_split('Keyword\n...    ...',
                     [(DATA, 'Keyword', 1, 0),
                      (EOL, '\n', 1, 7),
                      (CONT, '...', 2, 0),
                      (SEPA, '    ', 2, 3),
                      (DATA, '...', 2, 7),
                      (EOL, '', 2, 10)])

    def test_no_continuation_in_comment(self):
        verify_split('#    ...',
                     [(COMM, '#', 1, 0),
                      (SEPA, '    ', 1, 1),
                      (COMM, '...', 1, 5),
                      (EOL, '', 1, 8)])

    def test_line_with_only_continuation_marker_yields_empty_data_token(self):
        verify_split('Hello\n...\n',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (CONT, '...', 2, 0),
                      (DATA, '', 2, 3),    # this "virtual" token added
                      (EOL, '\n', 2, 3)])
        verify_split('''\
Documentation    1st line.    Second column.
...              2nd line.
...
...              2nd paragraph.''',
                     [(DATA, 'Documentation', 1, 0),
                      (SEPA, '    ', 1, 13),
                      (DATA, '1st line.', 1, 17),
                      (SEPA, '    ', 1, 26),
                      (DATA, 'Second column.', 1, 30),
                      (EOL, '\n', 1, 44),
                      (CONT, '...', 2, 0),
                      (SEPA, '              ', 2, 3),
                      (DATA, '2nd line.', 2, 17),
                      (EOL, '\n', 2, 26),
                      (CONT, '...', 3, 0),
                      (DATA, '', 3, 3),
                      (EOL, '\n', 3, 3),
                      (CONT, '...', 4, 0),
                      (SEPA, '              ', 4, 3),
                      (DATA, '2nd paragraph.', 4, 17),
                      (EOL, '', 4, 31)])
        verify_split('''\
Keyword
   ...
...    argh
...
''',
                     [(DATA, 'Keyword', 1, 0),
                      (EOL, '\n', 1, 7),
                      (SEPA, '   ', 2, 0),
                      (CONT, '...', 2, 3),
                      (DATA, '', 2, 6),
                      (EOL, '\n', 2, 6),
                      (CONT, '...', 3, 0),
                      (SEPA, '    ', 3, 3),
                      (DATA, 'argh', 3, 7),
                      (EOL, '\n', 3, 11),
                      (CONT, '...', 4, 0),
                      (DATA, '', 4, 3),
                      (EOL, '\n', 4, 3)])

    def test_line_with_only_continuation_marker_with_pipes(self):
        verify_split('Hello\n| ...\n',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (SEPA, '| ', 2, 0),
                      (CONT, '...', 2, 2),
                      (DATA, '', 2, 5),
                      (EOL, '\n', 2, 5)])
        verify_split('Hello\n| ... |\n',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (SEPA, '| ', 2, 0),
                      (CONT, '...', 2, 2),
                      (DATA, '', 2, 5),
                      (SEPA, ' |', 2, 5),
                      (EOL, '\n', 2, 7)])
        verify_split('Hello\n| ... | |\n',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (SEPA, '| ', 2, 0),
                      (CONT, '...', 2, 2),
                      (DATA, '', 2, 5),
                      (SEPA, ' | ', 2, 5),
                      (SEPA, '|', 2, 8),
                      (EOL, '\n', 2, 9)])
        verify_split('Hello\n| | ... | |\n',
                     [(DATA, 'Hello', 1, 0),
                      (EOL, '\n', 1, 5),
                      (SEPA, '| ', 2, 0),
                      (SEPA, '| ', 2, 2),
                      (CONT, '...', 2, 4),
                      (DATA, '', 2, 7),
                      (SEPA, ' | ', 2, 7),
                      (SEPA, '|', 2, 10),
                      (EOL, '\n', 2, 11)])


class TestComments(unittest.TestCase):

    def test_trailing_comment(self):
        verify_split('H#llo  # world',
                     [(DATA, 'H#llo', 1, 0),
                      (SEPA, '  ', 1, 5),
                      (COMM, '# world', 1, 7),
                      (EOL, '', 1, 14)])
        verify_split('| H#llo | # world',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'H#llo', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (COMM, '# world', 1, 10),
                      (EOL, '', 1, 17)])

    def test_separators(self):
        verify_split('Hello  # world    !!!\n',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, '  ', 1, 5),
                      (COMM, '# world', 1, 7),
                      (SEPA, '    ', 1, 14),
                      (COMM, '!!!', 1, 18),
                      (EOL, '\n', 1, 21)])
        verify_split('| Hello | # world | !!! |',
                     [(SEPA, '| ', 1, 0),
                      (DATA, 'Hello', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (COMM, '# world', 1, 10),
                      (SEPA, ' | ', 1, 17),
                      (COMM, '!!!', 1, 20),
                      (SEPA, ' |', 1, 23),
                      (EOL, '', 1, 25)])

    def test_empty_values(self):
        verify_split('| | Hello | | # world | | !!! |  |',
                     [(SEPA, '| ', 1, 0),
                      (DATA, '', 1, 2),
                      (SEPA, '| ', 1, 2),
                      (DATA, 'Hello', 1, 4),
                      (SEPA, ' | ', 1, 9),
                      (SEPA, '| ', 1, 12),
                      (COMM, '# world', 1, 14),
                      (SEPA, ' | ', 1, 21),
                      (SEPA, '| ', 1, 24),
                      (COMM, '!!!', 1, 26),
                      (SEPA, ' |  ', 1, 29),
                      (SEPA, '|', 1, 33),
                      (EOL, '', 1, 34)])

    def test_whole_line_comment(self):
        verify_split('# this is a comment',
                     [(COMM, '# this is a comment', 1, 0),
                      (EOL, '', 1, 19)])
        verify_split('#\n',
                     [(COMM, '#', 1, 0),
                      (EOL, '\n', 1, 1)])
        verify_split('| #this | too',
                     [(SEPA, '| ', 1, 0),
                      (COMM, '#this', 1, 2),
                      (SEPA, ' | ', 1, 7),
                      (COMM, 'too', 1, 10),
                      (EOL, '', 1, 13)])

    def test_empty_data_before_whole_line_comment_removed(self):
        verify_split('    # this is a comment',
                     [(SEPA, '    ', 1, 0),
                      (COMM, '# this is a comment', 1, 4),
                      (EOL, '', 1, 23)])
        verify_split('  #\n',
                     [(SEPA, '  ', 1, 0),
                      (COMM, '#', 1, 2),
                      (EOL, '\n', 1, 3)])
        verify_split('| | #this | too',
                     [(SEPA, '| ', 1, 0),
                      (SEPA, '| ', 1, 2),
                      (COMM, '#this', 1, 4),
                      (SEPA, ' | ', 1, 9),
                      (COMM, 'too', 1, 12),
                      (EOL, '', 1, 15)])

    def test_trailing_comment_with_continuation(self):
        verify_split('Hello    # comment\n...    world  # another comment',
                     [(DATA, 'Hello', 1, 0),
                      (SEPA, '    ', 1, 5),
                      (COMM, '# comment', 1, 9),
                      (EOL, '\n', 1, 18),
                      (CONT, '...', 2, 0),
                      (SEPA, '    ', 2, 3),
                      (DATA, 'world', 2, 7),
                      (SEPA, '  ', 2, 12),
                      (COMM, '# another comment', 2, 14),
                      (EOL, '', 2, 31)])

    def test_multiline_comment(self):
        verify_split('# first\n# second\n    # third',
                     [(COMM, '# first', 1, 0),
                      (EOL, '\n', 1, 7),
                      (COMM, '# second', 2, 0),
                      (EOL, '\n', 2, 8),
                      (SEPA, '    ', 3, 0),
                      (COMM, '# third', 3, 4),
                      (EOL, '', 3, 11)])

    def test_leading_spaces(self):
        verify_split('# no spaces',
                     [(COMM, '# no spaces', 1, 0),
                      (EOL, '', 1, 11)])
        verify_split(' # one space',
                     [(COMM, ' # one space', 1, 0),
                      (EOL, '', 1, 12)])
        verify_split('  # two spaces',
                     [(SEPA, '  ', 1, 0),
                      (COMM, '# two spaces', 1, 2),
                      (EOL, '', 1, 14)])
        verify_split('   # three spaces',
                     [(SEPA, '   ', 1, 0),
                      (COMM, '# three spaces', 1, 3),
                      (EOL, '', 1, 17)])


if __name__ == '__main__':
    unittest.main()
