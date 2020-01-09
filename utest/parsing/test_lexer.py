from io import StringIO
import os
import unittest
import tempfile

from robot.utils import PY3
from robot.utils.asserts import assert_equal

from robot.parsing import get_tokens, get_resource_tokens, Token


T = Token


def assert_tokens(source, expected, get_tokens=get_tokens, data_only=False):
    tokens = list(get_tokens(source, data_only))
    assert_equal(len(tokens), len(expected),
                 'Expected %d tokens:\n%s\n\nGot %d tokens:\n%s'
                 % (len(expected), expected, len(tokens), tokens),
                 values=False)
    for act, exp in zip(tokens, expected):
        exp = Token(*exp)
        assert_equal(act.type, exp.type)
        assert_equal(act.value, exp.value, formatter=repr)
        assert_equal(act.lineno, exp.lineno)
        assert_equal(act.col_offset, exp.col_offset)
        assert_equal(act.end_col_offset, exp.col_offset + len(exp.value))


class TestName(unittest.TestCase):

    def test_name_on_own_row(self):
        self._verify('My Name',
                     [(T.NAME, 'My Name', 2, 0), (T.EOL, '', 2, 7), (T.EOS, '', 2, 7)])
        self._verify('My Name    ',
                     [(T.NAME, 'My Name', 2, 0), (T.EOL, '    ', 2, 7), (T.EOS, '', 2, 11)])
        self._verify('My Name\n    Keyword',
                     [(T.NAME, 'My Name', 2, 0), (T.EOL, '\n', 2, 7), (T.EOS, '', 2, 8),
                      (T.SEPARATOR, '    ', 3, 0), (T.KEYWORD, 'Keyword', 3, 4), (T.EOL, '', 3, 11), (T.EOS, '', 3, 11)])
        self._verify('My Name  \n    Keyword',
                     [(T.NAME, 'My Name', 2, 0), (T.EOL, '  \n', 2, 7), (T.EOS, '', 2, 10),
                      (T.SEPARATOR, '    ', 3, 0), (T.KEYWORD, 'Keyword', 3, 4), (T.EOL, '', 3, 11), (T.EOS, '', 3, 11)])

    def test_name_and_keyword_on_same_row(self):
        self._verify('Name    Keyword',
                     [(T.NAME, 'Name', 2, 0), (T.EOS, '', 2, 4), (T.SEPARATOR, '    ', 2, 4),
                      (T.KEYWORD, 'Keyword', 2, 8), (T.EOL, '', 2, 15), (T.EOS, '', 2, 15)])
        self._verify('N  K  A',
                     [(T.NAME, 'N', 2, 0), (T.EOS, '', 2, 1), (T.SEPARATOR, '  ', 2, 1),
                      (T.KEYWORD, 'K', 2, 3), (T.SEPARATOR, '  ', 2, 4),
                      (T.ARGUMENT, 'A', 2, 6), (T.EOL, '', 2, 7), (T.EOS, '', 2, 7)])
        self._verify('N  ${v}=  K',
                     [(T.NAME, 'N', 2, 0), (T.EOS, '', 2, 1), (T.SEPARATOR, '  ', 2, 1),
                      (T.ASSIGN, '${v}=', 2, 3), (T.SEPARATOR, '  ', 2, 8),
                      (T.KEYWORD, 'K', 2, 10), (T.EOL, '', 2, 11), (T.EOS, '', 2, 11)])

    def test_name_and_setting_on_same_row(self):
        self._verify('Name    [Documentation]    The doc.',
                     [(T.NAME, 'Name', 2, 0), (T.EOS, '', 2, 4), (T.SEPARATOR, '    ', 2, 4),
                      (T.DOCUMENTATION, '[Documentation]', 2, 8), (T.SEPARATOR, '    ', 2, 23),
                      (T.ARGUMENT, 'The doc.', 2, 27), (T.EOL, '', 2, 35), (T.EOS, '', 2, 35)])

    def _verify(self, data, tokens):
        assert_tokens('*** Test Cases ***\n' + data,
                      [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                       (T.EOL, '\n', 1, 18),
                       (T.EOS, '', 1, 19)] + tokens)
        assert_tokens('*** Keywords ***\n' + data,
                      [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                       (T.EOL, '\n', 1, 16),
                       (T.EOS, '', 1, 17)] + tokens,
                      get_tokens=get_resource_tokens)


