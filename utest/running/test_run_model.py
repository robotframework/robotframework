import copy
import json
import os
import tempfile
import unittest
import warnings
from inspect import getattr_static
from pathlib import Path

from jsonschema import Draft202012Validator

from robot import api, model
from robot.model.modelobject import ModelObject
from robot.parsing import get_resource_model
from robot.running import (Break, Continue, Error, For, If, IfBranch, Keyword,
                           Return, ResourceFile, TestCase, TestDefaults, TestSuite,
                           Try, TryBranch, UserKeyword, Var, While)
from robot.utils.asserts import assert_equal, assert_false, assert_not_equal


CURDIR = Path(__file__).resolve().parent
MISCDIR = (CURDIR / '../../atest/testdata/misc').resolve()


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
    Log    ${CURDIR}
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
        self._verify_suite(suite, curdir=str(self.path.parent))

    def test_from_file_system_with_multiple_paths(self):
        suite = TestSuite.from_file_system(self.path, self.path)
        assert_equal(suite.name, 'Test Run Model & Test Run Model')
        self._verify_suite(suite.suites[0], curdir=str(self.path.parent))
        self._verify_suite(suite.suites[1], curdir=str(self.path.parent))

    def test_from_file_system_with_config(self):
        suite = TestSuite.from_file_system(self.path, process_curdir=False)
        self._verify_suite(suite)

    def test_from_file_system_with_defaults(self):
        defaults = TestDefaults(tags=('from defaults',), timeout='10s')
        suite = TestSuite.from_file_system(self.path, defaults=defaults)
        self._verify_suite(suite, tags=('from defaults', 'tag'), timeout='10s',
                           curdir=str(self.path.parent))

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
        self._verify_suite(suite, name='', curdir='.')

    def test_from_string_with_defaults(self):
        defaults = TestDefaults(tags=('from defaults',), timeout='10s')
        suite = TestSuite.from_string(self.data, defaults=defaults)
        self._verify_suite(suite, name='', tags=('from defaults', 'tag'), timeout='10s')

    def _verify_suite(self, suite, name='Test Run Model', tags=('tag',),
                      timeout=None, curdir='${CURDIR}'):
        curdir = curdir.replace('\\', '\\\\')
        assert_equal(suite.name, name)
        assert_equal(suite.doc, 'Some text.')
        assert_equal(suite.rpa, False)
        assert_equal(suite.resource.imports[0].type, 'LIBRARY')
        assert_equal(suite.resource.imports[0].name, 'ExampleLibrary')
        assert_equal(suite.resource.variables[0].name, '${VAR}')
        assert_equal(suite.resource.variables[0].value, ('Value',))
        assert_equal(suite.resource.keywords[0].name, 'Keyword')
        assert_equal(suite.resource.keywords[0].body[0].name, 'Log')
        assert_equal(suite.resource.keywords[0].body[0].args, (curdir,))
        assert_equal(suite.tests[0].name, 'Example')
        assert_equal(suite.tests[0].tags, tags)
        assert_equal(suite.tests[0].timeout, timeout)
        assert_equal(suite.tests[0].setup.name, 'No Operation')
        assert_equal(suite.tests[0].body[0].name, 'Keyword')


class TestCopy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.suite = TestSuite.from_file_system(MISCDIR)

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
            if (attr in ('parent', 'owner')
                    or isinstance(getattr_static(model1, attr, None), property)):
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
        return id(value1) == id(copy.deepcopy(value1))


