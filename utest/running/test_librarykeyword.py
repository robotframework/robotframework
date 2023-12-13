import inspect
import os.path
import re
import sys
import unittest
from pathlib import Path

from robot.errors import DataError
from robot.running.librarykeyword import StaticKeyword, DynamicKeyword
from robot.running.testlibraries import DynamicLibrary, TestLibrary
from robot.utils import type_name
from robot.utils.asserts import assert_equal, assert_raises_with_msg, assert_true

from classes import (NameLibrary, DocLibrary, ArgInfoLibrary,
                     __file__ as classes_source)
from ArgumentsPython import ArgumentsPython


def get_keyword_methods(lib):
    attrs = [getattr(lib, a) for a in dir(lib) if not a.startswith('_')]
    return [a for a in attrs if inspect.ismethod(a)]


def assert_argspec(argspec, minargs=0, maxargs=0, positional=(), varargs=None,
                   named_only=(), var_named=None, defaults=None):
    assert_equal(argspec.minargs, minargs)
    assert_equal(argspec.maxargs, maxargs)
    assert_equal(argspec.positional, positional)
    assert_equal(argspec.var_positional, varargs)
    assert_equal(argspec.named_only, named_only)
    assert_equal(argspec.var_named, var_named)
    assert_equal(argspec.defaults, defaults or {})


class TestStaticKeyword(unittest.TestCase):

    def test_name(self):
        for method in get_keyword_methods(NameLibrary()):
            kw = StaticKeyword.from_name(method.__name__,
                                         TestLibrary.from_class(NameLibrary))
            assert_equal(kw.name, method.__doc__)
            assert_equal(kw.full_name, f'NameLibrary.{method.__doc__}')

    def test_docs(self):
        for method in get_keyword_methods(DocLibrary()):
            kw = StaticKeyword.from_name(method.__name__,
                                         TestLibrary.from_class(DocLibrary))
            assert_equal(kw.doc, method.expected_doc)
            assert_equal(kw.short_doc, method.expected_shortdoc)

    def test_arguments(self):
        for method in get_keyword_methods(ArgInfoLibrary()):
            kw = StaticKeyword.from_name(method.__name__,
                                         TestLibrary.from_class(ArgInfoLibrary))
            args = (kw.args.positional, kw.args.defaults, kw.args.var_positional,
                    kw.args.var_named)
            expected = eval(method.__doc__)
            assert_equal(args, expected, method.__name__)

    def test_arg_limits(self):
        for method in get_keyword_methods(ArgumentsPython()):
            kw = StaticKeyword.from_name(method.__name__,
                                         TestLibrary.from_class(ArgumentsPython))
            exp_mina, exp_maxa = eval(method.__doc__)
            assert_equal(kw.args.minargs, exp_mina)
            assert_equal(kw.args.maxargs, exp_maxa)

    def test_getarginfo_getattr(self):
        keywords = TestLibrary.from_name('classes.GetattrLibrary').keywords
        assert_equal(len(keywords), 3)
        for kw in keywords:
            assert_true(kw.name in ('Foo', 'Bar', 'Zap'))
            assert_equal(kw.args.minargs, 0)
            assert_equal(kw.args.maxargs, sys.maxsize)


