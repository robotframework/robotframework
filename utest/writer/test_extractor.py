import unittest

from robot.parsing.model import VariableTable, TestCaseTable
from robot.utils.asserts import assert_equal
from robot.writer.dataextractor import DataExtractor

var_table = VariableTable(None)
var_table.add('${A scalar}', 'value', 'var comment')
var_table.add('', '', 'standalone comment')
var_table.add('@{A list}', ['v', 'a', 'lue'])

var_table_rows = [['${A scalar}', 'value', '# var comment'],
                  ['# standalone comment'],
                  ['@{A list}', 'v', 'a', 'lue']]

test_table = TestCaseTable(None)
test = test_table.add('A test case')
test.add_step(['No Operation'])
test.add_step(['Log Many', 'bar', 'quux', '#comment'])
loop = test.add_for_loop(['${i}', 'IN RANGE', '10'])
loop.add_step(['Log', '${i}'])
test2 = test_table.add('Second test')
test2.add_step(['FAIL'])

test_table_rows = [['A test case'],
                   ['', 'No Operation'],
                   ['', 'Log Many', 'bar', 'quux', '#comment'],
                   ['', 'FOR', '${i}', 'IN RANGE', '10'],
                   ['', '', 'Log', '${i}'],
                   ['', 'END'],
                   [],
                   ['Second test'],
                   ['', 'FAIL'],
                   []]

class DataExtractorTest(unittest.TestCase):

    def test_extracting_from_simple_table(self):
        assert_equal(list(DataExtractor().rows_from_table(var_table)),
                      var_table_rows)

    def test_extracting_from_indented_table(self):
        for idx, row in enumerate(DataExtractor()._rows_from_indented_table(test_table)):
            assert_equal(row, test_table_rows[idx])

    def test_names_on_first_content_row(self):
        table = TestCaseTable(None)
        t = table.add('Test')
        t.add_step(['No op'])
        extractor = DataExtractor(lambda t,n: True)
        assert_equal(list(extractor._rows_from_indented_table(table)),
                      [['Test', 'No op']])


if __name__ == '__main__':
    unittest.main()