class TestNameWithPipes(unittest.TestCase):

    def test_name_on_own_row(self):
        self._verify('| My Name',
                     [(T.SEPARATOR, '| ', 2, 0), (T.NAME, 'My Name', 2, 2), (T.EOL, '', 2, 9), (T.EOS, '', 2, 9)])
        self._verify('| My Name |',
                     [(T.SEPARATOR, '| ', 2, 0), (T.NAME, 'My Name', 2, 2), (T.SEPARATOR, ' |', 2, 9), (T.EOL, '', 2, 11), (T.EOS, '', 2, 11)])
        self._verify('| My Name | ',
                     [(T.SEPARATOR, '| ', 2, 0), (T.NAME, 'My Name', 2, 2), (T.SEPARATOR, ' |', 2, 9), (T.EOL, ' ', 2, 11), (T.EOS, '', 2, 12)])

    def test_name_and_keyword_on_same_row(self):
        self._verify('| Name | Keyword',
                     [(T.SEPARATOR, '| ', 2, 0), (T.NAME, 'Name', 2, 2), (T.EOS, '', 2, 6),
                      (T.SEPARATOR, ' | ', 2, 6), (T.KEYWORD, 'Keyword', 2, 9), (T.EOL, '', 2, 16), (T.EOS, '', 2, 16)])
        self._verify('| N | K | A |\n',
                     [(T.SEPARATOR, '| ', 2, 0), (T.NAME, 'N', 2, 2), (T.EOS, '', 2, 3),
                      (T.SEPARATOR, ' | ', 2, 3), (T.KEYWORD, 'K', 2, 6), (T.SEPARATOR, ' | ', 2, 7),
                      (T.ARGUMENT, 'A', 2, 10), (T.SEPARATOR, ' |', 2, 11), (T.EOL, '\n', 2, 13), (T.EOS, '', 2, 14)])
        self._verify('|    N  |  ${v} =    |    K    ',
                     [(T.SEPARATOR, '|    ', 2, 0), (T.NAME, 'N', 2, 5), (T.EOS, '', 2, 6),
                      (T.SEPARATOR, '  |  ', 2, 6), (T.ASSIGN, '${v} =', 2, 11), (T.SEPARATOR, '    |    ', 2, 17),
                      (T.KEYWORD, 'K', 2, 26), (T.EOL, '    ', 2, 27), (T.EOS, '', 2, 31)])

    def test_name_and_setting_on_same_row(self):
        self._verify('| Name | [Documentation] | The doc.',
                     [(T.SEPARATOR, '| ', 2, 0), (T.NAME, 'Name', 2, 2), (T.EOS, '', 2, 6), (T.SEPARATOR, ' | ', 2, 6),
                      (T.DOCUMENTATION, '[Documentation]', 2, 9), (T.SEPARATOR, ' | ', 2, 24),
                      (T.ARGUMENT, 'The doc.', 2, 27), (T.EOL, '', 2, 35), (T.EOS, '', 2, 35)])

    def _verify(self, data, tokens):
        assert_tokens('*** Test Cases ***\n' + data,
                      [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                       (T.EOL, '\n', 1, 18),
                       (T.EOS, '', 1, 19)] + tokens)
        assert_tokens('*** Keywords ***\n' + data,
                      [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                       (T.EOL, '\n', 1, 16),
                       (T.EOS, '', 1, 17)] + tokens,
                      get_tokens=get_resource_tokens)


