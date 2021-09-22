import inspect
import os.path
import re
import sys
import unittest

from robot.running.handlers import _PythonHandler, _JavaHandler, DynamicHandler
from robot.utils.asserts import assert_equal, assert_raises_with_msg, assert_true
from robot.running.testlibraries import TestLibrary, LibraryScope
from robot.running.dynamicmethods import (
    GetKeywordArguments, GetKeywordDocumentation, RunKeyword)
from robot.errors import DataError

from classes import (NameLibrary, DocLibrary, ArgInfoLibrary,
                     __file__ as classes_source)
from ArgumentsPython import ArgumentsPython


def _get_handler_methods(lib):
    attrs = [getattr(lib, a) for a in dir(lib) if not a.startswith('_')]
    return [a for a in attrs if inspect.ismethod(a)]

def _get_java_handler_methods(lib):
    # This hack assumes that all java handlers used start with 'a_' or 'java'
    # -- easier than excluding 'equals' etc. otherwise
    return [a for a in _get_handler_methods(lib)
            if a.__name__.startswith(('a_', 'java'))]


class LibraryMock(object):

    def __init__(self, name='MyLibrary', scope='GLOBAL'):
        self.name = self.orig_name = name
        self.scope = LibraryScope(scope, self)

    register_listeners = unregister_listeners = reset_instance \
        = get_instance = lambda *args: None


def assert_argspec(argspec, minargs=0, maxargs=0, positional=[], defaults={},
                   varargs=None, kwonlyargs=[], kwargs=None):
    assert_equal(argspec.minargs, minargs)
    assert_equal(argspec.maxargs, maxargs)
    assert_equal(argspec.positional, positional)
    assert_equal(argspec.defaults, defaults)
    assert_equal(argspec.var_positional, varargs)
    assert_equal(argspec.named_only, kwonlyargs)
    assert_equal(argspec.var_named, kwargs)


