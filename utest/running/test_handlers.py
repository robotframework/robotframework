import unittest
import sys
from types import * 

from robot.running.handlers import _RunnableHandler, _PythonHandler, \
        _JavaHandler, DynamicHandler
from robot import utils
from robot.errors import *
from robot.utils.asserts import *
from robot.running.testlibraries import TestLibrary

from classes import NameLibrary, DocLibrary, ArgInfoLibrary
from ArgumentsPython import ArgumentsPython
if utils.is_jython:
    import ArgumentsJava


def _get_handler_methods(lib):
    attrs = [ getattr(lib, a) for a in dir(lib) if not a.startswith('_') ]
    return [ a for a in attrs if type(a) is MethodType ]

def _get_java_handler_methods(lib):
    # This hack assumes that all java handlers used start with 'a_' -- easier
    # than excluding 'equals' etc. otherwise
    return [ a for a in _get_handler_methods(lib) if a.__name__.startswith('a_') ]
    

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

    def test_get_arg_info(self):
        for method in _get_handler_methods(ArgInfoLibrary()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            expected = eval(method.__doc__)
            assert_equals(handler.arguments._get_arg_spec(method),
                          expected, method.__name__)

    def test_arg_limits(self):
        for method in _get_handler_methods(ArgumentsPython()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            exp_mina, exp_maxa = eval(method.__doc__)
            assert_equals(handler.arguments._arg_limit_checker.minargs, exp_mina)
            assert_equals(handler.arguments._arg_limit_checker.maxargs, exp_maxa)

    def test_getarginfo_getattr(self):
        testlib = TestLibrary('classes.GetattrLibrary')
        handlers = testlib.handlers.values()
        assert_equals(len(handlers), 3)
        for handler in handlers:
            assert_true(handler.name in ['Foo','Bar','Zap'])
            assert_equals(handler.arguments._arg_limit_checker.minargs, 0)
            assert_equals(handler.arguments._arg_limit_checker.maxargs, sys.maxint)


class TestDynamicHandlerCreation(unittest.TestCase):
    _type_err_msg = 'Argument spec should be a list/array of strings'

    def test_with_none_doc(self):
        assert_equals(self._create_handler().doc, '')

    def test_with_empty_doc(self):
         assert_equals(self._create_handler('').doc, '')

    def test_with_non_empty_doc(self):
        doc = 'This is some documentation'
        assert_equals(self._create_handler(doc).doc, doc)

    def test_with_non_string_doc(self):
        doc = ['this', 'is', 'doc']
        assert_equals(self._create_handler(doc).doc, str(doc))
        doc = lambda x: None
        assert_equals(self._create_handler(doc).doc, str(doc))

    def test_with_none_argspec(self):
        self._assert_arg_specs(self._create_handler(), 0, sys.maxint, 
                               vararg='<unknown>')

    def test_with_empty_argspec(self):
        self._assert_arg_specs(self._create_handler(argspec=[]), 0, 0)

    def test_with_mandatory_args(self):
        for args in [ ['arg'], ['arg1', 'arg2', 'arg3'] ]:
            handler = self._create_handler(argspec=args) 
            self._assert_arg_specs(handler, len(args), len(args), args)

    def test_with_only_default_args(self):
        argspec = ['defarg1=value', 'defarg2=defvalue']
        self._assert_arg_specs(self._create_handler(argspec=argspec), 0, 2, 
                               ['defarg1', 'defarg2'], ['value', 'defvalue'])

    def test_default_value_may_contain_equal_sign(self):
        self._assert_arg_specs(self._create_handler(argspec=['d=foo=bar']), 0, 1,
                                                    ['d'], ['foo=bar'])

    def test_with_varargs(self):
        self._assert_arg_specs(self._create_handler(argspec=['*vararg']), 0, 
                                                    sys.maxint, vararg='vararg')

    def test_integration(self):
        handler = self._create_handler(argspec=['arg', 'default=value'])
        self._assert_arg_specs(handler, 1, 2, ['arg', 'default'], ['value'])
        handler = self._create_handler(argspec=['arg', 'default=value', '*var'])
        self._assert_arg_specs(handler, 1, sys.maxint, ['arg', 'default'], ['value'], 'var')

    def test_with_string_argspec(self):
        assert_raises_with_msg(TypeError, self._type_err_msg, self._create_handler, argspec='')

    def test_with_non_iterable_argspec(self):
        assert_raises_with_msg(TypeError, self._type_err_msg, self._create_handler, argspec=True)

    def test_mandatory_arg_after_default_arg(self):
        for argspec in [['d=v', 'arg'], ['a', 'b', 'c=v', 'd']]:
            assert_raises_with_msg(TypeError, self._type_err_msg, 
                                   self._create_handler, argspec=argspec)

    def test_vararg_not_last(self):
        for argspec in [ ['*foo', 'arg'], ['arg', '*var', 'arg'], 
                         ['a', 'b=d', '*var', 'c'], ['*var', '*vararg'] ]:
            assert_raises_with_msg(TypeError, self._type_err_msg,
                                   self._create_handler, argspec=argspec)

    def _create_handler(self, doc=None, argspec=None):
        return DynamicHandler(LibraryMock('TEST CASE'), 'mock', lambda x: None,
                              doc, argspec)

    def _assert_arg_specs(self, handler, minargs, maxargs, names=[], defaults=[], vararg=None):
        assert_equals(handler.arguments._arg_limit_checker.minargs, minargs)
        assert_equals(handler.arguments._arg_limit_checker.maxargs, maxargs)
        assert_equals(handler.arguments.names, names)
        assert_equals(handler.arguments.defaults, defaults)
        assert_equals(handler.arguments.varargs, vararg)


if utils.is_jython:
    
    handlers = dict([ (method.__name__, method) for method in 
                       _get_java_handler_methods(ArgumentsJava()) ])

    class TestJavaHandler(unittest.TestCase):

        def test_arg_limits_no_defaults_or_varargs(self):
            for count in [ 0, 1, 3 ]:
                method = handlers['a_%d' % count]
                handler = _JavaHandler(LibraryMock(), method.__name__, method)
                assert_equals(handler.arguments._arg_limit_checker.minargs, count)
                assert_equals(handler.arguments._arg_limit_checker.maxargs, count)

        def test_arg_limits_with_varargs(self):
            for count in [ 0, 1 ]:
                method = handlers['a_%d_n' % count]
                handler = _JavaHandler(LibraryMock(), method.__name__, method)
                assert_equals(handler.arguments._arg_limit_checker.minargs, count)
                assert_equals(handler.arguments._arg_limit_checker.maxargs, sys.maxint)

        def test_arg_limits_with_defaults(self):
            # defaults i.e. multiple signatures
            for mina, maxa in [ (0,1), (1,3) ]:
                method = handlers['a_%d_%d' % (mina, maxa)]
                handler = _JavaHandler(LibraryMock(), method.__name__, method)
                assert_equals(handler.arguments._arg_limit_checker.minargs, mina)
                assert_equals(handler.arguments._arg_limit_checker.maxargs, maxa)


    class TestArgumentCoercer(unittest.TestCase):

        def setUp(self):
            self.lib = TestLibrary('ArgTypeCoercion')

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
            assert_equals(handler.arguments.arg_coercer(args), expected)

        def _test_coercion_fails(self, handler, expected_message):
            assert_raises_with_msg(DataError, expected_message,
                                   handler.arguments.arg_coercer, ['invalid'])


if __name__ == '__main__':
    unittest.main()
