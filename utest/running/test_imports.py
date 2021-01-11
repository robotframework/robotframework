import unittest

from robot.running import TestSuite
from robot.utils import StringIO
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

    def test_imports(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.create('Library', 'OperatingSystem')
        suite.tests.create(name='Test').body.create_keyword('Directory Should Exist',
                                                            args=['.'])
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_library_imports(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.library('OperatingSystem')
        suite.tests.create(name='Test').body.create_keyword('Directory Should Exist',
                                                            args=['.'])
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_resource_imports(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.resource('test_resource.txt')
        suite.tests.create(name='Test').body.create_keyword('My Test Keyword')
        assert_equal(suite.tests[0].body[0].name, 'My Test Keyword')
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_variable_imports(self):
        suite = TestSuite(name='Suite')
        suite.resource.imports.variables('variables_file.py')
        suite.tests.create(name='Test').body.create_keyword(
            'Should Be Equal As Strings',
            args=['${MY_VARIABLE}', 'An example string']
        )
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_invalid_import_type(self):
        assert_raises_with_msg(ValueError,
                               "Invalid import type 'InvalidType'. Should be "
                               "one of 'Library', 'Resource' or 'Variables'.",
                               TestSuite().resource.imports.create,
                               'InvalidType', 'Name')


if __name__ == '__main__':
    unittest.main()
