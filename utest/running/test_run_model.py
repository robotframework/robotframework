import copy
import os
import tempfile
import unittest
import warnings
from pathlib import Path

from robot import api, model
from robot.model.modelobject import ModelObject
from robot.running import (Break, Continue, Error, For, If, IfBranch, Keyword,
                           Return, TestCase, TestDefaults, TestSuite, Try, TryBranch,
                           While)
from robot.running.model import ResourceFile, UserKeyword
from robot.utils.asserts import (assert_equal, assert_false, assert_not_equal,
                                 assert_raises, assert_true)

MISC_DIR = (Path(__file__).parent / '../../atest/testdata/misc').resolve()


class TestModelTypes(unittest.TestCase):

    def test_suite_setup_and_teardown(self):
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
    path = Path(os.getenv('TEMPDIR') or tempfile.gettempdir(),
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
    [Tags]    tag
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

    def test_from_file_system_with_defaults(self):
        defaults = TestDefaults(tags=('from defaults',), timeout='10s')
        suite = TestSuite.from_file_system(self.path, defaults=defaults)
        self._verify_suite(suite, tags=('from defaults', 'tag'), timeout='10s')

    def test_from_model(self):
        model = api.get_model(self.data)
        suite = TestSuite.from_model(model)
        self._verify_suite(suite, name='')

    def test_from_model_containing_source(self):
        model = api.get_model(self.path)
        suite = TestSuite.from_model(model)
        self._verify_suite(suite)

    def test_from_model_with_defaults(self):
        model = api.get_model(self.path)
        defaults = TestDefaults(tags=('from defaults',), timeout='10s')
        suite = TestSuite.from_model(model, defaults=defaults)
        self._verify_suite(suite, tags=('from defaults', 'tag'), timeout='10s')

    def test_from_model_with_custom_name(self):
        for source in [self.data, self.path]:
            model = api.get_model(source)
            with warnings.catch_warnings(record=True) as w:
                suite = TestSuite.from_model(model, name='Custom name')
                assert_equal(str(w[0].message),
                             "'name' argument of 'TestSuite.from_model' is deprecated. "
                             "Set the name to the returned suite separately.")
            self._verify_suite(suite, 'Custom name')

    def test_from_string(self):
        suite = TestSuite.from_string(self.data)
        self._verify_suite(suite, name='')

    def test_from_string_with_config(self):
        suite = TestSuite.from_string(self.data.replace('Test Cases', 'Testit'),
                                      lang='Finnish', curdir='.')
        self._verify_suite(suite, name='')

    def test_from_string_with_defaults(self):
        defaults = TestDefaults(tags=('from defaults',), timeout='10s')
        suite = TestSuite.from_string(self.data, defaults=defaults)
        self._verify_suite(suite, name='', tags=('from defaults', 'tag'), timeout='10s')

    def _verify_suite(self, suite, name='Test Run Model', tags=('tag',),
                      timeout=None, rpa=False):
        assert_equal(suite.name, name)
        assert_equal(suite.doc, 'Some text.')
        assert_equal(suite.rpa, rpa)
        assert_equal(suite.resource.imports[0].type, 'LIBRARY')
        assert_equal(suite.resource.imports[0].name, 'ExampleLibrary')
        assert_equal(suite.resource.variables[0].name, '${VAR}')
        assert_equal(suite.resource.variables[0].value, ('Value',))
        assert_equal(suite.resource.keywords[0].name, 'Keyword')
        assert_equal(suite.resource.keywords[0].body[0].name, 'Log')
        assert_equal(suite.resource.keywords[0].body[0].args, ('Hello!',))
        assert_equal(suite.tests[0].name, 'Example')
        assert_equal(suite.tests[0].tags, tags)
        assert_equal(suite.tests[0].timeout, timeout)
        assert_equal(suite.tests[0].setup.name, 'No Operation')
        assert_equal(suite.tests[0].body[0].name, 'Keyword')


class TestCopy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.suite = TestSuite.from_file_system(MISC_DIR)

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
    source = MISC_DIR / 'pass_and_fail.robot'

    @classmethod
    def setUpClass(cls):
        cls.suite = TestSuite.from_file_system(cls.source)

    def test_suite(self):
        assert_equal(self.suite.source, self.source)
        assert_false(hasattr(self.suite, 'lineno'))

    def test_import(self):
        self._assert_lineno_and_source(self.suite.resource.imports[0], 5)

    def test_import_without_source(self):
        suite = TestSuite()
        suite.resource.imports.library('Example')
        assert_equal(suite.resource.imports[0].source, None)
        assert_equal(suite.resource.imports[0].directory, None)

    def test_import_with_non_existing_source(self):
        for source in Path('dummy!'), Path('dummy/example/path'):
            suite = TestSuite(source=source)
            suite.resource.imports.library('Example')
            assert_equal(suite.resource.imports[0].source, source)
            assert_equal(suite.resource.imports[0].directory, source.parent)

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


class TestToFromDictAndJson(unittest.TestCase):

    def test_keyword(self):
        self._verify(Keyword(), name='')
        self._verify(Keyword('Name'), name='Name')
        self._verify(Keyword('N', tuple('args'), ('${result}',)),
                     name='N', args=list('args'), assign=['${result}'])
        self._verify(Keyword('Setup', type=Keyword.SETUP, lineno=1),
                     name='Setup', lineno=1)

    def test_for(self):
        self._verify(For(), type='FOR', variables=(), flavor='IN', values=(), body=[])
        self._verify(For(['${i}'], 'IN RANGE', ['10'], lineno=2),
                     type='FOR', variables=('${i}',), flavor='IN RANGE', values=('10',),
                     body=[], lineno=2)
        self._verify(For(['${i}', '${a}'], 'IN ENUMERATE', ['cat', 'dog'], start='1'),
                     type='FOR', variables=('${i}', '${a}'), flavor='IN ENUMERATE',
                     values=('cat', 'dog'), start='1', body=[])

    def test_while(self):
        self._verify(While(), type='WHILE', body=[])
        self._verify(While('1 > 0', '1 min'),
                     type='WHILE', condition='1 > 0', limit='1 min', body=[])
        self._verify(While('True', lineno=3, error='x'),
                     type='WHILE', condition='True', body=[], lineno=3, error='x')

    def test_if(self):
        self._verify(If(), type='IF/ELSE ROOT', body=[])
        self._verify(If(lineno=4, error='E'),
                     type='IF/ELSE ROOT', body=[], lineno=4, error='E')

    def test_if_branch(self):
        self._verify(IfBranch(), type='IF', condition=None, body=[])
        self._verify(IfBranch(If.ELSE_IF, '1 > 0'),
                     type='ELSE IF', condition='1 > 0', body=[])
        self._verify(IfBranch(If.ELSE, lineno=5),
                     type='ELSE', body=[], lineno=5)

    def test_if_structure(self):
        root = If()
        root.body.create_branch(If.IF, '$c').body.create_keyword('K1')
        root.body.create_branch(If.ELSE).body.create_keyword('K2', ['a'])
        self._verify(root,
                     type='IF/ELSE ROOT',
                     body=[{'type': 'IF', 'condition': '$c', 'body': [{'name': 'K1'}]},
                           {'type': 'ELSE', 'body': [{'name': 'K2', 'args': ['a']}]}])

    def test_try(self):
        self._verify(Try(), type='TRY/EXCEPT ROOT', body=[])
        self._verify(Try(lineno=6, error='E'),
                     type='TRY/EXCEPT ROOT', body=[], lineno=6, error='E')

    def test_try_branch(self):
        self._verify(TryBranch(), type='TRY', body=[])
        self._verify(TryBranch(Try.EXCEPT), type='EXCEPT', patterns=(), body=[])
        self._verify(TryBranch(Try.EXCEPT, ['Pa*'], 'glob', '${err}'), type='EXCEPT',
                     patterns=('Pa*',), pattern_type='glob', variable='${err}', body=[])
        self._verify(TryBranch(Try.ELSE, lineno=7), type='ELSE', body=[], lineno=7)
        self._verify(TryBranch(Try.FINALLY, lineno=8), type='FINALLY', body=[], lineno=8)

    def test_try_structure(self):
        root = Try()
        root.body.create_branch(Try.TRY).body.create_keyword('K1')
        root.body.create_branch(Try.EXCEPT).body.create_keyword('K2')
        root.body.create_branch(Try.ELSE).body.create_keyword('K3')
        root.body.create_branch(Try.FINALLY).body.create_keyword('K4')
        self._verify(root,
                     type='TRY/EXCEPT ROOT',
                     body=[{'type': 'TRY', 'body': [{'name': 'K1'}]},
                           {'type': 'EXCEPT', 'patterns': (), 'body': [{'name': 'K2'}]},
                           {'type': 'ELSE', 'body': [{'name': 'K3'}]},
                           {'type': 'FINALLY', 'body': [{'name': 'K4'}]}])

    def test_return_continue_break(self):
        self._verify(Return(), type='RETURN', values=())
        self._verify(Return(('x', 'y'), lineno=9, error='E'),
                     type='RETURN', values=('x', 'y'), lineno=9, error='E')
        self._verify(Continue(), type='CONTINUE')
        self._verify(Continue(lineno=10, error='E'),
                     type='CONTINUE', lineno=10, error='E')
        self._verify(Break(), type='BREAK')
        self._verify(Break(lineno=11, error='E'),
                     type='BREAK', lineno=11, error='E')

    def test_error(self):
        self._verify(Error(), type='ERROR', values=())
        self._verify(Error(('bad', 'things')), type='ERROR', values=('bad', 'things'))

    def test_test(self):
        self._verify(TestCase(), name='', body=[])
        self._verify(TestCase('N', 'D', 'T', '1s', lineno=12),
                     name='N', doc='D', tags=('T',), timeout='1s', lineno=12, body=[])
        self._verify(TestCase(template='K'), name='', body=[], template='K')

    def test_test_structure(self):
        test = TestCase('TC')
        test.setup.config(name='Setup')
        test.teardown.config(name='Teardown', args='a')
        test.body.create_keyword('K1')
        test.body.create_if().body.create_branch().body.create_keyword('K2')
        self._verify(test,
                     name='TC',
                     setup={'name': 'Setup'},
                     teardown={'name': 'Teardown', 'args': ['a']},
                     body=[{'name': 'K1'},
                           {'type': 'IF/ELSE ROOT',
                            'body': [{'type': 'IF', 'condition': None,
                                      'body': [{'name': 'K2'}]}]}])

    def test_suite(self):
        self._verify(TestSuite(), name='', resource={})
        self._verify(TestSuite('N', 'D', {'M': 'V'}, 'x.robot', rpa=True),
                     name='N', doc='D', metadata={'M': 'V'}, source='x.robot', rpa=True,
                     resource={})

    def test_suite_structure(self):
        suite = TestSuite('Root')
        suite.setup.config(name='Setup')
        suite.teardown.config(name='Teardown', args='a')
        suite.tests.create('T1').body.create_keyword('K')
        suite.suites.create('Child').tests.create('T2')
        self._verify(suite,
                     name='Root',
                     setup={'name': 'Setup'},
                     teardown={'name': 'Teardown', 'args': ['a']},
                     tests=[{'name': 'T1', 'body': [{'name': 'K'}]}],
                     suites=[{'name': 'Child',
                              'tests': [{'name': 'T2', 'body': []}],
                              'resource': {}}],
                     resource={})

    def test_user_keyword(self):
        self._verify(UserKeyword(), name='', body=[])
        self._verify(UserKeyword('N', ('a',), 'd', 't', ('r',), 't', 1, error='E'),
                     name='N',
                     args=('a',),
                     doc='d',
                     tags=('t',),
                     return_=('r',),
                     timeout='t',
                     lineno=1,
                     error='E',
                     body=[])

    def test_user_keyword_structure(self):
        uk = UserKeyword('UK')
        uk.body.create_keyword('K1')
        uk.body.create_if().body.create_branch(condition='$c').body.create_keyword('K2')
        uk.teardown.config(name='Teardown')
        self._verify(uk, name='UK',
                     body=[{'name': 'K1'},
                           {'type': 'IF/ELSE ROOT',
                            'body': [{'type': 'IF', 'condition': '$c',
                                      'body': [{'name': 'K2'}]}]}],
                     teardown={'name': 'Teardown'})

    def test_resource_file(self):
        self._verify(ResourceFile())
        resource = ResourceFile('x.resource', doc='doc')
        resource.imports.library('L', ['a'], 'A', 1)
        resource.imports.resource('R', 2)
        resource.imports.variables('V', ['a'], 3)
        resource.variables.create('${x}', ('value',))
        resource.variables.create('@{y}', ('v1', 'v2'), lineno=4)
        resource.variables.create('&{z}', ['k=v'], error='E')
        resource.keywords.create('UK').body.create_keyword('K')
        self._verify(resource,
                     source='x.resource',
                     doc='doc',
                     imports=[{'type': 'LIBRARY', 'name': 'L', 'args': ('a',),
                               'alias': 'A', 'lineno': 1},
                              {'type': 'RESOURCE', 'name': 'R', 'lineno': 2},
                              {'type': 'VARIABLES', 'name': 'V', 'args': ('a',),
                               'lineno': 3}],
                     variables=[{'name': '${x}', 'value': ('value',)},
                                {'name': '@{y}', 'value': ('v1', 'v2'), 'lineno': 4},
                                {'name': '&{z}', 'value': ('k=v',), 'error': 'E'}],
                     keywords=[{'name': 'UK', 'body': [{'name': 'K'}]}])

    def test_bigger_suite_structure(self):
        suite = TestSuite.from_file_system(MISC_DIR)
        self._verify(suite, **suite.to_dict())

    def _verify(self, obj, **expected):
        data = obj.to_dict()
        self.assertListEqual(list(data), list(expected))
        self.assertDictEqual(data, expected)
        roundtrip = type(obj).from_dict(data).to_dict()
        self.assertDictEqual(roundtrip, expected)
        roundtrip = type(obj).from_json(obj.to_json()).to_dict()
        self.assertDictEqual(roundtrip, expected)


if __name__ == '__main__':
    unittest.main()
