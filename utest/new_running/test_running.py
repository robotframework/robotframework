import unittest

from robot.utils.asserts import assert_equals
from robot.new_running import TestSuite


class TestRunning(unittest.TestCase):

    def test_one_library_keyword(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('Log',
                                                        args=['Hello, world!'])
        result = suite.run(output='NONE')
        self._check_suite(result, 'Suite', 'PASS')
        self._check_test(result.tests[0], 'Test', 'PASS')

    def test_failing_library_keyword(self):
        suite = TestSuite(name='Suite')
        test = suite.tests.create(name='Test')
        test.keywords.create('Log', args=['Dont fail yet.'])
        test.keywords.create('Fail', args=['Hello, world!'])
        result = suite.run(output='NONE')
        self._check_suite(result, 'Suite', 'FAIL')
        self._check_test(result.tests[0], 'Test', 'FAIL', 'Hello, world!')

    def _check_suite(self, suite, name, status):
        assert_equals(suite.name, name)
        assert_equals(suite.status, status)

    def _check_test(self, test, name, status, message=''):
        assert_equals(test.name, name)
        assert_equals(test.status, status)
        assert_equals(test.message, message)

