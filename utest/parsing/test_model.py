import os
import unittest

from robot.utils.asserts import (assert_equal, assert_false, assert_none,
                                 assert_not_equal, assert_true)
from robot.parsing.model import (ForLoop, KeywordTable, Step, TestCase,
                                 TestCaseFile, TestCaseTable,
                                 TestCaseFileSettingTable, UserKeyword,
                                 VariableTable)
from robot.parsing.settings import (Arguments, Documentation, Fixture, _Import,
                                    Return, Tags, Template, Timeout)


class ForLoopWithFakeParent(ForLoop):

    def __init__(self, *args, **kws):
        ForLoop.__init__(self, self, *args, **kws)

    def report_invalid_syntax(self, message, level='ERROR'):
        pass


class TestTestCaseFile(unittest.TestCase):

    def setUp(self):
        self.tcf = TestCaseFile()

    def test_init(self):
        assert_none(self.tcf.source)
        assert_true(isinstance(self.tcf.setting_table, TestCaseFileSettingTable))
        assert_true(isinstance(self.tcf.variable_table, VariableTable))
        assert_true(isinstance(self.tcf.testcase_table, TestCaseTable))
        assert_true(isinstance(self.tcf.keyword_table, KeywordTable))

    def test_name(self):
        assert_none(self.tcf.name)
        for source, name in [('hello.txt', 'Hello'),
                             ('hello', 'Hello'),
                             ('hello_world.tsv', 'Hello World'),
                             ('HELLO_world.htm', 'HELLO world'),
                             ('1name', '1Name'),
                             ('  h i   w o r l d  .htm', 'H I   W O R L D'),
                             ('HelloWorld.txt', 'HelloWorld'),
                             ('09__h_E_l_l_o_', 'h E l l o'),
                             ('prefix__the__name', 'The  Name')]:
            self.tcf.source = os.path.abspath(source)
            assert_equal(self.tcf.name, name)


class TestSettingTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().setting_table

    def test_init(self):
        assert_true(isinstance(self.table.doc, Documentation))
        assert_true(isinstance(self.table.suite_setup, Fixture))
        assert_true(isinstance(self.table.suite_teardown, Fixture))
        assert_true(isinstance(self.table.test_setup, Fixture))
        assert_true(isinstance(self.table.test_teardown, Fixture))
        assert_true(isinstance(self.table.test_timeout, Timeout))
        assert_true(isinstance(self.table.force_tags, Tags))
        assert_true(isinstance(self.table.default_tags, Tags))
        assert_equal(self.table.metadata.data, [])
        assert_equal(self.table.imports.data, [])

    def test_doc_default(self):
        assert_equal(self.table.doc.value, '')

    def test_set_doc_with_string(self):
        self.table.doc.populate('hello')
        assert_equal(self.table.doc.value, 'hello')

    def test_set_doc_with_list(self):
        self.table.doc.populate(['hello', 'world'])
        assert_equal(self.table.doc.value, 'helloworld')

    def test_fixture_default(self):
        assert_equal(self.table.suite_setup.name, None)
        assert_equal(self.table.suite_setup.args, [])
        assert_false(hasattr(self.table.suite_setup, 'value'))

    def test_set_fixture(self):
        self.table.suite_teardown.populate(['Name', 'a1', 'a2'])
        assert_equal(self.table.suite_teardown.name, 'Name')
        assert_equal(self.table.suite_teardown.args, ['a1', 'a2'])
        assert_false(hasattr(self.table.suite_teardown, 'value'))

    def test_set_fixture_with_empty_value(self):
        self.table.test_teardown.populate([])
        assert_equal(self.table.test_teardown.name, '')
        assert_equal(self.table.test_teardown.args, [])

    def test_timeout_default(self):
        assert_equal(self.table.test_timeout.value, None)
        assert_equal(self.table.test_timeout.message, '')
        assert_false(hasattr(self.table.suite_setup, 'value'))

    def test_set_timeout(self):
        self.table.test_timeout.populate(['1s', 'msg', 'in multiple', 'cell'])
        assert_equal(self.table.test_timeout.value, '1s')
        assert_equal(self.table.test_timeout.message, 'msg in multiple cell')
        assert_false(hasattr(self.table.suite_teardown, 'value'))

    def test_set_timeout_with_empty_value(self):
        self.table.test_timeout.populate([])
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
        self.table.metadata[0] = self.table.metadata[1]
        assert_equal(self.table.metadata[0].name, 'boo')
        assert_equal(self.table.metadata[0].value, 'f a r')

    def test_imports(self):
        self._verify_import(self.table.add_library('Name'), 'Name')
        self._verify_import(self.table.add_resource('reso.txt'), 'reso.txt')
        self._verify_import(self.table.add_variables('varz.py'), 'varz.py')
        self._verify_import(self.table.add_variables('./v2.py', ['a1', 'a2']),
                            './v2.py', ['a1', 'a2'])
        self._verify_import(self.table.add_library('N2', ['1', '2', '3', '4']),
                            'N2', ['1', '2', '3', '4'])
        assert_equal(len(self.table.imports), 5)
        assert_true(all(isinstance(im, _Import) for im in self.table.imports))
        self.table.imports[1] = self.table.imports[0]
        assert_equal(self.table.imports[1].name, 'Name')

    def test_resource_with_invalid_args(self):
        reso = self.table.add_resource('reso.txt', ['invalid', 'args'])
        self._verify_import(reso, 'reso.txt invalid args')

    def test_library_with_name(self):
        lib = self.table.add_library('Name', ['WITH NAME', 'New name'])
        self._verify_import(lib, 'Name', [], 'New name')
        lib = self.table.add_library('Orig', ['a1', 'a2', 'WITH NAME', 'New'])
        self._verify_import(lib, 'Orig', ['a1', 'a2'], 'New')

    def _verify_import(self, imp, name, args=[], alias=None):
        assert_equal(imp.name, name)
        assert_equal(imp.args, args)
        assert_equal(imp.alias, alias)
        assert_equal(imp.type, type(imp).__name__)

    def test_old_style_headers_are_ignored(self):
        self.table.set_header(['Settings', 'Value', 'value', 'Value'])
        assert_equal(self.table.header, ['Settings'])

    def test_len(self):
        assert_equal(len(self.table), 0)
        self.table.add_library('SomeLib')
        assert_equal(len(self.table), 1)
        self.table.doc.value = 'Some doc'
        self.table.add_metadata('meta name', 'content')
        assert_equal(len(self.table), 3)


class TestVariableTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().variable_table

    def test_init(self):
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

    def test_empty_value(self):
        self.table.add('${V1}', [])
        self.table.add('${V2}', '')
        assert_equal(self.table.variables[0].value, [''])
        assert_equal(self.table.variables[1].value, [''])

    def test_variable_syntax_is_not_verified(self):
        self.table.add('not var', 'the value')
        assert_equal(self.table.variables[0].name, 'not var')
        assert_equal(self.table.variables[0].value, ['the value'])

    def test_old_style_headers_are_ignored(self):
        self.table.set_header(['Variable', 'value', 'Value'])
        assert_equal(self.table.header, ['Variable'])

    def test_len(self):
        self.table.set_header(['Variable', 'value', 'Value'])
        assert_equal(len(self.table), 0)
        self.table.add('${a var}', 'some')
        self.table.add('@{b var}', 's', 'ome')
        assert_equal(len(self.table), 2)


class TestTestCaseTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().testcase_table
        self.test = TestCase(None, 'name')

    def test_init(self):
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
        self.test.doc.populate('My coooool doc')
        self.test.tags.populate(['My', 'coooool', 'tags'])
        assert_equal(self.test.doc.value, 'My coooool doc')
        assert_equal(self.test.tags.value, ['My', 'coooool', 'tags'])

    def test_add_step(self):
        step = self.test.add_step(['Keyword', 'arg1', 'arg2'])
        assert_equal(self.test.steps, [step])
        assert_equal(step.name, 'Keyword')
        assert_equal(step.args, ['arg1', 'arg2'])

    def test_add_for_loop(self):
        loop = self.test.add_for_loop(['${var}', 'IN', 'value'])
        assert_equal(self.test.steps, [loop])

    def test_old_style_headers_are_ignored(self):
        self.table.set_header(['test case', 'Action', 'Arg', 'Argument'])
        assert_equal(self.table.header, ['test case'])

    def test_len(self):
        self.table.set_header(['Test Case'])
        assert_equal(len(self.table), 0)
        self.table.add('A test')
        self.table.add('B test')
        assert_equal(len(self.table), 2)


