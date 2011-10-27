from itertools import chain
import unittest
from StringIO import StringIO

from robot.result.serializer import ResultSerializer
from robot.result.model import ExecutionResult
from robot.utils.asserts import assert_equals

from test_resultbuilder import XML, XML_TWICE, ExecutionResultBuilder

class TestResultSerializer(unittest.TestCase):

    def test_suite_serialization(self):
        result = ExecutionResultBuilder(StringIO(XML)).build()
        act_lines = self._get_result_xml(result)
        exp_lines = XML.splitlines()
        self._assert_xmls(act_lines, exp_lines)

    def _get_result_xml(self, result):
        output = StringIO()
        ResultSerializer(output).to_xml(result)
        return output.getvalue().splitlines()

    def _assert_xmls(self, actual, expected):
        assert_equals(len(actual), len(expected))
        for index, (act, exp) in enumerate(zip(actual, expected)[2:]):
            assert_equals(act, exp.strip(), 'Different values on line %d' % index)

    def test_combining_results(self):
        result1 = ExecutionResultBuilder(StringIO(XML)).build()
        result2 = ExecutionResultBuilder(StringIO(XML)).build()
        combined = ExecutionResult()
        suite = combined.suites.create()
        suite.suites = [result1.suite, result2.suite]
        combined.errors.messages = chain(result1.errors.messages,
                                         result2.errors.messages)
        actual = self._get_result_xml(combined)
        expected = XML_TWICE.splitlines()
        self._assert_xmls(actual, expected)