class TestCommentRowsAndEmptyRows(unittest.TestCase):

    def test_between_names(self):
        self._verify('Name\n#Comment\n\nName 2',
                     [(T.NAME, 'Name', 2, 0),
                      (T.EOL, '\n', 2, 4),
                      (T.EOS, '', 2, 5),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.EOL, '\n', 4, 0),
                      (T.EOS, '', 4, 1),
                      (T.NAME, 'Name 2', 5, 0),
                      (T.EOL, '', 5, 6),
                      (T.EOS, '', 5, 6)])

    def test_leading(self):
        self._verify('\n#Comment\n\nName',
                     [(T.EOL, '\n', 2, 0),
                      (T.EOS, '', 2, 1),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.EOL, '\n', 4, 0),
                      (T.EOS, '', 4, 1),
                      (T.NAME, 'Name', 5, 0),
                      (T.EOL, '', 5, 4),
                      (T.EOS, '', 5, 4)])

    def test_trailing(self):
        self._verify('Name\n#Comment\n\n',
                     [(T.NAME, 'Name', 2, 0),
                      (T.EOL, '\n', 2, 4),
                      (T.EOS, '', 2, 5),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.EOL, '\n', 4, 0),
                      (T.EOS, '', 4, 1)])
        self._verify('Name\n#Comment\n# C2\n\n',
                     [(T.NAME, 'Name', 2, 0),
                      (T.EOL, '\n', 2, 4),
                      (T.EOS, '', 2, 5),
                      (T.COMMENT, '#Comment', 3, 0),
                      (T.EOL, '\n', 3, 8),
                      (T.EOS, '', 3, 9),
                      (T.COMMENT, '# C2', 4, 0),
                      (T.EOL, '\n', 4, 4),
                      (T.EOS, '', 4, 5),
                      (T.EOL, '\n', 5, 0),
                      (T.EOS, '', 5, 1)])

    def test_on_their_own(self):
        self._verify('\n',
                     [(T.EOL, '\n', 2, 0),
                      (T.EOS, '', 2, 1)])
        self._verify('# comment',
                     [(T.COMMENT, '# comment', 2, 0),
                      (T.EOL, '', 2, 9),
                      (T.EOS, '', 2, 9)])
        self._verify('\n#\n#',
                     [(T.EOL, '\n', 2, 0),
                      (T.EOS, '', 2, 1),
                      (T.COMMENT, '#', 3, 0),
                      (T.EOL, '\n', 3, 1),
                      (T.EOS, '', 3, 2),
                      (T.COMMENT, '#', 4, 0),
                      (T.EOL, '', 4, 1),
                      (T.EOS, '', 4, 1)])

    def _verify(self, data, tokens):
        assert_tokens('*** Test Cases ***\n' + data,
                      [(T.TESTCASE_HEADER, '*** Test Cases ***', 1, 0),
                       (T.EOL, '\n', 1, 18),
                       (T.EOS, '', 1, 19)] + tokens)
        assert_tokens('*** Keywords ***\n' + data,
                      [(T.KEYWORD_HEADER, '*** Keywords ***', 1, 0),
                       (T.EOL, '\n', 1, 16),
                       (T.EOS, '', 1, 17)] + tokens,
                      get_tokens=get_resource_tokens)