class TestKeywordTable(unittest.TestCase):

    def setUp(self):
        self.table = TestCaseFile().keyword_table
        self.kw = UserKeyword(None, 'name')

    def test_init(self):
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
        assert_true(isinstance(self.kw.teardown, Fixture))

    def test_set_settings(self):
        self.kw.doc.populate('My coooool doc')
        self.kw.args.populate(['${args}', 'are not', 'validated'])
        assert_equal(self.kw.doc.value, 'My coooool doc')
        assert_equal(self.kw.args.value, ['${args}', 'are not', 'validated'])

    def test_add_step(self):
        step = self.kw.add_step(['Keyword', 'arg1', 'arg2'])
        assert_equal(self.kw.steps, [step])
        assert_equal(step.name, 'Keyword')
        assert_equal(step.args, ['arg1', 'arg2'])

    def test_add_for_loop(self):
        loop = self.kw.add_for_loop(['${var}', 'IN', 'value'])
        assert_equal(self.kw.steps, [loop])

    def test_old_style_headers_are_ignored(self):
        self.table.set_header(['keywords', 'Action', 'Arg', 'Argument'])
        assert_equal(self.table.header, ['keywords'])

    def test_len(self):
        self.table.set_header(['Keywords'])
        assert_equal(len(self.table), 0)
        self.table.add('A kw')
        self.table.add('B keyword')
        assert_equal(len(self.table), 2)


class TestStep(unittest.TestCase):

    def test_kw_only(self):
        self._test(['My kewl keyword'], 'My kewl keyword')

    def test_kw_and_args(self):
        self._test(['KW', 'first arg', '${a2}'], args=['first arg', '${a2}'])

    def test_assign_to_one_var(self):
        self._test(['${var}', 'KW'], assign=['${var}'])
        self._test(['${var}=', 'KW', 'a'], args=['a'], assign=['${var}='])
        self._test(['@{var}     =', 'KW'], assign=['@{var}     ='])

    def test_assign_to_multiple_var(self):
        self._test(['${v1}', '${v2}', '@{v3}=', 'KW', '${a1}', '${a2}'],
                   args=['${a1}', '${a2}'], assign=['${v1}', '${v2}', '@{v3}='])
        self._test(['${v1}=', '${v2} =', 'KW'], assign=['${v1}=', '${v2} ='])

    def test_assign_without_keyword(self):
        self._test(['${v1}', '${v2}'], kw=None, assign=['${v1}', '${v2}'])

    def test_is_comment(self):
        assert_true(Step([], comment="comment").is_comment())
        assert_false(Step(['KW'], comment="comment").is_comment())

    def test_representation(self):
        assert_equal(Step(['${v}, @{list}=', 'KW', 'arg']).as_list(),
                      ['${v}, @{list}=', 'KW', 'arg'])

    def _test(self, content, kw='KW', args=[], assign=[]):
        step = Step(content)
        assert_equal(step.name, kw)
        assert_equal(step.args, args)
        assert_equal(step.assign, assign)


