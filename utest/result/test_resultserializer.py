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

    #TODO!! THIS
    def _test_combining_results(self):
        result1 = ExecutionResultBuilder(StringIO(GOLDEN_XML)).build()
        result2 = ExecutionResultBuilder(StringIO(GOLDEN_XML)).build()
        combined = ExecutionResult()
        #combined += result1
        #combined += result2
        suite = combined.suites.create()
        suite.suites = [result1.suite, result2.suite]
        combined.errors.messages = chain(result1.errors.messages,
                                         result2.errors.messages)
        actual = self._get_result_xml(combined)
        expected = GOLDEN_XML_TWICE.splitlines()
        self._assert_xml_content(actual, expected)

if __name__ == '__main__':
    unittest.main()
