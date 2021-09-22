import os.path
import re
import sys
import unittest

from robot.running.testlibraries import (TestLibrary, _ClassLibrary,
                                         _ModuleLibrary, _DynamicLibrary)
from robot.utils.asserts import (assert_equal, assert_false, assert_none,
                                 assert_not_equal, assert_not_none, assert_true,
                                 assert_raises, assert_raises_with_msg)
from robot.utils import normalize
from robot.errors import DataError

from classes import (NameLibrary, DocLibrary, ArgInfoLibrary, GetattrLibrary,
                     SynonymLibrary, __file__ as classes_source)


# Valid keyword names and arguments for some libraries
default_keywords = [ ( "no operation", () ),
                     ( "log", ("msg",) ),
                     ( "L O G", ("msg","warning") ),
                     ( "fail", () ),
                     ( "  f  a  i  l  ", ("msg",) ) ]
example_keywords = [ ( "Log", ("msg",) ),
                     ( "log many", () ),
                     ( "logmany", ("msg",) ),
                     ( "L O G M A N Y", ("m1","m2","m3","m4","m5") ),
                     ( "equals", ("1","1") ),
                     ( "equals", ("1","2","failed") ), ]
java_keywords = [ ( "print", ("msg",) ) ]


class TestLibraryTypes(unittest.TestCase):

    def test_python_library(self):
        lib = TestLibrary("BuiltIn")
        assert_equal(lib.__class__, _ClassLibrary)
        assert_equal(lib.positional_args, [])

    def test_python_library_with_args(self):
        lib = TestLibrary("ParameterLibrary", ['my_host', '8080'])
        assert_equal(lib.__class__, _ClassLibrary)
        assert_equal(lib.positional_args, ['my_host', '8080'])

    def test_module_library(self):
        lib = TestLibrary("module_library")
        assert_equal(lib.__class__, _ModuleLibrary)

    def test_module_library_with_args(self):
        assert_raises(DataError, TestLibrary, "module_library", ['arg'] )

    def test_dynamic_python_library(self):
        lib = TestLibrary("RunKeywordLibrary")
        assert_equal(lib.__class__, _DynamicLibrary)


class TestImports(unittest.TestCase):

    def test_import_python_class(self):
        lib = TestLibrary("BuiltIn")
        self._verify_lib(lib, "BuiltIn", default_keywords)

    def test_import_python_class_from_module(self):
        lib = TestLibrary("robot.libraries.BuiltIn.BuiltIn")
        self._verify_lib(lib, "robot.libraries.BuiltIn.BuiltIn", default_keywords)

    def test_import_python_module(self):
        lib = TestLibrary("module_library")
        kws = ["passing", "two arguments from class", "lambdakeyword", "argument"]
        self._verify_lib(lib, "module_library", [(kw, None) for kw in kws])

    def test_import_python_module_from_module(self):
        lib = TestLibrary("pythonmodule.library")
        self._verify_lib(lib, "pythonmodule.library",
                         [("keyword from submodule", None)])

    def test_import_non_existing_module(self):
        msg = ("Importing library '{libname}' failed: "
               "ModuleNotFoundError: No module named '{modname}'")
        for name in 'nonexisting', 'nonexi.sting':
            error = assert_raises(DataError, TestLibrary, name)
            expected = msg.format(libname=name, modname=name.split('.')[0])
            assert_equal(str(error).splitlines()[0], expected)

    def test_import_non_existing_class_from_existing_module(self):
        assert_raises_with_msg(DataError,
                               "Importing library 'pythonmodule.NonExisting' failed: "
                               "Module 'pythonmodule' does not contain 'NonExisting'.",
                               TestLibrary, 'pythonmodule.NonExisting')

    def test_import_invalid_type(self):
        msg = "Importing library '%s' failed: Expected class or module, got %s."
        assert_raises_with_msg(DataError,
                               msg % ('pythonmodule.some_string', 'string'),
                               TestLibrary, 'pythonmodule.some_string')
        assert_raises_with_msg(DataError,
                               msg % ('pythonmodule.some_object', 'SomeObject'),
                               TestLibrary, 'pythonmodule.some_object')

    def test_import_with_unicode_name(self):
        self._verify_lib(TestLibrary(u"BuiltIn"), "BuiltIn", default_keywords)
        self._verify_lib(TestLibrary(u"robot.libraries.BuiltIn.BuiltIn"),
                         "robot.libraries.BuiltIn.BuiltIn", default_keywords)
        self._verify_lib(TestLibrary(u"pythonmodule.library"), "pythonmodule.library",
                         [("keyword from submodule", None)])

    def test_global_scope(self):
        self._verify_scope(TestLibrary('libraryscope.Global'), 'GLOBAL')

    def _verify_scope(self, lib, expected):
        assert_equal(str(lib.scope), expected)

    def test_suite_scope(self):
        self._verify_scope(TestLibrary('libraryscope.Suite'), 'SUITE')
        self._verify_scope(TestLibrary('libraryscope.TestSuite'), 'SUITE')

    def test_test_scope(self):
        self._verify_scope(TestLibrary('libraryscope.Test'), 'TEST')
        self._verify_scope(TestLibrary('libraryscope.TestCase'), 'TEST')

    def test_task_scope_is_mapped_to_test_scope(self):
        self._verify_scope(TestLibrary('libraryscope.Task'), 'TEST')

    def test_invalid_scope_is_mapped_to_test_scope(self):
        for libname in ['libraryscope.InvalidValue',
                        'libraryscope.InvalidEmpty',
                        'libraryscope.InvalidMethod',
                        'libraryscope.InvalidNone']:
            self._verify_scope(TestLibrary(libname), 'TEST')

    def _verify_lib(self, lib, libname, keywords):
        assert_equal(libname, lib.name)
        for name, _ in keywords:
            handler = lib.handlers[name]
            exp = "%s.%s" % (libname, name)
            assert_equal(normalize(handler.longname), normalize(exp))


