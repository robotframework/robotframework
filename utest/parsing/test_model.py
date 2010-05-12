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
        assert_false(self.tcf.setting_table.edited())
        assert_false(self.tcf.variable_table.edited())
        self.tcf.setting_table.doc.set('content')
        assert_true(self.tcf.edited())
        assert_true(self.tcf.setting_table.edited())
        assert_false(self.tcf.variable_table.edited())


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

    def test_set_doc(self):
        self.table.doc.set('hello')
        assert_equal(self.table.doc.value, 'hello')
        self.table.doc.set(['hello', 'world'])
        assert_equal(self.table.doc.value, 'hello world')


class TestVariableTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().variable_table

    def _test_variable_table(self):
        assert_equal(self.table.variables, [])

    def _test_create_scalar(self):
        self.table.create('${VAR}', 'hello')
        assert_true(len(self.table.variables), 1)
        assert_equal(self.table.variables[0].name, '${VAR}')
        assert_equal(self.table.variables[0].value, ['hello'])

    def _test_create_list(self):
        self.table.create('@{VAR}', ['hello', 'world'])


if __name__ == "__main__":
    unittest.main()
