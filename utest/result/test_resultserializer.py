import unittest
from StringIO import StringIO

from robot.result.serializer import ResultSerializer
from robot.result.model import TestSuite
from robot.utils.asserts import assert_equals


class TestResultSerializer(unittest.TestCase):

    def test_suite_serialization(self):
        suite = TestSuite(name='name')
        output = StringIO()
        ResultSerializer(output).to_xml(suite)
        assert_equals(output.getvalue(), '''<?xml version="1.0" encoding="UTF-8"?>
<robot>
<suite name="name">
</suite>
</robot>
''')