class TestDynamicKeyword(unittest.TestCase):

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
        self._assert_fails("Calling dynamic method 'get_keyword_documentation' failed: "
                           "Return value must be a string, got boolean.", doc=True)

    def test_none_argspec(self):
        self._assert_spec(None, 0, sys.maxsize, var_positional='varargs', var_named=False)

    def test_none_argspec_when_kwargs_supported(self):
        self._assert_spec(None, 0, sys.maxsize, var_positional='varargs', var_named='kwargs')

    def test_empty_argspec(self):
        self._assert_spec([])

    def test_mandatory_args(self):
        for argspec in [['arg'], ['arg1', 'arg2', 'arg3']]:
            self._assert_spec(argspec, len(argspec), len(argspec), tuple(argspec))

    def test_only_default_args(self):
        self._assert_spec(['d1=default', 'd2=True'],
                          0, 2, ('d1', 'd2'), defaults={'d1': 'default', 'd2': 'True'})

    def test_default_as_tuple_or_list_like(self):
        self._assert_spec([('d1', 'default'), ['d2', True]],
                          0, 2, ('d1', 'd2'), defaults={'d1': 'default', 'd2': True})

    def test_default_value_may_contain_equal_sign(self):
        self._assert_spec(['d=foo=bar'], 0, 1, ('d',), defaults={'d': 'foo=bar'})

    def test_default_value_as_tuple_may_contain_equal_sign(self):
        self._assert_spec([('n=m', 'd=f')], 0, 1, ('n=m',), defaults={'n=m': 'd=f'})

    def test_varargs(self):
        self._assert_spec(['*vararg'], 0, sys.maxsize, var_positional='vararg')

    def test_kwargs(self):
        self._assert_spec(['**kwarg'], 0, 0, var_named='kwarg')

    def test_varargs_and_kwargs(self):
        self._assert_spec(['*vararg', '**kwarg'],
                          0, sys.maxsize, var_positional='vararg', var_named='kwarg')

    def test_kwonly(self):
        self._assert_spec(['*', 'k', 'w', 'o'], named_only=('k', 'w', 'o'))
        self._assert_spec(['*vars', 'kwo',], var_positional='vars', named_only=('kwo',))

    def test_kwonly_with_defaults(self):
        self._assert_spec(['*', 'kwo=default'],
                          named_only=('kwo',),
                          defaults={'kwo': 'default'})
        self._assert_spec(['*vars', 'kwo=default'],
                          var_positional='vars',
                          named_only=('kwo',),
                          defaults={'kwo': 'default'})
        self._assert_spec(['*', 'x=1', 'y', 'z=3'],
                          named_only=('x', 'y', 'z'),
                          defaults={'x': '1', 'z': '3'})

    def test_kwonly_with_defaults_tuple(self):
        self._assert_spec(['*', ('kwo', 'default')],
                          named_only=('kwo',),
                          defaults={'kwo': 'default'})
        self._assert_spec([('*',), 'x=1', 'y', ('z', 3)],
                          named_only=('x', 'y', 'z'),
                          defaults={'x': '1', 'z': 3})

    def test_integration(self):
        self._assert_spec(['arg', 'default=value'],
                          1, 2,
                          positional=('arg', 'default'),
                          defaults={'default': 'value'})
        self._assert_spec(['arg', 'default=value', '*var'],
                          1, sys.maxsize,
                          positional=('arg', 'default'),
                          defaults={'default': 'value'},
                          var_positional='var')
        self._assert_spec(['arg', 'default=value', '**kw'],
                          1, 2,
                          positional=('arg', 'default'),
                          defaults={'default': 'value'},
                          var_named='kw')
        self._assert_spec(['arg', 'default=value', '*var', '**kw'],
                          1, sys.maxsize,
                          positional=('arg', 'default'),
                          defaults={'default': 'value'},
                          var_positional='var',
                          var_named='kw')
        self._assert_spec(['a', 'b=1', 'c=2', '*d', 'e', 'f=3', 'g', '**h'],
                          1, sys.maxsize,
                          positional=('a', 'b', 'c'),
                          defaults={'b': '1', 'c': '2', 'f': '3'},
                          var_positional='d',
                          named_only=('e', 'f', 'g'),
                          var_named='h')
        self._assert_spec([('a',), ('b', '1'), ('c', 2), ('*d',), ('e',), ('f', 3), ('g',), ('**h',)],
                          1, sys.maxsize,
                          positional=('a', 'b', 'c'),
                          defaults={'b': '1', 'c': 2, 'f': 3},
                          var_positional='d',
                          named_only=('e', 'f', 'g'),
                          var_named='h')

    def test_invalid_argspec_type(self):
        for argspec in [True, [1, 2], ['arg', ()]]:
            self._assert_fails(f"Calling dynamic method 'get_keyword_arguments' failed: "
                               f"Return value must be a list of strings "
                               f"or non-empty tuples, got {type_name(argspec)}.",
                               argspec)

    def test_invalid_tuple(self):
        for invalid in [('too', 'many', 'values'), ('*too', 'many'),
                        ('**too', 'many'), (1, 2), (1,)]:
            self._assert_fails(f'Invalid argument specification: '
                               f'Invalid argument "{invalid}".',
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
            self._assert_fails("Too few 'run_keyword' method parameters to support "
                               "free named arguments.", spec)

    def test_missing_kwonlyargs_support(self):
        for spec in (['*', 'kwo'], ['*vars', 'kwo1', 'kwo2=default']):
            self._assert_fails("Too few 'run_keyword' method parameters to support "
                               "named-only arguments.", spec)

    def _assert_doc(self, doc, expected=None):
        expected = doc if expected is None else expected
        assert_equal(self._create_keyword(doc=doc).doc, expected)

    def _assert_spec(self, in_args, minargs=0, maxargs=0, positional=(),
                     var_positional=None, named_only=(), var_named=None, defaults=None):
        if var_positional and not maxargs:
            maxargs = sys.maxsize
        if var_named is None and not named_only:
            kwargs_support_modes = [True, False]
        elif var_named is False:
            kwargs_support_modes = [False]
            var_named = None
        else:
            kwargs_support_modes = [True]
        for kwargs_support in kwargs_support_modes:
            kw = self._create_keyword(in_args, kwargs_support=kwargs_support)
            assert_argspec(kw.args, minargs, maxargs, positional, var_positional,
                           named_only, var_named, defaults)

    def _assert_fails(self, error, *args, **kwargs):
        assert_raises_with_msg(DataError, error,
                               self._create_keyword, *args, **kwargs)

    def _create_keyword(self, argspec=None, doc=None, kwargs_support=False):
        class Library:

            def get_keyword_names(self):
                return ['kw']

            if kwargs_support:
                def run_keyword(self, name, args, kwargs):
                    pass
            else:
                def run_keyword(self, name, args):
                    pass

            def get_keyword_arguments(self, name):
                return argspec

            def get_keyword_documentation(self, name):
                return doc

        lib = DynamicLibrary.from_class(Library, logger=LoggerMock())
        return DynamicKeyword.from_name('kw', lib)


class TestSourceAndLineno(unittest.TestCase):

    def test_class_with_init(self):
        lib = TestLibrary.from_name('classes.RecordingLibrary')
        self._verify(lib, 'kw', classes_source, 206)
        self._verify(lib, 'init', classes_source, 202)

    def test_class_without_init(self):
        lib = TestLibrary.from_name('classes.NameLibrary')
        self._verify(lib, 'simple1', classes_source, 13)
        self._verify(lib, 'init', classes_source, None)

    def test_module(self):
        from module_library import __file__ as source
        lib = TestLibrary.from_name('module_library')
        self._verify(lib, 'passing', source, 5)
        self._verify(lib, 'init', source, None)

    def test_package(self):
        from robot.variables.search import __file__ as source
        from robot.variables import __file__ as init_source
        lib = TestLibrary.from_name('robot.variables')
        self._verify(lib, 'search_variable', source, 23)
        self._verify(lib, 'init', init_source, None)

    def test_decorated(self):
        lib = TestLibrary.from_name('classes.Decorated')
        self._verify(lib, 'no_wrapper', classes_source, 325)
        self._verify(lib, 'wrapper', classes_source, 332)
        self._verify(lib, 'external', classes_source, 337)
        self._verify(lib, 'no_def', classes_source, 340)

    def test_dynamic_without_source(self):
        lib = TestLibrary.from_name('classes.ArgDocDynamicLibrary')
        self._verify(lib, 'No Arg', classes_source, None)

    def test_dynamic(self):
        lib = TestLibrary.from_name('classes.DynamicWithSource')
        self._verify(lib, 'only path', classes_source, None)
        self._verify(lib, 'path & lineno', classes_source, 42)
        self._verify(lib, 'lineno only', classes_source, 6475)
        self._verify(lib, 'invalid path', 'path validity is not validated', None)
        self._verify(lib, 'path w/ colon', r'c:\temp\lib.py', None)
        self._verify(lib, 'path w/ colon & lineno', r'c:\temp\lib.py', 1234567890)
        self._verify(lib, 'no source', classes_source, None)

    def test_dynamic_with_non_ascii_source(self):
        lib = TestLibrary.from_name('classes.DynamicWithSource')
        self._verify(lib, 'nön-äscii', 'hyvä esimerkki', None)
        self._verify(lib, 'nön-äscii utf-8', '福', 88)

    def test_dynamic_init(self):
        lib_with_init = TestLibrary.from_name('classes.ArgDocDynamicLibrary')
        lib_without_init = TestLibrary.from_name('classes.DynamicWithSource')
        self._verify(lib_with_init, 'init', classes_source, 217)
        self._verify(lib_without_init, 'init', classes_source, None)

    def test_dynamic_invalid_source(self):
        logger = LoggerMock()
        lib = TestLibrary.from_name('classes.DynamicWithSource', logger=logger)
        self._verify(lib, 'invalid source', lib.source, None)
        error = (
            "Error in library 'classes.DynamicWithSource': "
            "Getting source information for keyword 'Invalid Source' failed: "
            "Calling dynamic method 'get_keyword_source' failed: "
            "Return value must be a string, got integer."
        )
        assert_equal(logger.messages[-1], (error, 'ERROR'))

    def _verify(self, lib, name, source, lineno):
        if name == 'init':
            kw = lib.init
        else:
            kw, = lib.find_keywords(name)
        if source:
            source = re.sub(r'(\.pyc|\$py\.class)$', '.py', str(source))
            source = Path(os.path.normpath(source))
        assert_equal(kw.source, source)
        assert_equal(kw.lineno, lineno)


class LoggerMock:

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
