import unittest
import sys
import inspect

from robot.running.handlers import _PythonHandler, _JavaHandler, DynamicHandler
from robot import utils
from robot.utils.asserts import *
from robot.running.testlibraries import TestLibrary
from robot.running.dynamicmethods import GetKeywordArguments, GetKeywordDocumentation
from robot.errors import DataError

from classes import NameLibrary, DocLibrary, ArgInfoLibrary
from ArgumentsPython import ArgumentsPython
if utils.is_jython:
    import ArgumentsJava


def _get_handler_methods(lib):
    attrs = [getattr(lib, a) for a in dir(lib) if not a.startswith('_')]
    return [a for a in attrs if inspect.ismethod(a)]

def _get_java_handler_methods(lib):
    # This hack assumes that all java handlers used start with 'a_' -- easier
    # than excluding 'equals' etc. otherwise
    return [a for a in _get_handler_methods(lib) if a.__name__.startswith('a_') ]


class LibraryMock:
    def __init__(self, name='MyLibrary', scope='GLOBAL'):
        self.name = self.orig_name = name
        self.scope = scope


class TestPythonHandler(unittest.TestCase):

    def test_name(self):
        for method in _get_handler_methods(NameLibrary()):
            handler = _PythonHandler(LibraryMock('mylib'), method.__name__, method)
            assert_equals(handler.name, method.__doc__)
            assert_equals(handler.longname, 'mylib.'+method.__doc__)

    def test_docs(self):
        for method in _get_handler_methods(DocLibrary()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            assert_equals(handler.doc, method.expected_doc)
            assert_equals(handler.shortdoc, method.expected_shortdoc)

    def test_arguments(self):
        for method in _get_handler_methods(ArgInfoLibrary()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            args = handler.arguments
            argspec = (args.positional, args.defaults, args.varargs, args.kwargs)
            expected = eval(method.__doc__)
            assert_equals(argspec, expected, method.__name__)

    def test_arg_limits(self):
        for method in _get_handler_methods(ArgumentsPython()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            exp_mina, exp_maxa = eval(method.__doc__)
            assert_equals(handler.arguments.minargs, exp_mina)
            assert_equals(handler.arguments.maxargs, exp_maxa)

    def test_getarginfo_getattr(self):
        testlib = TestLibrary('classes.GetattrLibrary')
        handlers = testlib.handlers.values()
        assert_equals(len(handlers), 3)
        for handler in handlers:
            assert_true(handler.name in ['Foo','Bar','Zap'])
            assert_equals(handler.arguments.minargs, 0)
            assert_equals(handler.arguments.maxargs, sys.maxint)


class TestDynamicHandlerCreation(unittest.TestCase):

    def test_none_doc(self):
        self._assert_doc(None, '')

    def test_empty_doc(self):
        self._assert_doc('')

    def test_non_empty_doc(self):
        self._assert_doc('This is some documentation')

    def test_non_ascii_doc(self):
        self._assert_doc(u'P\xe4iv\xe4\xe4')

    def test_with_utf8_doc(self):
        doc = u'P\xe4iv\xe4\xe4'
        self._assert_doc(doc.encode('UTF-8'), doc)

    def test_invalid_doc_type(self):
        self._assert_fails('Return value must be string.', doc=True)

    def test_none_argspec(self):
        self._assert_spec(None, maxargs=sys.maxint,vararg='unknown')

    def test_empty_argspec(self):
        self._assert_spec([])

    def test_mandatory_args(self):
        for argspec in [['arg'], ['arg1', 'arg2', 'arg3']]:
            self._assert_spec(argspec, len(argspec), len(argspec), argspec)

    def test_only_default_args(self):
        self._assert_spec(['defarg1=value', 'defarg2=defvalue'], 0, 2,
                          ['defarg1', 'defarg2'], ['value', 'defvalue'])

    def test_default_value_may_contain_equal_sign(self):
        self._assert_spec(['d=foo=bar'], 0, 1, ['d'], ['foo=bar'])

    def test_varargs(self):
        self._assert_spec(['*vararg'], 0, sys.maxint, vararg='vararg')

    def test_integration(self):
        self._assert_spec(['arg', 'default=value'], 1, 2,
                          ['arg', 'default'], ['value'])
        self._assert_spec(['arg', 'default=value', '*var'], 1, sys.maxint,
                          ['arg', 'default'], ['value'], 'var')

    def test_invalid_argspec_type(self):
        for argspec in [True, [1, 2]]:
            self._assert_fails("Return value must be list of strings.", argspec)

    def test_mandatory_arg_after_default_arg(self):
        for argspec in [['d=v', 'arg'], ['a', 'b', 'c=v', 'd']]:
            self._assert_fails('Non-default argument after default arguments.',
                               argspec)

    def test_vararg_not_last(self):
        for argspec in [['*foo', 'arg'], ['arg', '*var', 'arg'],
                        ['a', 'b=d', '*var', 'c'], ['*var', '*vararg']]:
            self._assert_fails('Only last argument can be varargs.', argspec)

    def _assert_doc(self, doc, expected=None):
        expected = doc if expected is None else expected
        assert_equals(self._create_handler(doc=doc).doc, expected)

    def _assert_spec(self, argspec, minargs=0, maxargs=0, positional=[],
                     defaults=[], vararg=None):
        arguments = self._create_handler(argspec).arguments
        assert_equals(arguments.minargs, minargs)
        assert_equals(arguments.maxargs, maxargs)
        assert_equals(arguments.positional, positional)
        assert_equals(arguments.defaults, defaults)
        assert_equals(arguments.varargs, vararg)

    def _assert_fails(self, error, argspec=None, doc=None):
        assert_raises_with_msg(DataError, error,
                               self._create_handler, argspec, doc)
    def _create_handler(self, argspec=None, doc=None):
        doc = GetKeywordDocumentation(lib=None)._handle_return_value(doc)
        argspec = GetKeywordArguments(lib=None)._handle_return_value(argspec)
        return DynamicHandler(LibraryMock('TEST CASE'), 'mock', lambda x: None,
                              doc, argspec)


if utils.is_jython:

    handlers = dict((method.__name__, method) for method in
                    _get_java_handler_methods(ArgumentsJava('Arg', ['varargs'])))

    class TestJavaHandler(unittest.TestCase):

        def test_arg_limits_no_defaults_or_varargs(self):
            for count in [0, 1, 3]:
                method = handlers['a_%d' % count]
                handler = _JavaHandler(LibraryMock(), method.__name__, method)
                assert_equals(handler.arguments.minargs, count)
                assert_equals(handler.arguments.maxargs, count)

        def test_arg_limits_with_varargs(self):
            for count in [0, 1]:
                method = handlers['a_%d_n' % count]
                handler = _JavaHandler(LibraryMock(), method.__name__, method)
                assert_equals(handler.arguments.minargs, count)
                assert_equals(handler.arguments.maxargs, sys.maxint)

        def test_arg_limits_with_defaults(self):
            # defaults i.e. multiple signatures
            for mina, maxa in [(0,1), (1,3)]:
                method = handlers['a_%d_%d' % (mina, maxa)]
                handler = _JavaHandler(LibraryMock(), method.__name__, method)
                assert_equals(handler.arguments.minargs, mina)
                assert_equals(handler.arguments.maxargs, maxa)


    class TestArgumentCoercer(unittest.TestCase):

        def setUp(self):
            self.lib = TestLibrary('ArgTypeCoercion', ['42', 'true'])

        def test_coercion_in_constructor(self):
            instance = self.lib.get_instance()
            assert_equals(instance.myInt, 42)
            assert_equals(instance.myBool, True)

        def test_coercing_to_integer(self):
            self._test_coercion(self._handler_named('intArgument'),
                                ['1'], [1])

        def test_coercing_to_boolean(self):
            handler = self._handler_named('booleanArgument')
            self._test_coercion(handler, ['True'], [True])
            self._test_coercion(handler, ['FALSE'], [ False])

        def test_coercing_to_real_number(self):
            self._test_coercion(self._handler_named('doubleArgument'),
                                ['1.42'], [1.42])
            self._test_coercion(self._handler_named('floatArgument'),
                                ['-9991.098'], [-9991.098])

        def test_coercion_with_compatible_types(self):
            self._test_coercion(self._handler_named('coercableKeywordWithCompatibleTypes'),
                                ['9999', '-42', 'FaLsE', '31.31'],
                                [9999, -42, False, 31.31])

        def test_arguments_that_are_not_strings_are_not_coerced(self):
            self._test_coercion(self._handler_named('intArgument'),
                                [self.lib], [self.lib])
            self._test_coercion(self._handler_named('booleanArgument'),
                                [42], [42])

        def test_coercion_fails_with_reasonable_message(self):
            exp_msg = 'Argument at position 1 cannot be coerced to %s'
            self._test_coercion_fails(self._handler_named('intArgument'),
                                      exp_msg % 'integer')
            self._test_coercion_fails(self._handler_named('booleanArgument'),
                                      exp_msg % 'boolean')
            self._test_coercion_fails(self._handler_named('floatArgument'),
                                      exp_msg % 'floating point number')

        def test_no_arg_no_coercion(self):
            self._test_coercion(self._handler_named('noArgument'), [], [])

        def test_coercing_multiple_arguments(self):
            self._test_coercion(self._handler_named('coercableKeyword'),
                                ['10.0', '42', 'tRUe'], [10.0, 42, True])

        def test_coercion_is_not_done_with_conflicting_signatures(self):
            self._test_coercion(self._handler_named('unCoercableKeyword'),
                                ['True', '42'], ['True', '42'])

        def test_coercable_and_uncoercable_args_in_same_kw(self):
            self._test_coercion(self._handler_named('coercableAndUnCoercableArgs'),
                                ['1', 'False', '-23', '0'], ['1', False, -23, '0'])

        def _handler_named(self, name):
            return self.lib.handlers[name]

        def _test_coercion(self, handler, args, expected):
            assert_equals(handler._arg_coercer.coerce(args), expected)

        def _test_coercion_fails(self, handler, expected_message):
            assert_raises_with_msg(ValueError, expected_message,
                                   handler._arg_coercer.coerce, ['invalid'])


if __name__ == '__main__':
    unittest.main()
