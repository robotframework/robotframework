import unittest
from robot.parsing.model import TestCaseTable, TestCaseFileSettingTable

from robot.writer.formatters import TxtFormatter, HtmlFormatter, TsvFormatter
from robot.writer.tableformatters import RowSplitter, HtmlCell
from robot.utils.asserts import assert_equals


class TestRowSplitter(unittest.TestCase):

    def test_escaping_empty_cells_at_eol(self):
        formatter = RowSplitter(cols=3)
        assert_equals(formatter.split(['Some', 'text', '', 'with empty'], 0),
                                       [['Some', 'text', '${EMPTY}'],
                                        ['...', 'with empty']])

    def test_splitting_inside_comment(self):
        formatter = RowSplitter(cols=3)
        assert_equals(formatter.split(['Kw', 'Arg', '#Comment in', 'many cells'], 0),
                      [['Kw', 'Arg', '#Comment in'], ['...', '#many cells']])


class TestTxtFormatter(unittest.TestCase):

    def test_escaping_whitespace(self):
        assert_equals(TxtFormatter()._escape(['so  me']), ['so \ me'])

    def test_replacing_newlines(self):
        assert_equals(TxtFormatter()._escape(['so\nme']), ['so me'])


class TestTsvFormatter(unittest.TestCase):

    def test_replacing_newlines(self):
        assert_equals(TsvFormatter()._format_row(['so\nme'])[0], 'so me')


class TestHtmlFormatter(unittest.TestCase):

    def test_setting_table_doc(self):
        table = TestCaseFileSettingTable(None)
        table.set_header('Settings')
        table.doc.value = 'Some documentation'
        formatted = list(HtmlFormatter().setting_rows(table))
        assert_equals(self._rows_to_text(formatted),
                      [['Documentation', 'Some documentation']])
        assert_equals(formatted[0][1].attributes,
                      {'colspan': '4', 'class': 'colspan4'})

    def test_test_name_row_formatting(self):
        table = self._create_test_table()
        test = table.add('A Test')
        test.tags.value = ['t1', 't2', 't3', 't4']
        formatted = self._rows(table)
        assert_equals(len(formatted), 2)
        assert_equals(formatted[0], ['<a name="test_A Test">A Test</a>', '[Tags]', 't1', 't2', 't3'])
        assert_equals(formatted[1], ['', '...', 't4', '', ''])

    def test_test_documentation_colspan(self):
        table = self._create_test_table()
        test = table.add('Test')
        test.doc.value = 'Some doc'
        assert_equals(self._rows(table)[0],
            ['<a name="test_Test">Test</a>', '[Documentation]', 'Some doc'])
        assert_equals(list(HtmlFormatter().test_rows(table))[0][2].attributes,
                      {'colspan': '3', 'class': 'colspan3'})

    def test_test_documentation_with_comment(self):
        table = self._create_test_table()
        test = table.add('Test')
        test.doc.value = 'Some doc'
        test.doc._set_comment('a comment')
        assert_equals(self._rows(table)[0],
            ['<a name="test_Test">Test</a>', '[Documentation]', 'Some doc', '# a comment', ''])
        assert_equals(list(HtmlFormatter().test_rows(table))[0][2].attributes, {})

    def _rows(self, table):
        return self._rows_to_text(HtmlFormatter().test_rows(table))

    def _rows_to_text(self, rows):
        return [[cell.content for cell in row] for row in rows]

    def _create_test_table(self):
        table = TestCaseTable(None)
        table.set_header('Test Cases')
        return table

    def test_add_br_to_newlines(self):
        original = """This is real new line:
        here we have a single backslash n: \\n and here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n """
        expected = 'This is real new line:\n        here we have a single backslash n: \\n<br>\nand here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n<br>\n'
        assert_equals(HtmlCell(original).content, expected)

    def test_no_br_to_newlines_without_whitespace(self):
        original = r"Here there is no space after backslash-n: '\n'"
        assert_equals(HtmlCell(original).content, original)

    def test_no_br_to_double_backslashes(self):
        original = r"Here there is double backslash-n: \\n "
        assert_equals(HtmlCell(original).content, original)


if __name__ == "__main__":
    unittest.main()
