
import unittest

from robot.utils.asserts import *


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

    def test_variable_table(self):
        assert_equal(self.table.variables, [])

    def test_create_scalar(self):
        self.table.create('${VAR}', 'hello')
        assert_true(len(self.table.variables), 1)
        assert_equal(self.table.variables[0].name, '${VAR}')
        assert_equal(self.table.variables[0].value, ['hello'])

    def test_create_list(self):
        self.table.create('@{VAR}', ['hello', 'world'])


class TestCaseFile(object):

    def __init__(self, source=None):
        self.source = source
        self.setting_table = SettingTable()
        self.variable_table = VariableTable()
        self.testcase_table = TestCaseTable()
        self.keyword_table = KeywordTable()

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.testcase_table, self.keyword_table]:
            yield table

    def edited(self):
        return any(table.edited() for table in self)


class DataTable(object):

    def edited(self):
        return False

class SettingTable(DataTable):

    def __init__(self):
        self.doc = Documentation()
        self.suite_setup = Fixture()
        self.suite_teardown = Fixture()
        self.metadata = Metadata()
        self.test_setup = Fixture()
        self.test_teardown = Fixture()
        self.test_timeout = Timeout()
        self.force_tags = Tags()
        self.default_tags = Tags()
        self.imports = []

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.metadata, self.test_setup, self.test_teardown,
                        self.test_timeout, self.force_tags, self.default_tags] \
                        + self.imports:
            yield setting

    def edited(self):
        return any(setting.edited() for setting in self)

class VariableTable(DataTable):
    pass

class TestCaseTable(DataTable):
    pass

class KeywordTable(DataTable):
    pass


class Setting(object):

    def __init__(self):
        self.value = []

    def set(self, value):
        self.value = value

    def edited(self):
        return bool(self.value)

class Documentation(Setting):

    def set(self, value):
        if not isinstance(value, basestring):
            value = ' '.join(value)
        self.value = value

class Fixture(Setting):
    pass

class Metadata(Setting):
    pass

class Timeout(Setting):
    pass

class Tags(Setting):
    pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_create_test_case_file']
    unittest.main()