class TestGetTokensSourceFormats(unittest.TestCase):
    path = os.path.join(os.getenv('TEMPDIR') or tempfile.gettempdir(),
                        'test_lexer.robot')
    data = u'''\
*** Settings ***
Library         Easter

*** Test Cases ***
Example
    None shall pass    ${NONE}
'''
    tokens = [
        (T.SETTING_HEADER, '*** Settings ***', 1, 0),
        (T.EOL, '\n', 1, 16),
        (T.EOS, '', 1, 17),
        (T.LIBRARY, 'Library', 2, 0),
        (T.SEPARATOR, '         ', 2, 7),
        (T.ARGUMENT, 'Easter', 2, 16),
        (T.EOL, '\n', 2, 22),
        (T.EOS, '', 2, 23),
        (T.EOL, '\n', 3, 0),
        (T.EOS, '', 3, 1),
        (T.TESTCASE_HEADER, '*** Test Cases ***', 4, 0),
        (T.EOL, '\n', 4, 18),
        (T.EOS, '', 4, 19),
        (T.NAME, 'Example', 5, 0),
        (T.EOL, '\n', 5, 7),
        (T.EOS, '', 5, 8),
        (T.SEPARATOR, '    ', 6, 0),
        (T.KEYWORD, 'None shall pass', 6, 4),
        (T.SEPARATOR, '    ', 6, 19),
        (T.ARGUMENT, '${NONE}', 6, 23),
        (T.EOL, '\n', 6, 30),
        (T.EOS, '', 6, 31)
    ]
    data_tokens = [
        (T.SETTING_HEADER, '*** Settings ***', 1, 0),
        (T.EOS, '', 1, 16),
        (T.LIBRARY, 'Library', 2, 0),
        (T.ARGUMENT, 'Easter', 2, 16),
        (T.EOS, '', 2, 22),
        (T.TESTCASE_HEADER, '*** Test Cases ***', 4, 0),
        (T.EOS, '', 4, 18),
        (T.NAME, 'Example', 5, 0),
        (T.EOS, '', 5, 7),
        (T.KEYWORD, 'None shall pass', 6, 4),
        (T.ARGUMENT, '${NONE}', 6, 23),
        (T.EOS, '', 6, 30)
    ]

    @classmethod
    def setUpClass(cls):
        with open(cls.path, 'w') as f:
            f.write(cls.data)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.path)

    def test_string_path(self):
        self._verify(self.path)
        self._verify(self.path, data_only=True)

    if PY3:

        def test_pathlib_path(self):
            from pathlib import Path
            self._verify(Path(self.path))
            self._verify(Path(self.path), data_only=True)

    def test_open_file(self):
        with open(self.path) as f:
            self._verify(f)
        with open(self.path) as f:
            self._verify(f, data_only=True)

    def test_string_io(self):
        self._verify(StringIO(self.data))
        self._verify(StringIO(self.data), data_only=True)

    def test_string(self):
        self._verify(self.data)
        self._verify(self.data, data_only=True)

    def _verify(self, source, data_only=False):
        expected = self.data_tokens if data_only else self.tokens
        assert_tokens(source, expected, data_only=data_only)


class TestGetResourceTokensSourceFormats(TestGetTokensSourceFormats):
    data = u'''\
*** Variable ***
${VAR}    Value

*** KEYWORD ***
NOOP    No Operation
'''
    tokens = [
        (T.VARIABLE_HEADER, '*** Variable ***', 1, 0),
        (T.EOL, '\n', 1, 16),
        (T.EOS, '', 1, 17),
        (T.VARIABLE, '${VAR}', 2, 0),
        (T.SEPARATOR, '    ', 2, 6),
        (T.ARGUMENT, 'Value', 2, 10),
        (T.EOL, '\n', 2, 15),
        (T.EOS, '', 2, 16),
        (T.EOL, '\n', 3, 0),
        (T.EOS, '', 3, 1),
        (T.KEYWORD_HEADER, '*** KEYWORD ***', 4, 0),
        (T.EOL, '\n', 4, 15),
        (T.EOS, '', 4, 16),
        (T.NAME, 'NOOP', 5, 0),
        (T.EOS, '', 5, 4),
        (T.SEPARATOR, '    ', 5, 4),
        (T.KEYWORD, 'No Operation', 5, 8),
        (T.EOL, '\n', 5, 20),
        (T.EOS, '', 5, 21)
    ]
    data_tokens = [
        (T.VARIABLE_HEADER, '*** Variable ***', 1, 0),
        (T.EOS, '', 1, 16),
        (T.VARIABLE, '${VAR}', 2, 0),
        (T.ARGUMENT, 'Value', 2, 10),
        (T.EOS, '', 2, 15),
        (T.KEYWORD_HEADER, '*** KEYWORD ***', 4, 0),
        (T.EOS, '', 4, 15),
        (T.NAME, 'NOOP', 5, 0),
        (T.EOS, '', 5, 4),
        (T.KEYWORD, 'No Operation', 5, 8),
        (T.EOS, '', 5, 20)
    ]

    def _verify(self, source, data_only=False):
        expected = self.data_tokens if data_only else self.tokens
        assert_tokens(source, expected, get_tokens=get_resource_tokens,
                      data_only=data_only)


if __name__ == '__main__':
    unittest.main()
