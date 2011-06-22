from StringIO import StringIO
import unittest
from robot.utils.asserts import assert_equals, assert_true
from robot.result.jsondatamodel import DataModel

class TestDataModelWrite(unittest.TestCase):

    def test_writing_datamodel_elements(self):
        lines = self._get_lines()
        assert_true(lines[0].startswith('window.output = {}'))
        assert_true(lines[1].startswith('window.output["'))
        assert_true(lines[-1].startswith('window.settings ='))

    def _get_lines(self, data=None, separator=None):
        output = StringIO()
        DataModel(data or {'baseMillis':100}).write_to(output, separator=separator)
        return output.getvalue().splitlines()

    def test_writing_datamodel_with_separator(self):
        lines = self._get_lines(separator='seppo\n')
        assert_true(len(lines) >= 2)
        for index, line in enumerate(lines):
            if index % 2:
                assert_equals(line, 'seppo')
            else:
                assert_true(line.startswith('window.'))