class TestForLoop(unittest.TestCase):

    def test_normal_for(self):
        self._test(['${var}', 'IN', 'value1', 'value2'],
                   ['${var}'], ['value1', 'value2'])
        self._test(['${v1}', '${v2}', 'in', '@{values}'],
                   ['${v1}', '${v2}'], ['@{values}'])
        self._test(['${v1}', '${v2}', '${v3}', 'IN'],
                   ['${v1}', '${v2}', '${v3}'], [])
        self._test(['${x}', 'IN', 'IN RANGE', 'IN', 'IN RANGE', 'X'],
                   ['${x}'], ['IN RANGE', 'IN', 'IN RANGE', 'X'])

    def test_variable_format_is_not_verified(self):
        self._test(['whatever', 'here', 'in', 'value1', 'value2'],
                   ['whatever', 'here'], ['value1', 'value2'])

    def test_without_vars(self):
        self._test(['IN', 'value1', 'value2'], [], ['value1', 'value2'])

    def test_without_in(self):
        self._test(['whatever', 'here'], ['whatever', 'here'], [])

    def test_in_range(self):
        self._test(['${i}', 'IN RANGE', '100'], ['${i}'], ['100'],
                flavor='IN RANGE')
        self._test(['what', 'ever', 'in range', 'IN', 'whatever'],
                   ['what', 'ever'], ['IN', 'whatever'],
                   flavor='IN RANGE')

    def test_representation(self):
        ForLoop = ForLoopWithFakeParent
        assert_equal(ForLoop(['${var}', 'IN', 'value1', 'value2']).as_list(),
                      ['FOR', '${var}', 'IN', 'value1', 'value2'])
        assert_equal(ForLoop(['${v2}', '${v2}', 'IN RANGE', '100']).as_list(),
                      ['FOR', '${v2}', '${v2}', 'IN RANGE', '100'])

    def test_in_zip(self):
        self._test(['${i}', '${item}', 'in zip', '${list1}', '${list2}'],
                   ['${i}', '${item}'], ['${list1}', '${list2}'],
                   flavor='IN ZIP')

    def _test(self, content, vars, items, flavor='IN'):
        loop = ForLoopWithFakeParent(content)
        assert_equal(loop.vars, vars)
        assert_equal(loop.items, items)
        assert_equal(loop.flavor, flavor)


class TestSettings(unittest.TestCase):

    def test_timeout(self):
        timeout = Timeout('Timeout')
        assert_equal(timeout.as_list(), ['Timeout'])
        timeout.message='boo'
        assert_equal(timeout.as_list(), ['Timeout', '', 'boo'])
        timeout.message=''
        timeout.value='1 second'
        assert_equal(timeout.as_list(), ['Timeout', '1 second'])
        timeout.message='boo'
        assert_equal(timeout.as_list(), ['Timeout', '1 second', 'boo'])

    def test_tags(self):
        tags = Tags('Tags')
        assert_equal(tags.as_list(), ['Tags'])
        tags.value = ['tag1','tag2']
        assert_equal(tags.as_list(), ['Tags', 'tag1', 'tag2'])

    def test_fixtures(self):
        fixture = Fixture('Teardown')
        assert_equal(fixture.as_list(), ['Teardown'])
        fixture.name = 'Keyword'
        assert_equal(fixture.as_list(), ['Teardown', 'Keyword'])
        fixture.args = ['arg1', 'arg2']
        assert_equal(fixture.as_list(), ['Teardown', 'Keyword', 'arg1', 'arg2'])
        fixture.name = ''
        assert_equal(fixture.as_list(), ['Teardown', '', 'arg1', 'arg2'])

    def test_template(self):
        template = Template('Template')
        assert_equal(template.as_list(), ['Template'])
        template.value = 'value'
        assert_equal(template.as_list(), ['Template', 'value'])


class TestCopy(unittest.TestCase):

    def test_test_case_copy(self):
        test = self._create_test()
        copied = test.copy('Copied')
        assert_equal(copied.name, 'Copied')
        assert_equal(copied.tags.value, test.tags.value)
        assert_not_equal(copied.steps[0], test.steps[0])
        test.add_step(['A new KW'])
        assert_not_equal(len(test.steps), len(copied.steps))

    def test_keyword_copy(self):
        kw = self._create_keyword()
        copied = kw.copy('New KW')
        assert_equal(copied.name, 'New KW')
        assert_equal(copied.args.value, kw.args.value)

    def _create_test(self):
        test = TestCase(TestCaseTable(None), 'Test name')
        test.tags = Tags('Force Tags')
        test.tags.value = ['1', '2', '3']
        test.add_step(['Log', 'Foo'])
        return test

    def _create_keyword(self):
        kw = UserKeyword(KeywordTable(None), 'KW')
        kw.args.value = ['${a1}', '${a2}']
        kw.add_step(['Some step', '${a1}'])
        return kw


if __name__ == "__main__":
    unittest.main()
