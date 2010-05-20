import unittest

from robot.errors import DataError, ExecutionFailed
from robot.running.timeouts import KeywordTimeout
from robot.running.keywords import Keyword
from robot.utils.asserts import *
from test_testlibrary import _FakeNamespace


class OutputStub:

    def __getattr__(self, name):
        if name == 'syslog':
            return self
        return lambda *args: None


class MockHandler:

    def __init__(self, name='Mock Handler', doc='Mock Doc', error=False):
        self.name = self.longname = name
        self.doc = self.shortdoc = doc
        self.error = error
        self.timeout = KeywordTimeout()

    def init_keyword(self, varz):
        pass

    def run(self, context, args):
        """Sets given args to self.ags and optionally returns something.

        Returning works so that if two args are given and the first one is
        string 'return' (case insensitive) the second argument is returned.
        """
        if self.error:
            raise DataError
        self.args = args
        if len(args) == 2 and args[0].lower() == 'return':
            return args[1]


class _FakeSuite(object):
    def __init__(self):
        self.status = 'RUNNING'


class FakeNamespace(_FakeNamespace):
    def __init__(self):
        _FakeNamespace.__init__(self)
        self.suite = _FakeSuite()


class _FakeContext(object):
    def __init__(self, error=False):
        self.namespace = FakeNamespace()
        self.output = OutputStub()
        self.error = error
        self.variables = self.namespace.variables
        self.dry_run = False

    def get_handler(self, kwname):
        return MockHandler('Mocked.'+kwname, error=self.error)

    def get_current_vars(self):
        return self.namespace.variables

    def start_keyword(self, kw): pass
    def end_keyword(self, kw): pass
    def trace(self, msg): pass


class TestKeyword(unittest.TestCase):

    def test_run(self):
        for args in [ [], ['arg',], ['a1','a2'] ]:
            self._verify_run(args)

    def test_run_with_variables(self):
        for args in [ ['${str}',], ['a1','--${str}--'], ['@{list}',],
                           ['@{list}','${str}-${str}','@{list}','v3'] ]:
            self._verify_run(args)

    def test_run_with_escape(self):
        for args in [ ['\\ arg \\',], ['\\${str}',], ['\\\\${str}',], ]:
            self._verify_run(args)

    def test_run_error(self):
        kw = Keyword('handler_name', ())
        assert_raises(ExecutionFailed, kw.run, _FakeContext(error=True))

    def _verify_run(self, args):
        kw = Keyword('handler_name', args)
        assert_equals(kw.name, 'handler_name')
        assert_equals(kw.args, args)
        kw.run(_FakeContext())
        assert_equals(kw.name, 'Mocked.handler_name')
        assert_equals(kw.doc, 'Mock Doc')
        assert_equals(kw.handler_name, 'handler_name')


class TestResolveAssignment(unittest.TestCase):

    def test_one_scalar(self):
        self._verify(['${var}'])

    def test_multiple_scalars(self):
        self._verify('${v1} ${v2} ${v3}'.split())

    def test_list(self):
        self._verify(['@{list}'])

    def test_scalars_and_list(self):
        self._verify('${v1} ${v2} @{list}'.split())

    def test_init_list_in_wrong_place_raises(self):
        assert_raises(DataError, Keyword, 'Name', ['arg'], ['@{list}','${str}'])

    def _verify(self, assign):
        kw = Keyword('Name', ['arg'], assign)
        if assign[-1][0] == '$':
            exp_list = None
        else:
            exp_list = assign.pop()
        assert_equal(kw.name, 'Name')
        assert_equal(kw.args, ['arg'])
        assert_equal(kw.assign.keyword, 'Name')
        assert_equal(kw.assign.scalar_vars, assign)
        assert_equal(kw.assign.list_var, exp_list)


class TestX(unittest.TestCase):

    def test_set_string_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN','value']))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${var}'], 'value')

    def test_set_object_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN',self]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${var}'], self)

    def test_set_empty_list_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN',[]]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${var}'], [])

    def test_set_list_with_one_element_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN',['hi']]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${var}'], ['hi'])

    def test_set_strings_to_three_scalars(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','${v3}','KW','RETURN',['x','y','z']]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${v1}'], 'x')
        assert_equal(context.variables['${v2}'], 'y')
        assert_equal(context.variables['${v3}'], 'z')

    def test_set_objects_to_three_scalars(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','${v3}','KW','RETURN',[['x','y'],{},None]]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${v1}'], ['x','y'])
        assert_equal(context.variables['${v2}'], {})
        assert_equal(context.variables['${v3}'], None)

    def test_set_list_of_strings_to_list(self):
        skw = SetKeyword(SetKeywordData(['@{var}','KW','RETURN',['x','y','z']]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['@{var}'], ['x','y','z'])

    def test_set_empty_list_to_list(self):
        skw = SetKeyword(SetKeywordData(['@{var}','KW','RETURN',[]]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['@{var}'], [])

    def test_set_objects_to_two_scalars_and_list(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','@{v3}','KW','RETURN',['a',None,'x','y',{}]]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${v1}'], 'a')
        assert_equal(context.variables['${v2}'], None)
        assert_equal(context.variables['@{v3}'], ['x','y',{}])

    def test_set_scalars_and_list_so_that_list_is_empty(self):
        skw = SetKeyword(SetKeywordData(['${scal}','@{list}','KW','RETURN',['a']]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${scal}'], 'a')
        assert_equal(context.variables['@{list}'], [])

    def test_set_more_values_than_variables(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','KW','RETURN',['x','y','z']]))
        context = _FakeContext()
        skw.run(context)
        assert_equal(context.variables['${v1}'], 'x')
        assert_equal(context.variables['${v2}'], ['y','z'])

    def test_set_too_few_scalars_raises(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','KW','RETURN',['x']]))
        assert_raises(ExecutionFailed, skw.run, _FakeContext())

    def test_set_list_but_no_list_raises(self):
        skw = SetKeyword(SetKeywordData(['@{list}','KW','RETURN','not a list']))
        assert_raises(ExecutionFailed, skw.run, _FakeContext())

    def test_set_too_few_scalars_with_list_raises(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','@{list}','KW','RETURN',['x']]))
        assert_raises(ExecutionFailed, skw.run, _FakeContext())


if __name__ == '__main__':
    unittest.main()
