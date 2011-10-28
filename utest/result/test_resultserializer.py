from itertools import chain
import unittest
from StringIO import StringIO
from xml.etree.ElementTree import XML
from xml.etree.ElementTree import tostring

from robot.result.builders import ResultFromXML, ExecutionResultBuilder
from robot.result.serializer import ResultSerializer
from robot.result.model import ExecutionResult
from robot.utils.asserts import assert_equals

from test_resultbuilder import GOLDEN_XML, GOLDEN_XML_TWICE


class TestResultSerializer(unittest.TestCase):

    def test_single_result_serialization(self):
        output = StringIO()
        ResultSerializer(output).to_xml(ResultFromXML(StringIO(GOLDEN_XML)))
        self._assert_xml_content(self._xml_lines(output.getvalue()),
                                 self._xml_lines(GOLDEN_XML))

    def _xml_lines(self, text):
        return tostring(XML(text)).splitlines()

    def _assert_xml_content(self, actual, expected):
        assert_equals(len(actual), len(expected))
        for index, (act, exp) in enumerate(zip(actual, expected)[2:]):
            assert_equals(act, exp.strip(), 'Different values on line %d' % index)

    def test_combining_results(self):
        output = StringIO()
        result = ResultFromXML(StringIO(GOLDEN_XML), StringIO(GOLDEN_XML))
        ResultSerializer(output).to_xml(result)
        self._assert_xml_content(self._xml_lines(output.getvalue()),
                                 self._xml_lines(GOLDEN_XML_TWICE))

if __name__ == '__main__':
    unittest.main()
