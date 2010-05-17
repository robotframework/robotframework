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
        assert_true(isinstance(self.table.test_setup, Fixture))
        assert_true(isinstance(self.table.test_teardown, Fixture))
        assert_true(isinstance(self.table.test_timeout, Timeout))
        assert_true(isinstance(self.table.force_tags, Tags))
        assert_true(isinstance(self.table.default_tags, Tags))
        assert_equal(self.table.metadata, [])
        assert_equal(self.table.imports, [])

    def test_doc_default(self):
        assert_equal(self.table.doc.value, '')

    def test_set_doc_with_string(self):
        self.table.doc.set('hello')
        assert_equal(self.table.doc.value, 'hello')

    def test_set_doc_with_list(self):
        self.table.doc.set(['hello', 'world'])
        assert_equal(self.table.doc.value, 'hello world')

    def test_fixture_default(self):
        assert_equal(self.table.suite_setup.name, None)
        assert_equal(self.table.suite_setup.args, [])
        assert_false(hasattr(self.table.suite_setup, 'value'))

    def test_set_fixture(self):
        self.table.suite_teardown.set(['Name', 'a1', 'a2'])
        assert_equal(self.table.suite_teardown.name, 'Name')
        assert_equal(self.table.suite_teardown.args, ['a1', 'a2'])
        assert_false(hasattr(self.table.suite_teardown, 'value'))

    def test_set_fixture_with_empty_value(self):
        self.table.test_teardown.set([])
        assert_equal(self.table.test_teardown.name, '')
        assert_equal(self.table.test_teardown.args, [])

    def test_timeout_default(self):
        assert_equal(self.table.test_timeout.value, None)
        assert_equal(self.table.test_timeout.message, '')
        assert_false(hasattr(self.table.suite_setup, 'value'))

    def test_set_timeout(self):
        self.table.test_timeout.set(['1s', 'msg', 'in multiple', 'cell'])
        assert_equal(self.table.test_timeout.value, '1s')
        assert_equal(self.table.test_timeout.message, 'msg in multiple cell')
        assert_false(hasattr(self.table.suite_teardown, 'value'))

    def test_set_timeout_with_empty_value(self):
        self.table.test_timeout.set([])
        assert_equal(self.table.test_timeout.value, '')
        assert_equal(self.table.test_timeout.message, '')

    def test_metadata(self):
        self.table.add_metadata('Foo', 'bar')
        self.table.add_metadata('boo', ['f', 'a', 'r'])
        assert_equal(len(self.table.metadata), 2)
        assert_equal(self.table.metadata[0].name, 'Foo')
        assert_equal(self.table.metadata[0].value, 'bar')
        assert_equal(self.table.metadata[1].name, 'boo')
        assert_equal(self.table.metadata[1].value, 'f a r')

    def test_imports(self):
        self.table.add_library(['Name', 'arg'])
        self.table.add_resource(['reso.txt'])
        self.table.add_variables(['varz.py', 'a1', 'a2'])
        self.table.add_resource(['reso2.txt'])
        assert_equal(len(self.table.imports), 4)
        assert_true(all(isinstance(im, Import) for im in self.table.imports))


class TestVariableTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().variable_table

    def test_create(self):
        assert_equal(self.table.variables, [])

    def test_add_variables(self):
        self.table.add('${SCALAR}', ['hello'])
        self.table.add('${S2} =', 'hello as string')
        self.table.add('@{LIST}', ['hello', 'world'])
        assert_equal(len(self.table.variables), 3)
        assert_equal(self.table.variables[0].name, '${SCALAR}')
        assert_equal(self.table.variables[0].value, ['hello'])
        assert_equal(self.table.variables[1].name, '${S2}')
        assert_equal(self.table.variables[1].value, ['hello as string'])
        assert_equal(self.table.variables[2].name, '@{LIST}')
        assert_equal(self.table.variables[2].value, ['hello', 'world'])


class TestTestCaseTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().testcase_table
        self.test = TestCase('name')

    def test_create(self):
        assert_equal(self.table.tests, [])

    def test_add_test(self):
        test = self.table.add('My name')
        assert_true(len(self.table.tests), 1)
        assert_true(self.table.tests[0] is test)
        assert_equal(test.name, 'My name')

    def test_settings(self):
        assert_true(isinstance(self.test.doc, Documentation))
        assert_true(isinstance(self.test.tags, Tags))
        assert_true(isinstance(self.test.setup, Fixture))
        assert_true(isinstance(self.test.teardown, Fixture))
        assert_true(isinstance(self.test.timeout, Timeout))

    def test_set_settings(self):
        self.test.doc.set('My coooool doc')
        self.test.tags.set(['My', 'coooool', 'tags'])
        assert_equal(self.test.doc.value, 'My coooool doc')
        assert_equal(self.test.tags.value, ['My', 'coooool', 'tags'])

    def test_add_step(self):
        self.test.add_step(['Keyword', 'arg1', 'arg2'])
        assert_equal(len(self.test.steps), 1)
        assert_equal(self.test.steps[0].keyword, 'Keyword')
        assert_equal(self.test.steps[0].args, ['arg1', 'arg2'])


class TestKeywordTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().keyword_table
        self.kw = UserKeyword('name')

    def test_create(self):
        assert_equal(self.table.keywords, [])

    def test_add_keyword(self):
        kw = self.table.add('My name')
        assert_true(len(self.table.keywords), 1)
        assert_true(self.table.keywords[0] is kw)
        assert_equal(kw.name, 'My name')

    def test_settings(self):
        assert_true(isinstance(self.kw.doc, Documentation))
        assert_true(isinstance(self.kw.args, Arguments))
        assert_true(isinstance(self.kw.return_, Return))
        assert_true(isinstance(self.kw.timeout, Timeout))

    def test_set_settings(self):
        self.kw.doc.set('My coooool doc')
        self.kw.args.set(['${args}', 'are not', 'validated'])
        assert_equal(self.kw.doc.value, 'My coooool doc')
        assert_equal(self.kw.args.value, ['${args}', 'are not', 'validated'])

    def test_add_step(self):
        self.kw.add_step(['Keyword', 'arg1', 'arg2'])
        assert_equal(len(self.kw.steps), 1)
        assert_equal(self.kw.steps[0].keyword, 'Keyword')
        assert_equal(self.kw.steps[0].args, ['arg1', 'arg2'])


class TestStep(unittest.TestCase):

    def test_kw_only(self):
        self._test(['My kewl keyword'], 'My kewl keyword')

    def test_kw_and_args(self):
        self._test(['KW', 'first arg', '${a2}'], args=['first arg', '${a2}'])

    def test_assign_to_one_var(self):
        self._test(['${var}', 'KW'], assign=['${var}'])
        self._test(['${var}=', 'KW', 'a'], args=['a'], assign=['${var}'])
        self._test(['@{var}     =', 'KW'], assign=['@{var}'])

    def test_assign_to_multiple_var(self):
        self._test(['${v1}', '${v2}', '@{v3} =', 'KW', '${a1}', '${a2}'],
                   args=['${a1}', '${a2}'], assign=['${v1}', '${v2}', '@{v3}'])
        self._test(['${v1}=', '${v2}=', 'KW'], assign=['${v1}', '${v2}'])

    def test_assign_without_keyword(self):
        self._test(['${v1}', '${v2}'], kw='', assign=['${v1}', '${v2}'])

    def _test(self, content, kw='KW', args=[], assign=[]):
        step = Step(content)
        assert_equal(step.keyword, kw)
        assert_equal(step.args, args)
        assert_equal(step.assign, assign)


if __name__ == "__main__":
    unittest.main()