class TestLineNumberAndSource(unittest.TestCase):
    source = MISCDIR / 'pass_and_fail.robot'

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

    @classmethod
    def setUpClass(cls):
        with open(CURDIR / '../../doc/schema/running.json') as file:
            schema = json.load(file)
        cls.validator = Draft202012Validator(schema=schema)

    def test_keyword(self):
        self._verify(Keyword(), name='')
        self._verify(Keyword('Name'), name='Name')
        self._verify(Keyword('N', 'args', ('${result}',)),
                     name='N', args=tuple('args'), assign=('${result}',))
        self._verify(Keyword('Setup', type=Keyword.SETUP, lineno=1),
                     name='Setup', lineno=1)

    def test_for(self):
        self._verify(For(), type='FOR', assign=(), flavor='IN', values=(), body=[])
        self._verify(For(['${i}'], 'IN RANGE', ['10'], lineno=2),
                     type='FOR', assign=('${i}',), flavor='IN RANGE', values=('10',),
                     body=[], lineno=2)
        self._verify(For(['${i}', '${a}'], 'IN ENUMERATE', ['cat', 'dog'], start='1'),
                     type='FOR', assign=('${i}', '${a}'), flavor='IN ENUMERATE',
                     values=('cat', 'dog'), start='1', body=[])

    def test_old_for_json(self):
        assert_equal(For.from_dict({'variables': ('${x}',)}).assign, ('${x}',))

    def test_while(self):
        self._verify(While(), type='WHILE', body=[])
        self._verify(While('1 > 0', '1 min'),
                     type='WHILE', condition='1 > 0', limit='1 min', body=[])
        self._verify(While(limit='1', on_limit='PASS'),
                     type='WHILE', limit='1', on_limit='PASS', body=[])
        self._verify(While(limit='1', on_limit_message='Ooops!'),
                     type='WHILE', limit='1', on_limit_message='Ooops!', body=[])
        self._verify(While('True', lineno=3, error='x'),
                     type='WHILE', condition='True', body=[], lineno=3, error='x')

    def test_while_structure(self):
        root = While('True')
        root.body.create_keyword('K', 'a')
        root.body.create_while('False').body.create_keyword('W')
        root.body.create_break()
        self._verify(root, type='WHILE', condition='True',
                     body=[{'name': 'K', 'args': ('a',)},
                           {'type': 'WHILE', 'condition': 'False',
                            'body': [{'name': 'W'}]},
                           {'type': 'BREAK'}])

    def test_if(self):
        self._verify(If(), type='IF/ELSE ROOT', body=[])
        self._verify(If(lineno=4, error='E'),
                     type='IF/ELSE ROOT', body=[], lineno=4, error='E')

    def test_if_branch(self):
        self._verify(IfBranch(), type='IF', body=[])
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
                           {'type': 'ELSE', 'body': [{'name': 'K2', 'args': ('a',)}]}])

    def test_try(self):
        self._verify(Try(), type='TRY/EXCEPT ROOT', body=[])
        self._verify(Try(lineno=6, error='E'),
                     type='TRY/EXCEPT ROOT', body=[], lineno=6, error='E')

    def test_try_branch(self):
        self._verify(TryBranch(), type='TRY', body=[])
        self._verify(TryBranch(Try.EXCEPT), type='EXCEPT', patterns=(), body=[])
        self._verify(TryBranch(Try.EXCEPT, ['Pa*'], 'glob', '${err}'), type='EXCEPT',
                     patterns=('Pa*',), pattern_type='glob', assign='${err}', body=[])
        self._verify(TryBranch(Try.ELSE, lineno=7), type='ELSE', body=[], lineno=7)
        self._verify(TryBranch(Try.FINALLY, lineno=8), type='FINALLY', body=[], lineno=8)

    def test_old_try_branch_json(self):
        assert_equal(TryBranch.from_dict({'variable': '${x}'}).assign, '${x}')

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
        self._verify(Return(), type='RETURN')
        self._verify(Return(('x', 'y'), lineno=9, error='E'),
                     type='RETURN', values=('x', 'y'), lineno=9, error='E')
        self._verify(Continue(), type='CONTINUE')
        self._verify(Continue(lineno=10, error='E'),
                     type='CONTINUE', lineno=10, error='E')
        self._verify(Break(), type='BREAK')
        self._verify(Break(lineno=11, error='E'),
                     type='BREAK', lineno=11, error='E')

    def test_var(self):
        self._verify(Var(), type='VAR', name='', value=())
        self._verify(Var('${x}', 'y', 'TEST', '-', lineno=1, error='err'),
                     type='VAR', name='${x}', value=('y',), scope='TEST', separator='-',
                     lineno=1, error='err')

    def test_error(self):
        self._verify(Error(), type='ERROR', values=(), error='')
        self._verify(Error(('x', 'y'), error='Bad things happened!'),
                     type='ERROR', values=('x', 'y'), error='Bad things happened!')

    def test_test(self):
        self._verify(TestCase(), name='', body=[])
        self._verify(TestCase('N', 'D', 'T', '1s', lineno=12),
                     name='N', doc='D', tags=('T',), timeout='1s', lineno=12, body=[])
        self._verify(TestCase(template='K'), name='', body=[], template='K')

    def test_test_structure(self):
        test = TestCase('TC')
        test.setup.config(name='Setup')
        test.teardown.config(name='Teardown', args='a')
        test.body.create_var('${x}', 'a')
        test.body.create_keyword('K1', ['${x}'])
        test.body.create_if().body.create_branch('IF', '$c').body.create_keyword('K2')
        self._verify(test,
                     name='TC',
                     setup={'name': 'Setup'},
                     teardown={'name': 'Teardown', 'args': ('a',)},
                     body=[{'type': 'VAR', 'name': '${x}', 'value': ('a',)},
                           {'name': 'K1', 'args': ('${x}',)},
                           {'type': 'IF/ELSE ROOT',
                            'body': [{'type': 'IF', 'condition': '$c',
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
                     teardown={'name': 'Teardown', 'args': ('a',)},
                     tests=[{'name': 'T1', 'body': [{'name': 'K'}]}],
                     suites=[{'name': 'Child',
                              'tests': [{'name': 'T2', 'body': []}],
                              'resource': {}}],
                     resource={})

    def test_user_keyword(self):
        self._verify(UserKeyword(), name='', body=[])
        self._verify(UserKeyword('N', ('${a}',), 'd', ('t',), 't', 1, error='E'),
                     name='N',
                     args=('${a}',),
                     doc='d',
                     tags=('t',),
                     timeout='t',
                     lineno=1,
                     error='E',
                     body=[])

    def test_user_keyword_args(self):
        for spec in [('${a}', '${b}'),
                     ('${a}', '@{b}'),
                     ('@{a}', '&{b}'),
                     ('${a}', '@{b}', '${c}'),
                     ('${a}', '@{}', '${c}'),
                     ('${a}=d', '@{b}', '${c}=e')]:
            self._verify(UserKeyword(args=spec), name='', args=spec, body=[])

    def test_user_keyword_structure(self):
        uk = UserKeyword('UK')
        uk.setup.config(name='Setup', args=('New', 'in', 'RF 7'))
        uk.body.create_keyword('K1')
        uk.body.create_if().body.create_branch(condition='$c').body.create_keyword('K2')
        uk.teardown.config(name='Teardown')
        self._verify(uk, name='UK',
                     setup={'name': 'Setup', 'args': ('New', 'in', 'RF 7')},
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
        suite = TestSuite.from_file_system(MISCDIR)
        self._verify(suite, **suite.to_dict())

    def _verify(self, obj, **expected):
        data = obj.to_dict()
        self.assertListEqual(list(data), list(expected))
        self.assertDictEqual(data, expected)
        roundtrip = type(obj).from_dict(data).to_dict()
        self.assertDictEqual(roundtrip, expected)
        roundtrip = type(obj).from_json(obj.to_json()).to_dict()
        self.assertDictEqual(roundtrip, expected)
        self._validate(obj)

    def _validate(self, obj):
        suite = self._create_suite_structure(obj)
        self.validator.validate(instance=json.loads(suite.to_json()))
        # Validating `suite.to_dict` directly doesn't work due to tuples not
        # being accepted as arrays:
        # https://github.com/python-jsonschema/jsonschema/issues/148
        #self.validator.validate(instance=suite.to_dict())

    def _create_suite_structure(self, obj):
        suite = TestSuite()
        test = suite.tests.create()
        if isinstance(obj, TestSuite):
            suite = obj
        elif isinstance(obj, TestCase):
            suite.tests = [obj]
        elif isinstance(obj, (Keyword, For, While, If, Try, Var, Error)):
            test.body.append(obj)
        elif isinstance(obj, (IfBranch, TryBranch)):
            item = If() if isinstance(obj, IfBranch) else Try()
            item.body.append(obj)
            test.body.append(item)
        elif isinstance(obj, (Break, Continue, Return)):
            branch = test.body.create_if().body.create_branch()
            branch.body.append(obj)
        elif isinstance(obj, UserKeyword):
            suite.resource.keywords.append(obj)
        elif isinstance(obj, ResourceFile):
            suite.resource = obj
        else:
            raise ValueError(obj)
        return suite


class TestResourceFile(unittest.TestCase):
    path = CURDIR.parent / 'resources/test.resource'
    data = '''
*** Settings ***
Library         Example
Keyword Tags    common

*** Variables ***
${NAME}         Value

*** Keywords ***
Example
    [Tags]    own
    Log    Hello!
'''

    def test_from_file_system(self):
        res = ResourceFile.from_file_system(self.path)
        assert_equal(res.variables[0].name, '${PATH}')
        assert_equal(res.variables[0].value, (str(self.path.parent).replace('\\', '\\\\'),))
        assert_equal(res.keywords[0].name, 'My Test Keyword')

    def test_from_file_system_with_config(self):
        res = ResourceFile.from_file_system(self.path, process_curdir=False)
        assert_equal(res.variables[0].name, '${PATH}')
        assert_equal(res.variables[0].value, ('${CURDIR}',))
        assert_equal(res.keywords[0].name, 'My Test Keyword')

    def test_from_string(self):
        res = ResourceFile.from_string(self.data)
        assert_equal(res.imports[0].name, 'Example')
        assert_equal(res.variables[0].name, '${NAME}')
        assert_equal(res.variables[0].value, ('Value',))
        assert_equal(res.keywords[0].name, 'Example')
        assert_equal(res.keywords[0].tags, ['common', 'own'])
        assert_equal(res.keywords[0].body[0].name, 'Log')
        assert_equal(res.keywords[0].body[0].args, ('Hello!',))

    def test_from_string_with_config(self):
        res = ResourceFile.from_string('*** Muuttujat ***\n${NIMI}\tarvo', lang='fi')
        assert_equal(res.variables[0].name, '${NIMI}')
        assert_equal(res.variables[0].value, ('arvo',))

    def test_from_model(self):
        model = get_resource_model(self.data)
        res = ResourceFile.from_model(model)
        assert_equal(res.imports[0].name, 'Example')
        assert_equal(res.variables[0].name, '${NAME}')
        assert_equal(res.variables[0].value, ('Value',))
        assert_equal(res.keywords[0].name, 'Example')
        assert_equal(res.keywords[0].tags, ['common', 'own'])
        assert_equal(res.keywords[0].body[0].name, 'Log')
        assert_equal(res.keywords[0].body[0].args, ('Hello!',))


class TestStringRepresentation(unittest.TestCase):

    def test_user_keyword_repr(self):
        assert_equal(repr(UserKeyword(name='x')),
                     "robot.running.UserKeyword(name='x')")
        assert_equal(repr(UserKeyword(name='å', args=['${a}'], doc='Not included')),
                     "robot.running.UserKeyword(name='å', args=['${a}'])")


if __name__ == '__main__':
    unittest.main()