class TestLibraryInit(unittest.TestCase):

    def test_python_library_without_init(self):
        self._test_init_handler('ExampleLibrary')

    def test_python_library_with_init(self):
        self._test_init_handler('ParameterLibrary', ['foo'], 0, 2)

    def test_new_style_class_without_init(self):
        self._test_init_handler('newstyleclasses.NewStyleClassLibrary')

    def test_new_style_class_with_init(self):
        lib = self._test_init_handler('newstyleclasses.NewStyleClassArgsLibrary', ['value'], 1, 1)
        assert_equal(len(lib.handlers), 1)

    def test_library_with_metaclass(self):
        self._test_init_handler('newstyleclasses.MetaClassLibrary')

    def test_library_with_zero_len(self):
        self._test_init_handler('LenLibrary')

    def _test_init_handler(self, libname, args=None, min=0, max=0):
        lib = TestLibrary(libname, args)
        assert_equal(lib.init.arguments.minargs, min)
        assert_equal(lib.init.arguments.maxargs, max)
        return lib


class TestVersion(unittest.TestCase):

    def test_no_version(self):
        self._verify_version('classes.NameLibrary', '')

    def test_version_in_class_library(self):
        self._verify_version('classes.VersionLibrary', '0.1')
        self._verify_version('classes.VersionObjectLibrary', 'ver')

    def test_version_in_module_library(self):
        self._verify_version('module_library', 'test')

    def _verify_version(self, name, version):
        assert_equal(TestLibrary(name).version, version)


class TestDocFormat(unittest.TestCase):

    def test_no_doc_format(self):
        self._verify_doc_format('classes.NameLibrary', '')

    def test_doc_format_in_python_libarary(self):
        self._verify_doc_format('classes.VersionLibrary', 'HTML')

    def _verify_doc_format(self, name, doc_format):
        assert_equal(TestLibrary(name).doc_format, doc_format)


class _TestScopes(unittest.TestCase):

    def _get_lib_and_instance(self, name):
        lib = TestLibrary(name)
        if lib.scope.is_global:
            assert_not_none(lib._libinst)
        else:
            assert_none(lib._libinst)
        return lib, lib._libinst

    def _start_new_suite(self):
        self.lib.start_suite()
        assert_none(self.lib._libinst)
        inst = self.lib.get_instance()
        assert_not_none(inst)
        return inst

    def _verify_end_suite_restores_previous_instance(self, prev_inst):
        self.lib.end_suite()
        assert_true(self.lib._libinst is prev_inst)
        if prev_inst is not None:
            assert_true(self.lib.get_instance() is prev_inst)


