from __future__ import with_statement

import os
import unittest
from StringIO import StringIO

from robot.result.builders import ExecutionResultBuilder, _Element, IgnoredElement, ResultsFromXML
from robot.result.model import ExecutionResult
from robot.utils.asserts import assert_equals, assert_true


with open(os.path.join(os.path.dirname(__file__), 'golden.xml')) as f:
    GOLDEN_XML = f.read()

with open(os.path.join(os.path.dirname(__file__), 'goldenTwice.xml')) as f:
    GOLDEN_XML_TWICE = f.read()


class TestBuildingSuiteExecutionResult(unittest.TestCase):

    def setUp(self):
        result = ResultsFromXML(StringIO(GOLDEN_XML))
        self._suite = result.suite
        self._test = self._suite.tests[0]
        self._keyword = self._test.keywords[0]
        self._user_keyword = self._test.keywords[1]
        self._message = self._keyword.messages[0]
        self._setup = self._suite.keywords[0]
        self._errors = result.errors

    def test_suite_is_built(self):
        assert_equals(self._suite.source, 'normal.html')
        assert_equals(self._suite.name, 'Normal')
        assert_equals(self._suite.doc, 'Normal test cases')
        assert_equals(self._suite.metadata, {'Something': 'My Value'})
        assert_equals(self._suite.status, 'PASS')
        assert_equals(self._suite.starttime, '20111024 13:41:20.873')
        assert_equals(self._suite.endtime, '20111024 13:41:20.952')
        assert_equals(self._suite.critical_stats.passed, 1)
        assert_equals(self._suite.critical_stats.failed, 0)
        assert_equals(self._suite.all_stats.passed, 1)
        assert_equals(self._suite.all_stats.failed, 0)

    def test_testcase_is_built(self):
        assert_equals(self._test.name, 'First One')
        assert_equals(self._test.doc, 'Test case documentation')
        assert_equals(self._test.timeout, '')
        assert_equals(list(self._test.tags), ['t1'])
        assert_equals(len(self._test.keywords), 2)
        assert_equals(self._test.status, 'PASS')
        assert_equals(self._test.starttime, '20111024 13:41:20.925')
        assert_equals(self._test.endtime, '20111024 13:41:20.934')
        assert_true(self._test.critical)

    def test_keyword_is_built(self):
        assert_equals(self._keyword.name, 'BuiltIn.Log')
        assert_equals(self._keyword.doc, 'Logs the given message with the given level.')
        assert_equals(self._keyword.args, ['Test 1'])
        assert_equals(self._keyword.status, 'PASS')
        assert_equals(self._keyword.starttime, '20111024 13:41:20.926')
        assert_equals(self._keyword.endtime, '20111024 13:41:20.928')
        assert_equals(len(self._keyword.keywords), 0)
        assert_equals(len(self._keyword.messages), 1)

    def test_user_keyword_is_built(self):
        assert_equals(self._user_keyword.name, 'logs on trace')
        assert_equals(self._user_keyword.doc, '')
        assert_equals(self._user_keyword.args, [])
        assert_equals(self._user_keyword.status, 'PASS')
        assert_equals(self._user_keyword.starttime, '20111024 13:41:20.930')
        assert_equals(self._user_keyword.endtime, '20111024 13:41:20.933')
        assert_equals(len(self._user_keyword.messages), 0)
        assert_equals(len(self._user_keyword.keywords), 1)

    def test_message_is_built(self):
        assert_equals(self._message.message, 'Test 1')
        assert_equals(self._message.level, 'INFO')
        assert_equals(self._message.timestamp, '20111024 13:41:20.927')

    def test_suite_setup_is_built(self):
        assert_equals(len(self._setup.keywords), 0)
        assert_equals(len(self._setup.messages), 0)

    def test_errors_are_built(self):
        assert_equals(len(self._errors.messages), 1)
        assert_equals(self._errors.messages[0].message,
                      "Error in file 'normal.html' in table 'Settings': Resource file 'nope' does not exist.")

class TestCombiningSuites(unittest.TestCase):

    def test_(self):
        result = ResultsFromXML(StringIO(GOLDEN_XML), StringIO(GOLDEN_XML))
        suite = result.suite
        assert_equals(suite.name, 'Normal & Normal')


class TestElements(unittest.TestCase):

    def test_nested_suites(self):
        xml = """
        <robot>
        <suite name="foo">
          <suite name="bar">
          </suite>
        </suite>
        </robot>
        """
        result = ResultsFromXML(StringIO(xml))
        assert_equals(result.suite.name, 'foo')
        assert_equals(result.suite.suites[0].name, 'bar')
        assert_equals(result.suite.longname, 'foo')
        assert_equals(result.suite.suites[0].longname, 'foo.bar')

    def test_unknown_elements_are_ignored(self):
        assert_true(isinstance(_Element(None).child_element('some_tag'),
                               IgnoredElement))


if __name__ == '__main__':
    unittest.main()

