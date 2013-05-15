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
        kw = result.tests[0].keywords[0]
        assert_equals(kw.name, 'Log')
        assert_equals(kw.args, ['Hello, world!'])
        assert_equals(kw.status, 'PASS')

    def _continue_here____test_one_failing_library_keyword(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('Fail',
                                                        args=['Hello, world!'])
        result = suite.run(output='NONE')
        assert_equals(result.name, 'Suite')
        assert_equals(result.tests[0].name, 'Test')
        kw = result.tests[0].keywords[0]
        assert_equals(kw.name, 'Log')
        assert_equals(kw.args, ['Hello, world!'])
        assert_equals(kw.status, 'PASS')
