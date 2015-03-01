import unittest
from six.moves import StringIO

from robot.running import TestSuite
from robot.utils.asserts import assert_equals, assert_raises_with_msg


def run(suite, **config):
    result = suite.run(output=None, log=None, report=None,
                       stdout=StringIO(), stderr=StringIO(), **config)
    return result.suite

def assert_suite(suite, name, status, message='', tests=1):
    assert_equals(suite.name, name)
    assert_equals(suite.status, status)
    assert_equals(suite.message, message)
    assert_equals(len(suite.tests), tests)

def assert_test(test, name, status, tags=(), msg=''):
    assert_equals(test.name, name)
    assert_equals(test.status, status)
    assert_equals(test.message, msg)
    assert_equals(tuple(test.tags), tags)


class TestImports(unittest.TestCase):

    def test_imports(self):
        suite = TestSuite(name='Suite')
        suite.imports.create('Library', 'OperatingSystem')
        suite.tests.create(name='Test').keywords.create('Directory Should Exist',
                                                        args=['.'])
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_library_imports(self):
        suite = TestSuite(name='Suite')
        suite.imports.library('OperatingSystem')
        suite.tests.create(name='Test').keywords.create('Directory Should Exist',
                                                        args=['.'])
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_resource_imports(self):
        suite = TestSuite(name='Suite')
        suite.imports.resource('test_resource.txt')
        suite.tests.create(name='Test').keywords.create('My Test Keyword')
        assert_equals(suite.tests[0].keywords[0].name, 'My Test Keyword')
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_variable_imports(self):
        suite = TestSuite(name='Suite')
        suite.imports.variables('variables_file.py')
        suite.tests.create(name='Test').keywords.create(
            'Should Be Equal As Strings',
            ['${MY_VARIABLE}', 'An example string']
        )
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_invalid_import_type(self):
        assert_raises_with_msg(ValueError,
                               "Invalid import type 'InvalidType'. Should be "
                               "one of 'Library', 'Resource' or 'Variables'.",
                               TestSuite().imports.create,
                               'InvalidType', 'Name')


if __name__ == '__main__':
    unittest.main()
