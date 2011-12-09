from StringIO import StringIO
import unittest

from robot.utils.asserts import assert_equals, assert_true
from robot.reporting.jsexecutionresult import JsExecutionResult
from robot.reporting.jswriter import JsResultWriter


class TestDataModelWrite(unittest.TestCase):

    def test_writing_datamodel_elements(self):
        lines = self._get_lines()
        assert_true(lines[0].startswith('window.output = {}'), lines[0])
        assert_true(lines[1].startswith('window.output["'), lines[1])
        assert_true(lines[-1].startswith('window.settings ='), lines[-1])

    def _get_lines(self, suite=(), strings=(), basemillis=100,
                   start_block='', end_block='', split_threshold=9999):
        output = StringIO()
        data = JsExecutionResult(suite, None, None, strings, basemillis)
        attrs = {'start_block': start_block, 'end_block': end_block,
                 'split_threshold': split_threshold}
        writer = type('CustomWriter', (JsResultWriter,), attrs)(output)
        writer.write(data, settings={})
        return output.getvalue().splitlines()

    def test_writing_datamodel_with_separator(self):
        lines = self._get_lines(start_block='seppo\n')
        assert_true(len(lines) >= 2)
        self._assert_separators_in(lines, 'seppo')

    def _assert_separators_in(self, lines, separator, end_separator=False):
        for index, line in enumerate(lines):
            if index % 2 == int(end_separator):
                assert_equals(line, separator)
            else:
                assert_true(line.startswith('window.'), line)

    def test_writing_datamodel_with_split_threshold_in_suite(self):
        suite = (1, (2, 3), (4, (5,), (6, 7)), 8)
        lines = self._get_lines(suite=suite, split_threshold=2, start_block='foo\n')
        parts = filter(lambda l: l.startswith('window.sPart'), lines)
        expected = ['window.sPart0 = [2,3];',
                    'window.sPart1 = [6,7];',
                    'window.sPart2 = [4,[5],window.sPart1];',
                    'window.sPart3 = [1,window.sPart0,window.sPart2,8];']
        assert_equals(parts, expected)
        self._assert_separators_in(lines, 'foo')

    def test_splitting_output_strings(self):
        lines = self._get_lines(strings=['data' for _ in range(100)],
                                split_threshold=9, end_block='?\n')
        parts = [l for l in lines if l.startswith('window.output["strings')]
        assert_equals(len(parts), 13)
        assert_equals(parts[0], 'window.output["strings"] = [];')
        for line in parts[1:]:
            assert_true(line.startswith('window.output["strings"] = window.output["strings"].concat(['), line)
        self._assert_separators_in(lines, '?', end_separator=True)


if __name__ == '__main__':
    unittest.main()
