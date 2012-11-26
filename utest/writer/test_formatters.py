import unittest
from robot.parsing.model import TestCaseTable, TestCaseFileSettingTable

from robot.writer.formatters import TxtFormatter, TsvFormatter, PipeFormatter
from robot.writer.htmlformatter import HtmlFormatter, HtmlCell
from robot.utils.asserts import assert_equals, assert_true


class TestTxtFormatter(unittest.TestCase):

    def setUp(self):
        self._formatter = TxtFormatter(6)

    def test_escaping_whitespace(self):
        assert_equals(self._formatter._escape(['so  me']), ['so \\ me'])
        assert_equals(self._formatter._escape(['   ']), [' \\ \\ '])

    def test_replacing_newlines(self):
        assert_equals(self._formatter._escape(['so\nme']), ['so me'])

    def test_escaping_consecutive_spaces(self):
        settings = TestCaseFileSettingTable(None)
        settings.force_tags.value = ['f  1']
        assert_equals(list(self._formatter.format_table(settings))[0],
                      ['Force Tags    ', 'f \\ 1'])

    def test_escaping_empty_intermediate_cells(self):
        settings = TestCaseFileSettingTable(None)
        settings.suite_setup.name = 'Run'
        settings.suite_setup.args = ['', 'baby']
        assert_equals(list(self._formatter.format_table(settings))[0][1:],
                      ['Run', '\\', 'baby'])

    def test_aligned_header_cells_are_not_escaped(self):
        table = TestCaseTable(None)
        table.set_header(['test case', 'cus  tom',  'header'])
        table.add('Test case with a long name').add_step(['keyword here', 'args'])
        assert_equals(self._formatter.format_header(table),
                     ['*** test case *** ', 'cus \\ tom   ', 'header'])



class TestPipeFormatter(unittest.TestCase):

    def test_escaping_pipes(self):
        formatter = PipeFormatter(7)
        assert_equals(formatter._escape(['so | me']), ['so \\| me'])
        assert_equals(formatter._escape(['|so|me|']), ['|so|me|'])
        assert_equals(formatter._escape(['so |']), ['so \\|'])
        assert_equals(formatter._escape(['| so']), ['\\| so'])

    def test_empty_cell(self):
        settings = TestCaseFileSettingTable(None)
        settings.force_tags.value = ['f1', '', 'f3']
        assert_equals(list(PipeFormatter(4).format_table(settings))[0],
                      ['Force Tags    ', 'f1', '  ', 'f3'])


class TestTsvFormatter(unittest.TestCase):

    def setUp(self):
        self._formatter = TsvFormatter(6)

    def test_replacing_newlines(self):
        assert_equals(self._formatter._format_row(['so\nme'])[0], 'so me')

    def test_escaping_tabs(self):
        assert_equals(self._formatter._format_row(['so\tme'])[0], 'so\\tme')

    def test_escaping_consecutive_spaces(self):
        assert_equals(self._formatter._format_row(['so  me'])[0], 'so \ me')


