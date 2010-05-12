import unittest

from robot.utils.asserts import *
from robot.parsing.newmodel import *


class TestTestCaseFile(unittest.TestCase):

    def setUp(self):
        self.tcf = TestCaseFile()

    def test_create(self):
        assert_none(self.tcf.source)
        assert_true(isinstance(self.tcf.setting_table, SettingTable))
        assert_true(isinstance(self.tcf.variable_table, VariableTable))
        assert_true(isinstance(self.tcf.testcase_table, TestCaseTable))
        assert_true(isinstance(self.tcf.keyword_table, KeywordTable))

    def test_edited(self):
        assert_false(self.tcf.edited())
        self.tcf.setting_table.doc.set('content')
        assert_true(self.tcf.edited())


class TestSettingTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().setting_table

    def test_create(self):
        assert_true(isinstance(self.table.doc, Documentation))
        assert_true(isinstance(self.table.suite_setup, Fixture))
        assert_true(isinstance(self.table.suite_teardown, Fixture))
        assert_true(isinstance(self.table.metadata, Metadata))
        assert_true(isinstance(self.table.test_setup, Fixture))
        assert_true(isinstance(self.table.test_teardown, Fixture))
        assert_true(isinstance(self.table.test_timeout, Timeout))
        assert_true(isinstance(self.table.force_tags, Tags))
        assert_true(isinstance(self.table.default_tags, Tags))
        assert_equal(self.table.imports, [])

    def test_empty_doc(self):
        assert_equal(self.table.doc.value, '')

    def test_set_doc_with_string(self):
        self.table.doc.set('hello')
        assert_equal(self.table.doc.value, 'hello')

    def test_set_doc_with_list(self):
        self.table.doc.set(['hello', 'world'])
        assert_equal(self.table.doc.value, 'hello world')


class TestVariableTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().variable_table

    def test_create(self):
        assert_equal(self.table.variables, [])

    def test_add_variables(self):
        self.table.add('${SCALAR}', ['hello'])
        self.table.add('@{LIST}', ['hello', 'world'])
        assert_true(len(self.table.variables), 2)
        assert_equal(self.table.variables[0].name, '${SCALAR}')
        assert_equal(self.table.variables[0].value, ['hello'])
        assert_equal(self.table.variables[1].name, '@{LIST}')
        assert_equal(self.table.variables[1].value, ['hello', 'world'])


class TestTestCaseTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().testcase_table

    def test_create(self):
        assert_equal(self.table.tests, [])

    def test_add_test(self):
        test = self.table.add('My name')
        assert_true(len(self.table.tests), 1)
        assert_true(self.table.tests[0] is test)
        assert_equal(test.name, 'My name')

    def test_settings(self):
        test = self.table.add('Name')
        assert_true(isinstance(test.doc, Documentation))
        assert_true(isinstance(test.tags, Tags))
        assert_true(isinstance(test.setup, Fixture))
        assert_true(isinstance(test.teardown, Fixture))
        assert_true(isinstance(test.timeout, Timeout))

    def test_set_settings(self):
        test = self.table.add('Name')
        test.doc.set('My coooool doc')
        test.tags.set(['My', 'coooool', 'tags'])
        assert_equal(test.doc.value, 'My coooool doc')
        assert_equal(test.tags.value, ['My', 'coooool', 'tags'])

    def test_add_test_row(self):
        test = NotImplemented


if __name__ == "__main__":
    unittest.main()
