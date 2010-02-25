import unittest
from types import *

from robot.parsing.userkeyword import UserHandler, UserHandlerList, UserErrorHandler
from robot.errors import *
from robot.utils.asserts import *


class LibraryMock:
    def __init__(self, name='MyLibrary'):
        self.name = name

class KwDataMock:
    def __init__(self, name='My Keyword', metadata=None):
        self.name = name
        self.metadata = metadata
        self.keywords = []

    def report_invalid_syntax(self, msg):
        self.error = msg

class MetaMock:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class TestUserHandlerList(unittest.TestCase):

    def test_invalid_argument_contains_unicode(self):
        mock = KwDataMock(metadata=[MetaMock('arguments', [u'\xe4'])])
        handler = UserHandlerList([mock])[0]
        assert_true(isinstance(handler, UserErrorHandler))
        assert_equals(handler._error, u"Invalid argument '\xe4'")


class TestUserHandler(unittest.TestCase):

    def test_name(self):
        for kw_name, exp_name in [ ('keyword', 'Keyword'),
                                   ('kw_name', 'Kw_name'),
                                   ('MyKWName', 'MyKWName') ]:
            handler = UserHandler(KwDataMock(kw_name))
            assert_equals(handler.name, exp_name)


class TestGetArgSpec(unittest.TestCase):

    def setUp(self):
        self.handler = UserHandler(KwDataMock())

    def test_no_args(self):
        self._verify('', (), (), None)

    def test_one_arg(self):
        self._verify('${arg1}', ('${arg1}',), (), None)

    def test_one_vararg(self):
        self._verify('@{varargs}', (), (), '@{varargs}')

    def test_one_default(self):
        self._verify('${arg1} ${arg2}=default @{varargs}',
                     ('${arg1}', '${arg2}'), ('default',), '@{varargs}')

    def test_one_empty_default(self):
        self._verify('${arg1} ${arg2}= @{varargs}',
                     ('${arg1}', '${arg2}'), ('',), '@{varargs}')

    def test_many_defaults(self):
        self._verify('${arg1}=default1 ${arg2}=default2 ${arg3}=default3',
                     ('${arg1}', '${arg2}', '${arg3}'),
                     ('default1', 'default2', 'default3'), None)

    def _verify(self, in_args, exp_args, exp_defaults, exp_varargs):
        args, defaults, varargs = self.handler._get_arg_spec(in_args.split())
        assert_equals(args, exp_args)
        assert_equals(defaults, exp_defaults)
        assert_equals(varargs, exp_varargs)

    def test_many_varargs_raises(self):
        in_args = ['@{varargs}', '@{varargs2}']
        assert_raises(DataError, self.handler._get_arg_spec, in_args)

    def test_args_after_varargs_raises(self):
        in_args = ['@{varargs}', '${arg1}']
        assert_raises(DataError, self.handler._get_arg_spec, in_args)

    def test_get_defaults_before_args_raises(self):
        in_args = ['${args1}=default', '${arg2}']
        assert_raises(DataError, self.handler._get_arg_spec, in_args)


if __name__ == '__main__':
    unittest.main()
