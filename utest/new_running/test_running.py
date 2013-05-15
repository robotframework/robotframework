import unittest

from robot.utils.asserts import assert_equals
from robot.new_running import TestSuite


class TestRunning(unittest.TestCase):

    def test_one_library_keyword(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('Log',
                                                        args=['Hello, world!'])
        result = suite.run(output='NONE')
        assert_equals(result.name, 'Suite')
        assert_equals(result.tests[0].name, 'Test')
        assert_equals(result.tests[0].status, 'PASS')


    def test_one_failing_library_keyword(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('Fail',
                                                        args=['Hello, world!'])
        result = suite.run(output='NONE')
        assert_equals(result.name, 'Suite')
        test = result.tests[0]
        assert_equals(test.name, 'Test')
        assert_equals(test.message, 'Hello, world!')
        assert_equals(test.status, 'FAIL')