class GlobalScope(_TestScopes):

    def test_global_scope(self):
        lib, instance = self._get_lib_and_instance('BuiltIn')
        for mname in ['start_suite', 'start_suite', 'start_test', 'end_test',
                      'start_test', 'end_test', 'end_suite', 'start_suite',
                      'start_test', 'end_test', 'end_suite', 'end_suite']:
            getattr(lib, mname)()
            assert_true(instance is lib._libinst)


class TestSuiteScope(_TestScopes):

    def setUp(self):
        self.lib, self.instance = self._get_lib_and_instance("libraryscope.Suite")
        self.lib.start_suite()

    def test_start_suite_flushes_instance(self):
        assert_none(self.lib._libinst)
        inst = self.lib.get_instance()
        assert_not_none(inst)
        assert_false(inst is self.instance)

    def test_start_test_or_end_test_do_not_flush_instance(self):
        inst = self.lib.get_instance()
        for _ in range(10):
            self.lib.start_test()
            assert_true(inst is self.lib._libinst)
            assert_true(inst is self.lib.get_instance())
            self.lib.end_test()
            assert_true(inst is self.lib._libinst)

    def test_end_suite_restores_previous_instance_with_one_suite(self):
        self.lib.start_test()
        self.lib.get_instance()
        self.lib.end_test()
        self.lib.get_instance()
        self.lib.end_suite()
        assert_none(self.lib._libinst)

    def test_intance_caching(self):
        inst1 = self.lib.get_instance()
        inst2 = self._start_new_suite()
        assert_false(inst1 is inst2)
        self._run_tests(inst2)
        self._verify_end_suite_restores_previous_instance(inst1)
        inst3 = self._start_new_suite()
        inst4 = self._start_new_suite()
        self._run_tests(inst4, 10)
        self._verify_end_suite_restores_previous_instance(inst3)
        self._verify_end_suite_restores_previous_instance(inst1)
        self._verify_end_suite_restores_previous_instance(None)

    def _run_tests(self, exp_inst, count=3):
        for _ in range(count):
            self.lib.start_test()
            assert_true(self.lib.get_instance() is exp_inst)
            self.lib.end_test()
            assert_true(self.lib.get_instance() is exp_inst)


class TestCaseScope(_TestScopes):

    def setUp(self):
        self.lib, self.instance = self._get_lib_and_instance("libraryscope.Test")
        self.lib.start_suite()

    def test_different_instances_for_all_tests(self):
        self._run_tests(None)
        inst = self.lib.get_instance()
        self._run_tests(inst, 5)
        self.lib.end_suite()
        assert_none(self.lib._libinst)

    def test_nested_suites(self):
        top_inst = self.lib.get_instance()
        self._run_tests(top_inst, 4)
        self.lib.start_suite()
        self._run_tests(None, 3)
        self.lib.start_suite()
        self._run_tests(self.lib.get_instance(), 3)
        self.lib.end_suite()
        self.lib.end_suite()
        assert_true(self.lib._libinst is top_inst)

    def _run_tests(self, suite_inst, count=3):
        old_insts = [suite_inst]
        for _ in range(count):
            self.lib.start_test()
            assert_none(self.lib._libinst)
            inst = self.lib.get_instance()
            assert_false(inst in old_insts)
            old_insts.append(inst)
            self.lib.end_test()
            assert_true(self.lib._libinst is suite_inst)


