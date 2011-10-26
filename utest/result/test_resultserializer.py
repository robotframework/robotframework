import unittest
from StringIO import StringIO

from robot.result.serializer import ResultSerializer
from robot.result.model import TestSuite
from robot.utils.asserts import assert_equals

from test_resultbuilder import XML, ExecutionResultBuilder

class TestResultSerializer(unittest.TestCase):

    def test_suite_serialization(self):
        result = ExecutionResultBuilder(StringIO(XML)).build()
        output = StringIO()
        ResultSerializer(output).to_xml(result)
        act_lines = output.getvalue().splitlines()
        exp_lines = XML.splitlines()
        assert_equals(len(act_lines), len(exp_lines))
        for act, exp in zip(act_lines, exp_lines)[2:]:
            assert_equals(act, exp.strip())
