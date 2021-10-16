from io import StringIO
import unittest

from robot.reporting.jsexecutionresult import JsExecutionResult
from robot.reporting.jswriter import JsResultWriter
from robot.utils.asserts import assert_equal, assert_true


def get_lines(suite=(), strings=(), basemillis=100, start_block='',
              end_block='', split_threshold=9999, min_level='INFO'):
    output = StringIO()
    data = JsExecutionResult(suite, None, None, strings, basemillis, min_level=min_level)
    writer = JsResultWriter(output, start_block, end_block, split_threshold)
    writer.write(data, settings={})
    return output.getvalue().splitlines()


def assert_separators(lines, separator, end_separator=False):
    for index, line in enumerate(lines):
        if index % 2 == int(end_separator):
            assert_equal(line, separator)
        else:
            assert_true(line.startswith('window.'), line)


class TestDataModelWrite(unittest.TestCase):

    def test_writing_datamodel_elements(self):
        lines = get_lines(min_level='DEBUG')
        assert_true(lines[0].startswith('window.output = {}'), lines[0])
        assert_true(lines[1].startswith('window.output["'), lines[1])
        assert_true(lines[-1].startswith('window.settings ='), lines[-1])

    def test_writing_datamodel_with_separator(self):
        lines = get_lines(start_block='seppo\n')
        assert_true(len(lines) >= 2)
        assert_separators(lines, 'seppo')

    def test_splitting_output_strings(self):
        lines = get_lines(strings=['data' for _ in range(100)],
                                split_threshold=9, end_block='?\n')
        parts = [l for l in lines if l.startswith('window.output["strings')]
        assert_equal(len(parts), 13)
        assert_equal(parts[0], 'window.output["strings"] = [];')
        for line in parts[1:]:
            assert_true(line.startswith('window.output["strings"] = window.output["strings"].concat(['), line)
        assert_separators(lines, '?', end_separator=True)


class TestSuiteWriter(unittest.TestCase):

    def test_no_splitting(self):
        suite = (1, (2, 3), (4, (5,), (6, ())), 8)
        expected = ['window.output["suite"] = [1,[2,3],[4,[5],[6,[]]],8];']
        self._assert_splitting(suite, 100, expected)

    def test_simple_splitting_version_1(self):
        suite = ((1, 2, 3, 4), (5, 6, 7, 8), 9)
        expected = ['window.sPart0 = [1,2,3,4];',
                    'window.sPart1 = [5,6,7,8];',
                    'window.output["suite"] = [window.sPart0,window.sPart1,9];']
        self._assert_splitting(suite, 4, expected)

    def test_simple_splitting_version_2(self):
        suite = ((1, 2, 3, 4), (5, 6, 7, 8), 9, 10)
        expected = ['window.sPart0 = [1,2,3,4];',
                    'window.sPart1 = [5,6,7,8];',
                    'window.sPart2 = [window.sPart0,window.sPart1,9,10];',
                    'window.output["suite"] = window.sPart2;']
        self._assert_splitting(suite, 4, expected)

    def test_simple_splitting_version_3(self):
        suite = ((1, 2, 3, 4), (5, 6, 7, 8, 9, 10), 11)
        expected = ['window.sPart0 = [1,2,3,4];',
                    'window.sPart1 = [5,6,7,8,9,10];',
                    'window.output["suite"] = [window.sPart0,window.sPart1,11];']
        self._assert_splitting(suite, 4, expected)

    def test_tuple_itself_has_size_one(self):
        suite = ((1, (), (), 4), (((((),),),),))
        expected = ['window.sPart0 = [1,[],[],4];',
                    'window.sPart1 = [[[[[]]]]];',
                    'window.output["suite"] = [window.sPart0,window.sPart1];']
        self._assert_splitting(suite, 4, expected)

    def test_nested_splitting(self):
        suite = (1, (2, 3), (4, (5,), (6, 7)), 8)
        expected = ['window.sPart0 = [2,3];',
                    'window.sPart1 = [6,7];',
                    'window.sPart2 = [4,[5],window.sPart1];',
                    'window.sPart3 = [1,window.sPart0,window.sPart2,8];',
                    'window.output["suite"] = window.sPart3;']
        self._assert_splitting(suite, 2, expected)

    def _assert_splitting(self, suite, threshold, expected):
        lines = get_lines(suite, split_threshold=threshold, start_block='foo\n')
        parts = [l for l in lines if l.startswith(('window.sPart',
                                                   'window.output["suite"]'))]
        assert_equal(parts, expected)
        assert_separators(lines, 'foo')


if __name__ == '__main__':
    unittest.main()
