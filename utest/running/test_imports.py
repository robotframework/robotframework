from io import StringIO
import unittest

from robot.running import TestSuite
from robot.running.resourcemodel import Import
from robot.utils.asserts import assert_equal, assert_raises_with_msg


def run(suite, **config):
    result = suite.run(output=None, log=None, report=None,
                       stdout=StringIO(), stderr=StringIO(), **config)
    return result.suite


def assert_suite(suite, name, status, message='', tests=1):
    assert_equal(suite.name, name)
    assert_equal(suite.status, status)
    assert_equal(suite.message, message)
    assert_equal(len(suite.tests), tests)


def assert_test(test, name, status, tags=(), msg=''):
    assert_equal(test.name, name)
    assert_equal(test.status, status)
    assert_equal(test.message, msg)
    assert_equal(tuple(test.tags), tags)


class TestImports(unittest.TestCase):

    def run_and_check_pass(self, suite):
        result = run(suite)
        try:
            assert_suite(result, 'Suite', 'PASS')
            assert_test(result.tests[0], 'Test', 'PASS')
        except AssertionError as e:
            # Something failed. Let's print more info.
            full_msg = ["Expected and obtained don't match. Test messages:"]
            for test in result.tests:
                full_msg.append('%s: %s' % (test, test.message))
            raise AssertionError('\n'.join(full_msg)) from e

    def test_create(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.create('Library', 'OperatingSystem')
        suite.resource.imports.create('RESOURCE', 'test.resource')
        suite.resource.imports.create(type='LibRary', name='String')
        test = suite.tests.create(name='Test')
        test.body.create_keyword('Directory Should Exist', args=['.'])
        test.body.create_keyword('My Test Keyword')
        test.body.create_keyword('Convert To Lower Case', args=['ROBOT'])
        self.run_and_check_pass(suite)

    def test_library(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.library('OperatingSystem')
        suite.tests.create(name='Test').body.create_keyword('Directory Should Exist',
                                                            args=['.'])
        self.run_and_check_pass(suite)

    def test_resource(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.resource('test.resource')
        suite.tests.create(name='Test').body.create_keyword('My Test Keyword')
        assert_equal(suite.tests[0].body[0].name, 'My Test Keyword')
        self.run_and_check_pass(suite)

    def test_variables(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.variables('variables_file.py')
        suite.tests.create(name='Test').body.create_keyword(
            'Should Be Equal As Strings',
            args=['${MY_VARIABLE}', 'An example string']
        )
        self.run_and_check_pass(suite)

    def test_invalid_type(self):
        assert_raises_with_msg(ValueError,
                               "Invalid import type: Expected 'LIBRARY', 'RESOURCE' "
                               "or 'VARIABLES', got 'INVALIDTYPE'.",
                               TestSuite().resource.imports.create,
                               'InvalidType', 'Name')

    def test_repr(self):
        assert_equal(repr(Import(Import.LIBRARY, 'X')),
                     "robot.running.Import(type='LIBRARY', name='X')")
        assert_equal(repr(Import(Import.LIBRARY, 'X', ['a'], 'A')),
                     "robot.running.Import(type='LIBRARY', name='X', args=('a',), alias='A')")
        assert_equal(repr(Import(Import.RESOURCE, 'X')),
                     "robot.running.Import(type='RESOURCE', name='X')")
        assert_equal(repr(Import(Import.VARIABLES, '')),
                     "robot.running.Import(type='VARIABLES', name='')")


if __name__ == '__main__':
    unittest.main()
