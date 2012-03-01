import unittest

from robot.errors import DataError, ExecutionFailed
from robot.running.timeouts import KeywordTimeout
from robot.running.keywords import Keyword
from robot.utils.asserts import assert_equals, assert_raises
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
        self.teardown = False
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


class TestSettingVariables(unittest.TestCase):

    def test_set_string_to_scalar(self):
        self._verify_scalar('value')

    def test_set_object_to_scalar(self):
        self._verify_scalar(self)

    def test_set_empty_list_to_scalar(self):
        self._verify_scalar([])

    def test_set_list_with_one_element_to_scalar(self):
        self._verify_scalar(['hi'])

    def test_set_strings_to_multiple_scalars(self):
        self._verify_three_scalars('x', 'y', 'z')

    def test_set_objects_to_multiple_scalars(self):
        self._verify_three_scalars(['x', 'y'], {}, None)

    def test_set_list_of_strings_to_list(self):
        self._verify_list(['x','y','z'])

    def test_set_empty_list_to_list(self):
        self._verify_list([])

    def test_set_objects_to_list(self):
        self._verify_list([{True: False}, None, self])

    def test_set_objects_to_two_scalars_and_list(self):
        variables = self._run_kw(['${v1}','${v2}','@{v3}'], ['a',None,'x','y',{}])
        assert_equals(variables['${v1}'], 'a')
        assert_equals(variables['${v2}'], None)
        assert_equals(variables['@{v3}'], ['x','y',{}])

    def test_set_scalars_and_list_so_that_list_is_empty(self):
        variables = self._run_kw(['${scal}','@{list}'], ['a'])
        assert_equals(variables['${scal}'], 'a')
        assert_equals(variables['@{list}'], [])

    def test_set_more_values_than_variables(self):
        variables = self._run_kw(['${v1}','${v2}'], ['x','y','z'])
        assert_equals(variables['${v1}'], 'x')
        assert_equals(variables['${v2}'], ['y','z'])

    def test_set_too_few_scalars_raises(self):
        assert_raises(ExecutionFailed, self._run_kw, ['${v1}','${v2}'], ['x'])

    def test_set_list_but_no_list_raises(self):
        assert_raises(ExecutionFailed, self._run_kw, ['@{list}'], 'not a list')

    def test_set_too_few_scalars_with_list_raises(self):
        assert_raises(ExecutionFailed, self._run_kw, ['${v1}','${v2}','@{list}'], ['x'])

    def _verify_scalar(self, return_value):
        variables = self._run_kw(['${var}'], return_value)
        assert_equals(variables['${var}'], return_value)

    def _verify_list(self, return_value):
        variables = self._run_kw(['@{var}'], return_value)
        assert_equals(variables['@{var}'], return_value)

    def _verify_three_scalars(self, ret1, ret2, ret3):
        variables = self._run_kw(['${v1}','${v2}','${v3}'], [ret1, ret2, ret3])
        assert_equals(variables['${v1}'], ret1)
        assert_equals(variables['${v2}'], ret2)
        assert_equals(variables['${v3}'], ret3)

    def _run_kw(self, assign, return_value):
        kw = Keyword('Name', ['Return', return_value], assign)
        context = _FakeContext()
        kw.run(context)
        return context.variables


if __name__ == '__main__':
    unittest.main()