class TestHandlers(unittest.TestCase):

    def test_get_handlers(self):
        for lib in [NameLibrary, DocLibrary, ArgInfoLibrary, GetattrLibrary, SynonymLibrary]:
            handlers = TestLibrary('classes.%s' % lib.__name__).handlers
            assert_equal(lib.handler_count, len(handlers), lib.__name__)
            for handler in handlers:
                assert_false(handler._handler_name.startswith('_'))
                assert_true('skip' not in handler._handler_name)

    def test_non_global_dynamic_handlers(self):
        lib = TestLibrary("RunKeywordLibrary")
        assert_equal(len(lib.handlers), 2)
        assert_true('Run Keyword That Passes' in lib.handlers)
        assert_true('Run Keyword That Fails' in lib.handlers)
        assert_none(lib.handlers['Run Keyword That Passes']._method)
        assert_none(lib.handlers['Run Keyword That Fails']._method)

    def test_global_dynamic_handlers(self):
        lib = TestLibrary("RunKeywordLibrary.GlobalRunKeywordLibrary")
        assert_equal(len(lib.handlers), 2)
        for name in 'Run Keyword That Passes', 'Run Keyword That Fails':
            handler = lib.handlers[name]
            assert_not_none(handler._method)
            assert_not_equal(handler._method, lib._libinst.run_keyword)
            assert_equal(handler._method.__name__, 'handler')

    def test_synonym_handlers(self):
        testlib = TestLibrary('classes.SynonymLibrary')
        names = ['handler', 'synonym_handler', 'another_synonym']
        for handler in testlib.handlers:
            # test 'handler_name' -- raises ValueError if it isn't in 'names'
            names.remove(handler._handler_name)
        assert_equal(len(names), 0, 'handlers %s not created' % names, False)

    def test_global_handlers_are_created_only_once(self):
        lib = TestLibrary('classes.RecordingLibrary')
        assert_true(lib.scope.is_global)
        instance = lib._libinst
        assert_true(instance is not None)
        assert_equal(instance.kw_accessed, 1)
        assert_equal(instance.kw_called, 0)
        for _ in range(5):
            lib.handlers.create_runner('kw')._run(_FakeContext(), [])
        assert_true(lib._libinst is instance)
        assert_equal(instance.kw_accessed, 1)
        assert_equal(instance.kw_called, 5)


class TestDynamicLibrary(unittest.TestCase):

    def test_get_keyword_doc_is_used_if_present(self):
        lib = TestLibrary('classes.ArgDocDynamicLibrary')
        assert_equal(lib.handlers['No Arg'].doc,
                     'Keyword documentation for No Arg')
        assert_equal(lib.handlers['Multiline'].doc,
                     'Multiline\nshort doc!\n\nBody\nhere.')

    def test_get_keyword_doc_and_args_are_ignored_if_not_callable(self):
        lib = TestLibrary('classes.InvalidAttributeDynamicLibrary')
        assert_equal(len(lib.handlers), 7)
        assert_equal(lib.handlers['No Arg'].doc, '')
        assert_handler_args(lib.handlers['No Arg'], 0, sys.maxsize)

    def test_handler_is_not_created_if_get_keyword_doc_fails(self):
        lib = TestLibrary('classes.InvalidGetDocDynamicLibrary')
        assert_equal(len(lib.handlers), 0)

    def test_handler_is_not_created_if_get_keyword_args_fails(self):
        lib = TestLibrary('classes.InvalidGetArgsDynamicLibrary')
        assert_equal(len(lib.handlers), 0)

    def test_arguments_without_kwargs(self):
        lib = TestLibrary('classes.ArgDocDynamicLibrary')
        for name, (mina, maxa) in [('No Arg', (0, 0)),
                                   ('One Arg', (1, 1)),
                                   ('One or Two Args', (1, 2)),
                                   ('Many Args', (0, sys.maxsize)),
                                   ('No Arg Spec', (0, sys.maxsize))]:
            assert_handler_args(lib.handlers[name], mina, maxa)

    def test_arguments_with_kwargs(self):
        lib = TestLibrary('classes.ArgDocDynamicLibraryWithKwargsSupport')
        for name, (mina, maxa) in [('No Arg', (0, 0)),
                                   ('One Arg', (1, 1)),
                                   ('One or Two Args', (1, 2)),
                                   ('Many Args', (0, sys.maxsize))]:
            assert_handler_args(lib.handlers[name], mina, maxa, kwargs=False)
        for name, (mina, maxa) in [('Kwargs', (0, 0)),
                                   ('Varargs and Kwargs', (0, sys.maxsize)),
                                   ('No Arg Spec', (0, sys.maxsize))]:
            assert_handler_args(lib.handlers[name], mina, maxa, kwargs=True)


def assert_handler_args(handler, minargs=0, maxargs=0, kwargs=False):
    assert_equal(handler.arguments.minargs, minargs)
    assert_equal(handler.arguments.maxargs, maxargs)
    assert_equal(bool(handler.arguments.var_named), kwargs)