class TestPythonHandler(unittest.TestCase):

    def test_name(self):
        for method in _get_handler_methods(NameLibrary()):
            handler = _PythonHandler(LibraryMock('mylib'), method.__name__, method)
            assert_equal(handler.name, method.__doc__)
            assert_equal(handler.longname, 'mylib.'+method.__doc__)

    def test_docs(self):
        for method in _get_handler_methods(DocLibrary()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            assert_equal(handler.doc, method.expected_doc)
            assert_equal(handler.shortdoc, method.expected_shortdoc)

    def test_arguments(self):
        for method in _get_handler_methods(ArgInfoLibrary()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            args = handler.arguments
            argspec = (args.positional, args.defaults, args.var_positional, args.var_named)
            expected = eval(method.__doc__)
            assert_equal(argspec, expected, method.__name__)

    def test_arg_limits(self):
        for method in _get_handler_methods(ArgumentsPython()):
            handler = _PythonHandler(LibraryMock(), method.__name__, method)
            exp_mina, exp_maxa = eval(method.__doc__)
            assert_equal(handler.arguments.minargs, exp_mina)
            assert_equal(handler.arguments.maxargs, exp_maxa)

    def test_getarginfo_getattr(self):
        handlers = TestLibrary('classes.GetattrLibrary').handlers
        assert_equal(len(handlers), 3)
        for handler in handlers:
            assert_true(handler.name in ['Foo','Bar','Zap'])
            assert_equal(handler.arguments.minargs, 0)
            assert_equal(handler.arguments.maxargs, sys.maxsize)


class TestDynamicHandlerCreation(unittest.TestCase):

    def test_none_doc(self):
        self._assert_doc(None, '')

    def test_empty_doc(self):
        self._assert_doc('')

    def test_non_empty_doc(self):
        self._assert_doc('This is some documentation')

    def test_non_ascii_doc(self):
        self._assert_doc('Hyvää yötä')

    def test_with_utf8_doc(self):
        doc = 'Hyvää yötä'
        self._assert_doc(doc.encode('UTF-8'), doc)

    def test_invalid_doc_type(self):
        self._assert_fails('Return value must be a string, got boolean.', doc=True)

    def test_none_argspec(self):
        self._assert_spec(None, maxargs=sys.maxsize, varargs='varargs', kwargs=False)

    def test_none_argspec_when_kwargs_supported(self):
        self._assert_spec(None, maxargs=sys.maxsize, varargs='varargs', kwargs='kwargs')

    def test_empty_argspec(self):
        self._assert_spec([])

    def test_mandatory_args(self):
        for argspec in [['arg'], ['arg1', 'arg2', 'arg3']]:
            self._assert_spec(argspec, len(argspec), len(argspec), argspec)

    def test_only_default_args(self):
        self._assert_spec(['d1=default', 'd2=True'], 0, 2,
                          ['d1', 'd2'], {'d1': 'default', 'd2': 'True'})

    def test_default_as_tuple_or_list_like(self):
        self._assert_spec([('d1', 'default'), ['d2', True]], 0, 2,
                          ['d1', 'd2'], {'d1': 'default', 'd2': True})

    def test_default_value_may_contain_equal_sign(self):
        self._assert_spec(['d=foo=bar'], 0, 1, ['d'], {'d': 'foo=bar'})

    def test_default_value_as_tuple_may_contain_equal_sign(self):
        self._assert_spec([('n=m', 'd=f')], 0, 1, ['n=m'], {'n=m': 'd=f'})

    def test_varargs(self):
        self._assert_spec(['*vararg'], 0, sys.maxsize, varargs='vararg')

    def test_kwargs(self):
        self._assert_spec(['**kwarg'], 0, 0, kwargs='kwarg')

    def test_varargs_and_kwargs(self):
        self._assert_spec(['*vararg', '**kwarg'],
                          0, sys.maxsize, varargs='vararg', kwargs='kwarg')

    def test_kwonlyargs(self):
        self._assert_spec(['*', 'kwo'], kwonlyargs=['kwo'])
        self._assert_spec(['*vars', 'kwo'], varargs='vars', kwonlyargs=['kwo'])
        self._assert_spec(['*', 'x', 'y', 'z'], kwonlyargs=['x', 'y', 'z'])

    def test_kwonlydefaults(self):
        self._assert_spec(['*', 'kwo=default'],
                          kwonlyargs=['kwo'],
                          defaults={'kwo': 'default'})
        self._assert_spec(['*vars', 'kwo=default'],
                          varargs='vars',
                          kwonlyargs=['kwo'],
                          defaults={'kwo': 'default'})
        self._assert_spec(['*', 'x=1', 'y', 'z=3'],
                          kwonlyargs=['x', 'y', 'z'],
                          defaults={'x': '1', 'z': '3'})

    def test_kwonlydefaults_with_tuple(self):
        self._assert_spec(['*', ('kwo', 'default')],
                          kwonlyargs=['kwo'],
                          defaults={'kwo': 'default'})
        self._assert_spec([('*',), 'x=1', 'y', ('z', 3)],
                          kwonlyargs=['x', 'y', 'z'],
                          defaults={'x': '1', 'z': 3})

    def test_integration(self):
        self._assert_spec(['arg', 'default=value'],
                          1, 2,
                          positional=['arg', 'default'],
                          defaults={'default': 'value'})
        self._assert_spec(['arg', 'default=value', '*var'],
                          1, sys.maxsize,
                          positional=['arg', 'default'],
                          defaults={'default': 'value'},
                          varargs='var')
        self._assert_spec(['arg', 'default=value', '**kw'],
                          1, 2,
                          positional=['arg', 'default'],
                          defaults={'default': 'value'},
                          kwargs='kw')
        self._assert_spec(['arg', 'default=value', '*var', '**kw'],
                          1, sys.maxsize,
                          positional=['arg', 'default'],
                          defaults={'default': 'value'},
                          varargs='var',
                          kwargs='kw')
        self._assert_spec(['a', 'b=1', 'c=2', '*d', 'e', 'f=3', 'g', '**h'],
                          1, sys.maxsize,
                          positional=['a', 'b', 'c'],
                          defaults={'b': '1', 'c': '2', 'f': '3'},
                          varargs='d',
                          kwonlyargs=['e', 'f', 'g'],
                          kwargs='h')
        self._assert_spec([('a',), ('b', '1'), ('c', 2), ('*d',), ('e',), ('f', 3), ('g',), ('**h',)],
                          1, sys.maxsize,
                          positional=['a', 'b', 'c'],
                          defaults={'b': '1', 'c': 2, 'f': 3},
                          varargs='d',
                          kwonlyargs=['e', 'f', 'g'],
                          kwargs='h')

    def test_invalid_argspec_type(self):
        for argspec in [True, [1, 2], ['arg', ()]]:
            self._assert_fails("Return value must be a list of strings "
                               "or non-empty tuples.", argspec)

    def test_invalid_tuple(self):
        for invalid in [('too', 'many', 'values'), ('*too', 'many'),
                        ('**too', 'many'), (1, 2), (1,)]:
            self._assert_fails('Invalid argument specification: '
                               'Invalid argument "%s".' % (invalid,),
                               ['valid', invalid])

    def test_mandatory_arg_after_default_arg(self):
        for argspec in [['d=v', 'arg'], ['a', 'b', 'c=v', 'd']]:
            self._assert_fails('Invalid argument specification: '
                               'Non-default argument after default arguments.',
                               argspec)

    def test_multiple_vararg(self):
        self._assert_fails('Invalid argument specification: '
                           'Cannot have multiple varargs.',
                           ['*first', '*second'])

    def test_vararg_with_kwonly_separator(self):
        self._assert_fails('Invalid argument specification: '
                           'Cannot have multiple varargs.',
                           ['*', '*varargs'])
        self._assert_fails('Invalid argument specification: '
                           'Cannot have multiple varargs.',
                           ['*varargs', '*'])
        self._assert_fails('Invalid argument specification: '
                           'Cannot have multiple varargs.',
                           ['*', '*'])

    def test_kwarg_not_last(self):
        for argspec in [['**foo', 'arg'], ['arg', '**kw', 'arg'],
                        ['a', 'b=d', '**kw', 'c'], ['**kw', '*vararg'],
                        ['**kw', '**kwarg']]:
            self._assert_fails('Invalid argument specification: '
                               'Only last argument can be kwargs.', argspec)

    def test_missing_kwargs_support(self):
        for spec in (['**kwargs'], ['arg', '**kws'], ['a', '*v', '**k']):
            self._assert_fails("Too few 'run_keyword' method parameters "
                               "for **kwargs support.", spec)

    def test_missing_kwonlyargs_support(self):
        for spec in (['*', 'kwo'], ['*vars', 'kwo1', 'kwo2=default']):
            self._assert_fails("Too few 'run_keyword' method parameters "
                               "for keyword-only arguments support.", spec)

    def _assert_doc(self, doc, expected=None):
        expected = doc if expected is None else expected
        assert_equal(self._create_handler(doc=doc).doc, expected)

    def _assert_spec(self, argspec, minargs=0, maxargs=0,
                     positional=[], defaults={}, varargs=None,
                     kwonlyargs=[], kwargs=None):
        if varargs and not maxargs:
            maxargs = sys.maxsize
        if kwargs is None and not kwonlyargs:
            kwargs_support_modes = [True, False]
        elif kwargs is False:
            kwargs_support_modes = [False]
            kwargs = None
        else:
            kwargs_support_modes = [True]
        for kwargs_support in kwargs_support_modes:
            handler = self._create_handler(argspec, kwargs_support=kwargs_support)
            assert_argspec(handler.arguments, minargs, maxargs, positional,
                           defaults, varargs, kwonlyargs, kwargs)

    def _assert_fails(self, error, *args, **kwargs):
        assert_raises_with_msg(DataError, error,
                               self._create_handler, *args, **kwargs)

    def _create_handler(self, argspec=None, doc=None, kwargs_support=False):
        lib = LibraryMock('TEST CASE')
        if kwargs_support:
            lib.run_keyword = lambda name, args, kwargs: None
        else:
            lib.run_keyword = lambda name, args: None
        lib.run_keyword.__name__ = 'run_keyword'
        doc = GetKeywordDocumentation(lib)._handle_return_value(doc)
        argspec = GetKeywordArguments(lib)._handle_return_value(argspec)
        return DynamicHandler(lib, 'mock', RunKeyword(lib), doc, argspec)


class TestSourceAndLineno(unittest.TestCase):

    def test_class_with_init(self):
        lib = TestLibrary('classes.RecordingLibrary')
        self._verify(lib.handlers['kw'], classes_source, 206)
        self._verify(lib.init, classes_source, 202)

    def test_class_without_init(self):
        lib = TestLibrary('classes.NameLibrary')
        self._verify(lib.handlers['simple1'], classes_source, 13)
        self._verify(lib.init, classes_source, -1)

    def test_module(self):
        from module_library import __file__ as source
        lib = TestLibrary('module_library')
        self._verify(lib.handlers['passing'], source, 5)
        self._verify(lib.init, source, -1)

    def test_package(self):
        from robot.variables.search import __file__ as source
        from robot.variables import __file__ as init_source
        lib = TestLibrary('robot.variables')
        self._verify(lib.handlers['is_variable'], source, 33)
        self._verify(lib.init, init_source, -1)

    def test_decorated(self):
        lib = TestLibrary('classes.Decorated')
        self._verify(lib.handlers['no_wrapper'], classes_source, 320)
        self._verify(lib.handlers['wrapper'], classes_source, 327)
        self._verify(lib.handlers['external'], classes_source, 332)
        self._verify(lib.handlers['no_def'], classes_source, 335)

    def test_dynamic_without_source(self):
        lib = TestLibrary('classes.ArgDocDynamicLibrary')
        self._verify(lib.handlers['No Arg'], classes_source, -1)

    def test_dynamic(self):
        lib = TestLibrary('classes.DynamicWithSource')
        self._verify(lib.handlers['only path'],
                     classes_source)
        self._verify(lib.handlers['path & lineno'],
                     classes_source, 42)
        self._verify(lib.handlers['lineno only'],
                     classes_source, 6475)
        self._verify(lib.handlers['invalid path'],
                     'path validity is not validated')
        self._verify(lib.handlers['path w/ colon'],
                     r'c:\temp\lib.py', -1)
        self._verify(lib.handlers['path w/ colon & lineno'],
                     r'c:\temp\lib.py', 1234567890)
        self._verify(lib.handlers['no source'],
                     classes_source)

    def test_dynamic_with_non_ascii_source(self):
        lib = TestLibrary('classes.DynamicWithSource')
        self._verify(lib.handlers['nön-äscii'], 'hyvä esimerkki')
        self._verify(lib.handlers['nön-äscii utf-8'], '福', 88)

    def test_dynamic_init(self):
        lib_with_init = TestLibrary('classes.ArgDocDynamicLibrary')
        lib_without_init = TestLibrary('classes.DynamicWithSource')
        self._verify(lib_with_init.init, classes_source, 217)
        self._verify(lib_without_init.init, classes_source, -1)

    def test_dynamic_invalid_source(self):
        logger = LoggerMock()
        lib = TestLibrary('classes.DynamicWithSource', logger=logger)
        self._verify(lib.handlers['invalid source'], None)
        error = (
            "Error in library 'classes.DynamicWithSource': "
            "Getting source information for keyword 'Invalid Source' failed: "
            "Calling dynamic method 'get_keyword_source' failed: "
            "Return value must be a string, got integer."
        )
        assert_equal(logger.messages, [(error, 'ERROR')])

    def _verify(self, kw, source, lineno=-1):
        if source:
            source = re.sub(r'(\.pyc|\$py\.class)$', '.py', source)
            source = os.path.normpath(source)
        assert_equal(kw.source, source)
        assert_equal(kw.lineno, lineno)


class LoggerMock(object):

    def __init__(self):
        self.messages = []

    def write(self, message, level):
        self.messages.append((message, level))

    def info(self, message):
        self.write(message, 'INFO')

    def debug(self, message):
        pass


if __name__ == '__main__':
    unittest.main()
