import copy
import os
from os.path import abspath, normpath, join
import tempfile
import unittest
import warnings

from robot import api, model
from robot.model.modelobject import ModelObject
from robot.running.model import TestSuite, TestCase, Keyword, For, If, UserKeyword
from robot.running import TestSuiteBuilder
from robot.utils.asserts import (assert_equal, assert_not_equal, assert_false,
                                 assert_raises, assert_true)
from robot.utils import unicode


MISC_DIR = normpath(join(abspath(__file__), '..', '..', '..',
                         'atest', 'testdata', 'misc'))


class TestModelTypes(unittest.TestCase):

    def test_suite_setup(self):
        suite = TestSuite()
        assert_equal(type(suite.setup), Keyword)
        assert_equal(type(suite.teardown), Keyword)
        assert_not_equal(type(suite.setup), model.Keyword)
        assert_not_equal(type(suite.teardown), model.Keyword)

    def test_suite_test_case(self):
        test = TestSuite().tests.create()
        assert_equal(type(test), TestCase)
        assert_not_equal(type(test), model.TestCase)

    def test_test_case_keyword(self):
        kw = TestCase().body.create_keyword()
        assert_equal(type(kw), Keyword)
        assert_not_equal(type(kw), model.Keyword)


class TestUserKeyword(unittest.TestCase):

    def test_keywords_deprecation(self):
        uk = UserKeyword('Name')
        uk.body.create_keyword()
        uk.teardown.config(name='T')
        with warnings.catch_warnings(record=True) as w:
            kws = uk.keywords
            assert_equal(len(kws), 2)
            assert_true('deprecated' in str(w[0].message))
        assert_raises(AttributeError, kws.append, Keyword())
        assert_raises(AttributeError, setattr, uk, 'keywords', [])


class TestSuiteFromSources(unittest.TestCase):
    path = join(os.getenv('TEMPDIR') or tempfile.gettempdir(),
                'test_run_model.robot')
    data = '''
*** Settings ***
Documentation    Some text.
Test Setup       No Operation
Library          ExampleLibrary

*** Variables ***
${VAR}           Value

*** Test Cases ***
Example
    Keyword

*** Keywords ***
Keyword
    Log    Hello!
'''

    @classmethod
    def setUpClass(cls):
        with open(cls.path, 'w') as f:
            f.write(cls.data)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.path)

    def test_from_file_system(self):
        suite = TestSuite.from_file_system(self.path)
        self._verify_suite(suite)

    def test_from_file_system_with_multiple_paths(self):
        suite = TestSuite.from_file_system(self.path, self.path)
        assert_equal(suite.name, 'Test Run Model & Test Run Model')
        self._verify_suite(suite.suites[0])
        self._verify_suite(suite.suites[1])

    def test_from_file_system_with_config(self):
        suite = TestSuite.from_file_system(self.path, rpa=True)
        self._verify_suite(suite, rpa=True)

    def test_from_model(self):
        model = api.get_model(self.data)
        suite = TestSuite.from_model(model)
        self._verify_suite(suite, name='')

    def test_from_model_containing_source(self):
        model = api.get_model(self.path)
        suite = TestSuite.from_model(model)
        self._verify_suite(suite)

    def test_from_model_with_custom_name(self):
        for source in [self.data, self.path]:
            model = api.get_model(source)
            suite = TestSuite.from_model(model, name='Custom name')
            self._verify_suite(suite, 'Custom name')

    def _verify_suite(self, suite, name='Test Run Model', rpa=False):
        assert_equal(suite.name, name)
        assert_equal(suite.doc, 'Some text.')
        assert_equal(suite.rpa, rpa)
        assert_equal(suite.resource.imports[0].type, 'Library')
        assert_equal(suite.resource.imports[0].name, 'ExampleLibrary')
        assert_equal(suite.resource.variables[0].name, '${VAR}')
        assert_equal(suite.resource.variables[0].value, ('Value',))
        assert_equal(suite.resource.keywords[0].name, 'Keyword')
        assert_equal(suite.resource.keywords[0].body[0].name, 'Log')
        assert_equal(suite.resource.keywords[0].body[0].args, ('Hello!',))
        assert_equal(suite.tests[0].name, 'Example')
        assert_equal(suite.tests[0].setup.name, 'No Operation')
        assert_equal(suite.tests[0].body[0].name, 'Keyword')


class TestCopy(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuiteBuilder().build(MISC_DIR)

    def test_copy(self):
        self.assert_copy(self.suite, self.suite.copy())

    def assert_copy(self, original, copied):
        assert_not_equal(id(original), id(copied))
        self.assert_same_attrs_and_values(original, copied)
        for attr in ['suites', 'tests']:
            for child in getattr(original, attr, []):
                self.assert_copy(child, child.copy())

    def assert_same_attrs_and_values(self, model1, model2):
        assert_equal(dir(model1), dir(model2))
        for attr, value1, value2 in self.get_non_property_attrs(model1, model2):
            if callable(value1) and callable(value2):
                continue
            assert_equal(id(value1), id(value2), attr)
            if isinstance(value1, ModelObject):
                self.assert_same_attrs_and_values(value1, value2)

    def get_non_property_attrs(self, model1, model2):
        for attr in dir(model1):
            if 'parent' in attr or isinstance(getattr(type(model1), attr, None), property):
                continue
            value1 = getattr(model1, attr)
            value2 = getattr(model2, attr)
            yield attr, value1, value2

    def test_deepcopy(self):
        self.assert_deepcopy(self.suite, self.suite.deepcopy())

    def assert_deepcopy(self, original, copied):
        assert_not_equal(id(original), id(copied))
        self.assert_same_attrs_and_different_values(original, copied)
        # It would be too slow to test deepcopy recursively like we test copy.

    def assert_same_attrs_and_different_values(self, model1, model2):
        assert_equal(dir(model1), dir(model2))
        for attr, value1, value2 in self.get_non_property_attrs(model1, model2):
            if attr.startswith('__') or self.cannot_differ(value1, value2):
                continue
            assert_not_equal(id(value1), id(value2), attr)
            if isinstance(value1, ModelObject):
                self.assert_same_attrs_and_different_values(value1, value2)

    def cannot_differ(self, value1, value2):
        if isinstance(value1, ModelObject):
            return False
        if type(value1) is not type(value2):
            return False
        # None, Booleans, small numbers, etc. are singletons.
        try:
            return id(value1) == id(copy.deepcopy(value1))
        except TypeError:  # Got in some cases at least with Python 2.6
            return True


class TestLineNumberAndSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = join(MISC_DIR, 'pass_and_fail.robot')
        cls.suite = TestSuite.from_file_system(cls.source)

    def test_suite(self):
        assert_equal(self.suite.source, self.source)
        assert_false(hasattr(self.suite, 'lineno'))

    def test_import(self):
        self._assert_lineno_and_source(self.suite.resource.imports[0], 5)

    def test_variable(self):
        self._assert_lineno_and_source(self.suite.resource.variables[0], 8)

    def test_test(self):
        self._assert_lineno_and_source(self.suite.tests[0], 12)

    def test_user_keyword(self):
        self._assert_lineno_and_source(self.suite.resource.keywords[0], 24)

    def test_keyword_call(self):
        self._assert_lineno_and_source(self.suite.tests[0].body[0], 15)
        self._assert_lineno_and_source(self.suite.resource.keywords[0].body[0], 27)

    def _assert_lineno_and_source(self, item, lineno):
        assert_equal(item.source, self.source)
        assert_equal(item.lineno, lineno)


if __name__ == '__main__':
    unittest.main()
