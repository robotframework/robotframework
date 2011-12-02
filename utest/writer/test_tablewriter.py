import unittest
from robot.writer.tablewriter import TableWriter, SpaceSeparator, PipeSeparator


class _Output(object):

    def __init__(self):
        self._data = ''

    def should_equal(self, *expected):
        joined = '\n'.join(expected)
        if joined.strip()!=self._data.strip():
            msg = "\n%s \n---\n!=\n---\n%s" % (repr(joined),repr(self._data))
            raise AssertionError(msg)

    def write(self, data):
        self._data += data


class TestTableWriter(unittest.TestCase):

    def setUp(self):
        self._space_output = _Output()
        self._pipe_output  = _Output()
        self._space_writer = TableWriter(output=self._space_output,
                                         separator=SpaceSeparator())
        self._pipe_writer  = TableWriter(output=self._pipe_output,
                                         separator=PipeSeparator())

    def test_writing_test_case(self):
        self._add_headers(['*** Test Cases ***'])
        self._add_tcuk_name('My Test Case')
        self._add_rows([['','Log','Hello'],['','No Operation']])
        self._write()
        self._space_output.should_equal(
            '*** Test Cases ***',
            'My Test Case',
            '    Log    Hello',
            '    No Operation')
        self._pipe_output.should_equal(
            '| *** Test Cases *** |',
            '| My Test Case |',
            '|    | Log | Hello |',
            '|    | No Operation |')

    def _add_headers(self, headers):
        self._pipe_writer.add_headers(headers)
        self._space_writer.add_headers(headers)

    def _add_tcuk_name(self, name):
        self._pipe_writer.add_tcuk_name(name)
        self._space_writer.add_tcuk_name(name)

    def _add_rows(self, rows):
        for row in rows:
            self._pipe_writer.add_row(row)
            self._space_writer.add_row(row)

    def _write(self):
        self._pipe_writer.write()
        self._space_writer.write()

    def test_writing_test_case_with_headers(self):
        self._add_headers(['*** Test Cases ***', 'Foo'])
        self._add_tcuk_name('My Test Case')
        self._add_rows([['','Log','Hello'],['','No Operation']])
        self._write()
        self._space_output.should_equal(
            '*** Test Cases ***  Foo',
            'My Test Case        Log           Hello',
            '                    No Operation')
        self._pipe_output.should_equal(
            '| *** Test Cases *** | Foo |',
            '| My Test Case       | Log          | Hello |',
            '|                    | No Operation |')

    def test_empty_test_cases(self):
        self._add_headers(['*** Test Cases ***'])
        self._add_tcuk_name('My Test Case')
        self._add_tcuk_name('My Test Case2')
        self._write()
        self._space_output.should_equal(
            '*** Test Cases ***',
            'My Test Case',
            'My Test Case2')
        self._pipe_output.should_equal(
            '| *** Test Cases *** |',
            '| My Test Case |',
            '| My Test Case2 |')

    def test_empty_test_cases_with_headers(self):
        self._add_headers(['*** Test Cases ***', 'foo'])
        self._add_tcuk_name('My Test Case')
        self._add_tcuk_name('My Test Case2')
        self._write()
        self._space_output.should_equal(
            '*** Test Cases ***  foo',
            'My Test Case',
            'My Test Case2')
        self._pipe_output.should_equal(
            '| *** Test Cases *** | foo |',
            '| My Test Case |',
            '| My Test Case2 |')

    def test_inline_name_lengths(self):
        self._add_headers(['*** Test Cases ***', 'Foo'])
        self._add_tcuk_name('Test Case With Length 24')
        self._add_rows([['','Log','Hello'],['','No Operation']])
        self._add_tcuk_name('Test Case With Length 25!')
        self._add_rows([['','Log','Hello'],['','No Operation']])
        self._write()
        self._space_output.should_equal(
            '*** Test Cases ***        Foo',
            'Test Case With Length 24  Log           Hello',
            '                          No Operation',
            'Test Case With Length 25!',
            '                          Log           Hello',
            '                          No Operation')

    def test_writing_with_2_additional_headers(self):
        self._add_headers(['*** Test Cases ***', 'h1', 'h2'])
        self._add_tcuk_name('My Test')
        self._add_rows([['','Something', 'nothing more to say'],
                        ['','Something else', 'jeps', 'heps']])
        self._write()
        self._space_output.should_equal(
            '*** Test Cases ***  h1              h2',
            'My Test             Something       nothing more to say',
            '                    Something else  jeps                 heps'
        )

    def test_ignore_first_column_length_when_only_one_element_in_row(self):
        self._add_headers(['*** Test Cases ***', 'h1', 'h2'])
        self._add_tcuk_name('Test Case with very long title that should be ignored')
        self._add_rows([['', 'something', 'something else']])
        self._write()
        self._space_output.should_equal(
            '*** Test Cases ***  h1         h2',
            'Test Case with very long title that should be ignored',
            '                    something  something else'
        )


if __name__ == '__main__':
    unittest.main()