class TestHtmlFormatter(unittest.TestCase):

    def setUp(self):
        self._formatter = HtmlFormatter(5)

    def test_setting_table_doc(self):
        table = TestCaseFileSettingTable(None)
        table.set_header('Settings')
        table.doc.value = 'Some documentation'
        formatted = list(self._formatter.format_table(table))
        assert_equals(self._rows_to_text(formatted),
                      [['Documentation', 'Some documentation']])
        assert_equals(formatted[0][1].attributes,
                      {'colspan': '4', 'class': 'colspan4'})

    def test_test_name_row_formatting(self):
        table = self._create_test_table()
        test = table.add('A Test')
        test.tags.value = ['t1', 't2', 't3', 't4']
        formatted = self._rows(table)
        assert_equals(len(formatted), 2, formatted)
        assert_equals(formatted[0], ['<a name="test_A Test">A Test</a>', '[Tags]', 't1', 't2', 't3'])
        assert_equals(formatted[1], ['', '...', 't4', '', ''])

    def test_test_documentation_colspan(self):
        table = self._create_test_table()
        test = table.add('Test')
        test.doc.value = 'Some doc'
        assert_equals(self._rows(table)[0],
            ['<a name="test_Test">Test</a>', '[Documentation]', 'Some doc'])
        assert_equals(list(self._formatter.format_table(table))[0][2].attributes,
                      {'colspan': '3', 'class': 'colspan3'})

    def test_test_documentation_with_comment(self):
        table = self._create_test_table()
        test = table.add('Test')
        test.doc.value = 'Some doc'
        test.doc._set_comment('a comment')
        assert_equals(self._rows(table)[0],
            ['<a name="test_Test">Test</a>', '[Documentation]', 'Some doc', '# a comment', ''])
        assert_equals(list(self._formatter.format_table(table))[0][2].attributes, {})

    def test_testcase_table_custom_headers(self):
        self._check_header_length([], 1)
        self._check_header_length(['a', 'b', 'ceee dee'], 4)
        self._check_header_length(['akjsakjskjd kjsda kdjs'], 2)
        self._check_header_length([str(i) for i in range(1000)], 1001)

    def test_header_width_matches_widest_row(self):
        table = self._create_test_table(['h', 'e'])
        test = table.add('Some test')
        test.add_step(['kw', 'arg1', 'arg2', 'arg3'])
        assert_equals(len(self._formatter.format_header(table)), 5)

    def _check_header_length(self, headers, expected_length):
        table = self._create_test_table(headers)
        assert_equals(len(self._formatter.format_header(table)), expected_length)

    def test_testcase_table_header_colspan(self):
        self._assert_header_colspan([], 5)
        self._assert_header_colspan(['a', 'b'], 1)

    def _assert_header_colspan(self, header, expected_colspan):
        table = self._create_test_table(header)
        row = self._formatter.format_header(table)
        assert_equals(row[0].attributes['colspan'], str(expected_colspan))

    def test_escaping_consecutive_spaces(self):
        assert_equals(self._formatter._format_row(['so  me'])[0].content, 'so \ me')

    def test_number_of_columns_is_max_of_header_and_row_widths(self):
        table = self._create_test_table(['a', 'b'])
        test = table.add('Test')
        test.add_step(['Log Many', 'kukka', 'nen'])
        self._check_row_lengths(table, 4)
        table = self._create_test_table(['a', 'b', 'c'])
        test = table.add('Test')
        test.add_step(['No Operation'])
        self._check_row_lengths(table, 4)

    def _check_row_lengths(self, table, expected_length):
        rows = list(self._formatter.format_table(table))
        assert_true(len(rows) > 0)
        for row in rows:
            assert_equals(len(row), expected_length)

    def _rows(self, table):
        return self._rows_to_text(self._formatter.format_table(table))

    def _rows_to_text(self, rows):
        return [[cell.content for cell in row] for row in rows]

    def _create_test_table(self, additional_headers=()):
        table = TestCaseTable(None)
        table.set_header(['Test Cases'] + list(additional_headers))
        return table

    def test_add_br_to_newlines(self):
        original = """This is real new line:
        here we have a single backslash n: \\n and here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n """
        expected = 'This is real new line:\n        here we have a single backslash n: \\n<br>\nand here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n<br>\n'
        assert_equals(HtmlCell(original).content, expected)

    def test_br_to_newlines_without_whitespace(self):
        original = r"Here there is no space after backslash-n: '\n'"
        assert_equals(HtmlCell(original).content,
                      original.replace('\\n', '\\n<br>\n'))

    def test_no_br_to_double_backslashes(self):
        original = r"Here there is double backslash-n: \\n "
        assert_equals(HtmlCell(original).content, original)


if __name__ == "__main__":
    unittest.main()