class TestDynamicLibraryIntroDocumentation(unittest.TestCase):

    def test_doc_from_class_definition(self):
        self._assert_intro_doc('dynlibs.StaticDocsLib',
                               'This is lib intro.')

    def test_doc_from_dynamic_method(self):
        self._assert_intro_doc('dynlibs.DynamicDocsLib',
                               'Dynamic intro doc.')

    def test_dynamic_doc_overrides_class_doc(self):
        self._assert_intro_doc('dynlibs.StaticAndDynamicDocsLib',
                                         'dynamic override')

    def test_failure_in_dynamic_resolving_of_doc(self):
        lib = TestLibrary('dynlibs.FailingDynamicDocLib')
        assert_raises(DataError, getattr, lib, 'doc')

    def _assert_intro_doc(self, library_name, expected_doc):
        assert_equal(TestLibrary(library_name).doc, expected_doc)


class TestDynamicLibraryInitDocumentation(unittest.TestCase):

    def test_doc_from_class_init(self):
        self._assert_init_doc('dynlibs.StaticDocsLib', 'Init doc.')

    def test_doc_from_dynamic_method(self):
        self._assert_init_doc('dynlibs.DynamicDocsLib', 'Dynamic init doc.')

    def test_dynamic_doc_overrides_method_doc(self):
        self._assert_init_doc('dynlibs.StaticAndDynamicDocsLib',
                              'dynamic override')

    def test_failure_in_dynamic_resolving_of_doc(self):
        init = TestLibrary('dynlibs.FailingDynamicDocLib').init
        assert_raises(DataError, getattr, init, 'doc')

    def _assert_init_doc(self, library_name, expected_doc):
        assert_equal(TestLibrary(library_name).init.doc, expected_doc)


class TestSourceAndLineno(unittest.TestCase):

    def test_class(self):
        lib = TestLibrary('classes.NameLibrary')
        self._verify(lib, classes_source, 10)

    def test_class_in_package(self):
        from robot.variables.variables import __file__ as source
        lib = TestLibrary('robot.variables.Variables')
        self._verify(lib, source, 24)

    def test_dynamic(self):
        lib = TestLibrary('classes.ArgDocDynamicLibrary')
        self._verify(lib, classes_source, 215)

    def test_module(self):
        from module_library import __file__ as source
        lib = TestLibrary('module_library')
        self._verify(lib, source, 1)

    def test_package(self):
        from robot.variables import __file__ as source
        lib = TestLibrary('robot.variables')
        self._verify(lib, source, 1)

    def test_decorated(self):
        lib = TestLibrary('classes.Decorated')
        self._verify(lib, classes_source, 317)

    def test_no_class_statement(self):
        lib = TestLibrary('classes.NoClassDefinition')
        self._verify(lib, classes_source, -1)

    def _verify(self, lib, source, lineno):
        if source:
            source = re.sub(r'(\.pyc|\$py\.class)$', '.py', source)
            source = os.path.normpath(source)
        assert_equal(lib.source, source)
        assert_equal(lib.lineno, lineno)


class _FakeNamespace:
    def __init__(self):
        self.variables = _FakeVariableScope()
        self.uk_handlers = []
        self.test = None


class _FakeVariableScope:
    def __init__(self):
        self.variables = {}
    def replace_scalar(self, variable):
        return variable
    def replace_list(self, args, replace_until=None):
        return []
    def replace_string(self, variable):
        try:
            number = variable.replace('$', '').replace('{', '').replace('}', '')
            return int(number)
        except ValueError:
            pass
        try:
            return self.variables[variable]
        except KeyError:
            raise DataError("Non-existing variable '%s'" % variable)
    def __setitem__(self, key, value):
        self.variables.__setitem__(key, value)
    def __getitem__(self, key):
        return self.variables.get(key)


class _FakeOutput:
    def trace(self, str):
        pass
    def log_output(self, output):
        pass


class _FakeContext:
    def __init__(self):
        self.output = _FakeOutput()
        self.namespace = _FakeNamespace()
        self.dry_run = False
        self.in_teardown = False
        self.variables = _FakeVariableScope()
        self.timeouts = set()
        self.test = None


if __name__ == '__main__':
    unittest.main()
