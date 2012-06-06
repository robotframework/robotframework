from __future__ import with_statement
import unittest
import os
from StringIO import StringIO

from robot.result import ExecutionResult
from robot.reporting.outputwriter import OutputWriter
from robot.utils import XmlWriter
from robot.utils.asserts import assert_equals
from robot.utils import ET, ETSource

from test_resultbuilder import GOLDEN_XML, GOLDEN_XML_TWICE


class StreamXmlWriter(XmlWriter):

    def _create_output(self, output):
        return output

    def close(self):
        pass


class TestableOutputWriter(OutputWriter):

    def _get_writer(self, output, generator):
        writer = StreamXmlWriter(output, encoding='UTF-8')
        writer.start('robot')
        return writer


class TestResultSerializer(unittest.TestCase):

    def test_single_result_serialization(self):
        output = StringIO()
        writer = TestableOutputWriter(output)
        ExecutionResult(GOLDEN_XML).visit(writer)
        self._assert_xml_content(self._xml_lines(output.getvalue()),
                                 self._xml_lines(GOLDEN_XML))

    def _xml_lines(self, text):
        with ETSource(text) as source:
            tree = ET.parse(source)
        output = StringIO()
        tree.write(output)
        return output.getvalue().splitlines()

    def _assert_xml_content(self, actual, expected):
        assert_equals(len(actual), len(expected))
        for index, (act, exp) in enumerate(zip(actual, expected)[2:]):
            assert_equals(act, exp.strip(), 'Different values on line %d' % index)

    def test_combining_results(self):
        output = StringIO()
        writer = TestableOutputWriter(output)
        ExecutionResult(GOLDEN_XML, GOLDEN_XML).visit(writer)
        self._assert_xml_content(self._xml_lines(output.getvalue()),
                                 self._xml_lines(GOLDEN_XML_TWICE))


if __name__ == '__main__':
    unittest.main()
