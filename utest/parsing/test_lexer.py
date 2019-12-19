from io import StringIO
import os
import unittest
import tempfile

from robot.utils.asserts import assert_equal

from robot.parsing import get_tokens, get_resource_tokens, Token


T = Token


def assert_tokens(tokens, expected):
    assert_equal(len(tokens), len(expected))
    for act, exp in zip(tokens, expected):
        exp = Token(*exp)
        assert_equal(act.type, exp.type)
        assert_equal(act.value, exp.value)
        assert_equal(act.lineno, exp.lineno)
        assert_equal(act.columnno, exp.columnno)


class SourceFormatsTestBase(unittest.TestCase):
    data = None
    tokens = None
    path = os.path.join(os.getenv('TEMPDIR') or tempfile.gettempdir(),
                        'test_lexer.robot')

    @classmethod
    def setUpClass(cls):
        with open(cls.path, 'w') as f:
            f.write(cls.data)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.path)


class TestGetTokensSourceFormats(SourceFormatsTestBase):
    data = u'''\
*** Settings ***
Library         Easter

*** Test Cases ***
Example
    None shall pass    ${NONE}
'''
    tokens = [
        (T.SETTING_HEADER, '*** Settings ***', 1, 1),
        (T.EOL, '\n', 1, 17),
        (T.EOS, '', 1, 18),
        (T.LIBRARY, 'Library', 2, 1),
        (T.SEPARATOR, '         ', 2, 8),
        (T.ARGUMENT, 'Easter', 2, 17),
        (T.EOL, '\n', 2, 23),
        (T.EOS, '', 2, 24),
        (T.EOL, '\n', 3, 1),
        (T.EOS, '', 3, 2),
        (T.TESTCASE_HEADER, '*** Test Cases ***', 4, 1),
        (T.EOL, '\n', 4, 19),
        (T.EOS, '', 4, 20),
        (T.NAME, 'Example', 5, 1),
        (T.EOL, '\n', 5, 8),
        (T.EOS, '', 5, 9),
        (T.SEPARATOR, '    ', 6, 1),
        (T.KEYWORD, 'None shall pass', 6, 5),
        (T.SEPARATOR, '    ', 6, 20),
        (T.ARGUMENT, '${NONE}', 6, 24),
        (T.EOL, '\n', 6, 31),
        (T.EOS, '', 6, 32)
    ]
    data_tokens = [
        (T.SETTING_HEADER, '*** Settings ***', 1, 1),
        (T.EOS, '', 1, 17),
        (T.LIBRARY, 'Library', 2, 1),
        (T.ARGUMENT, 'Easter', 2, 17),
        (T.EOS, '', 2, 23),
        (T.TESTCASE_HEADER, '*** Test Cases ***', 4, 1),
        (T.EOS, '', 4, 19),
        (T.NAME, 'Example', 5, 1),
        (T.EOS, '', 5, 8),
        (T.KEYWORD, 'None shall pass', 6, 5),
        (T.ARGUMENT, '${NONE}', 6, 24),
        (T.EOS, '', 6, 31)
    ]

    def test_file(self):
        self._verify(self.path)
        self._verify(self.path, data_only=True)

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
        tokens = get_tokens(source, data_only)
        expected = self.data_tokens if data_only else self.tokens
        assert_tokens(list(tokens), expected)


class TestGetResourceTokensSourceFormats(SourceFormatsTestBase):
    get_tokens = get_resource_tokens
    data = u'''\
*** Variable ***
${VAR}    Value

*** KEYWORD ***
NOOP    No Operation
'''
    tokens = [
        (T.VARIABLE_HEADER, '*** Variable ***', 1, 1),
        (T.EOL, '\n', 1, 17),
        (T.EOS, '', 1, 18),
        (T.VARIABLE, '${VAR}', 2, 1),
        (T.SEPARATOR, '    ', 2, 7),
        (T.ARGUMENT, 'Value', 2, 11),
        (T.EOL, '\n', 2, 16),
        (T.EOS, '', 2, 17),
        (T.EOL, '\n', 3, 1),
        (T.EOS, '', 3, 2),
        (T.KEYWORD_HEADER, '*** KEYWORD ***', 4, 1),
        (T.EOL, '\n', 4, 16),
        (T.EOS, '', 4, 17),
        (T.NAME, 'NOOP', 5, 1),
        (T.SEPARATOR, '    ', 5, 5),
        (T.EOS, '', 5, 9),
        (T.KEYWORD, 'No Operation', 5, 9),
        (T.EOL, '\n', 5, 21),
        (T.EOS, '', 5, 22)
    ]
    data_tokens = [
        (T.VARIABLE_HEADER, '*** Variable ***', 1, 1),
        (T.EOS, '', 1, 17),
        (T.VARIABLE, '${VAR}', 2, 1),
        (T.ARGUMENT, 'Value', 2, 11),
        (T.EOS, '', 2, 16),
        (T.KEYWORD_HEADER, '*** KEYWORD ***', 4, 1),
        (T.EOS, '', 4, 16),
        (T.NAME, 'NOOP', 5, 1),
        (T.EOS, '', 5, 5),
        (T.KEYWORD, 'No Operation', 5, 9),
        (T.EOS, '', 5, 21)
    ]

    def test_file(self):
        self._verify(self.path)
        self._verify(self.path, data_only=True)

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
        tokens = get_resource_tokens(source, data_only)
        expected = self.data_tokens if data_only else self.tokens
        assert_tokens(list(tokens), expected)


if __name__ == '__main__':
    unittest.main()
