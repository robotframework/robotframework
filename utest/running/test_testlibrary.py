import os.path
import re
import sys
import unittest
from pathlib import Path

from robot.running.testlibraries import (TestLibrary, ClassLibrary,
                                         ModuleLibrary, DynamicLibrary)
from robot.utils.asserts import (assert_equal, assert_false, assert_none,
                                 assert_not_none, assert_true,
                                 assert_raises, assert_raises_with_msg)
from robot.utils import normalize
from robot.errors import DataError

from classes import (NameLibrary, DocLibrary, ArgInfoLibrary, GetattrLibrary,
                     SynonymLibrary, __file__ as classes_source)


class NullLogger:

    def write(self, *args, **kwargs):
        pass

    error = warn = info = debug = write


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


class TestLibraryTypes(unittest.TestCase):

    def test_python_library(self):
        lib = TestLibrary.from_name("BuiltIn")
        assert_true(isinstance(lib, ClassLibrary))
        assert_equal(lib.init.positional, [])
        assert_equal(lib.init.named, {})

    def test_python_library_with_args(self):
        lib = TestLibrary.from_name("ParameterLibrary", args=['my_host', 'port=8080'])
        assert_true(isinstance(lib, ClassLibrary))
        assert_equal(lib.init.positional, ['my_host'])
        assert_equal(lib.init.named, {'port': '8080'})

    def test_module_library(self):
        lib = TestLibrary.from_name("module_library")
        assert_true(isinstance(lib, ModuleLibrary))

    def test_module_library_with_args(self):
        assert_raises(DataError, TestLibrary.from_name, "module_library", args=['arg'])

    def test_dynamic_python_library(self):
        lib = TestLibrary.from_name("RunKeywordLibrary")
        assert_true(isinstance(lib, DynamicLibrary))


class TestImports(unittest.TestCase):

    def test_import_python_class(self):
        lib = TestLibrary.from_name("BuiltIn")
        self._verify_lib(lib, "BuiltIn", default_keywords)

    def test_import_python_class_from_module(self):
        lib = TestLibrary.from_name("robot.libraries.BuiltIn.BuiltIn")
        self._verify_lib(lib, "robot.libraries.BuiltIn.BuiltIn", default_keywords)

    def test_import_python_module(self):
        lib = TestLibrary.from_name("module_library")
        kws = ["passing", "two arguments from class", "lambdakeyword", "argument"]
        self._verify_lib(lib, "module_library", [(kw, None) for kw in kws])

    def test_import_python_module_from_module(self):
        lib = TestLibrary.from_name("pythonmodule.library")
        self._verify_lib(lib, "pythonmodule.library",
                         [("keyword from submodule", None)])

    def test_import_non_existing_module(self):
        msg = ("Importing library '{libname}' failed: "
               "ModuleNotFoundError: No module named '{modname}'")
        for name in 'nonexisting', 'nonexi.sting':
            error = assert_raises(DataError, TestLibrary.from_name, name)
            expected = msg.format(libname=name, modname=name.split('.')[0])
            assert_equal(str(error).splitlines()[0], expected)

    def test_import_non_existing_class_from_existing_module(self):
        assert_raises_with_msg(DataError,
                               "Importing library 'pythonmodule.NonExisting' failed: "
                               "Module 'pythonmodule' does not contain 'NonExisting'.",
                               TestLibrary.from_name, 'pythonmodule.NonExisting')

    def test_import_invalid_type(self):
        msg = "Importing library '%s' failed: Expected class or module, got %s."
        assert_raises_with_msg(DataError,
                               msg % ('pythonmodule.some_string', 'string'),
                               TestLibrary.from_name, 'pythonmodule.some_string')
        assert_raises_with_msg(DataError,
                               msg % ('pythonmodule.some_object', 'SomeObject'),
                               TestLibrary.from_name, 'pythonmodule.some_object')

    def test_global_scope(self):
        self._verify_scope(TestLibrary.from_name('libraryscope.Global'), 'GLOBAL')

    def _verify_scope(self, lib, expected):
        assert_equal(lib.scope.name, expected)

    def test_suite_scope(self):
        self._verify_scope(TestLibrary.from_name('libraryscope.Suite'), 'SUITE')
        self._verify_scope(TestLibrary.from_name('libraryscope.TestSuite'), 'SUITE')

    def test_test_scope(self):
        self._verify_scope(TestLibrary.from_name('libraryscope.Test'), 'TEST')
        self._verify_scope(TestLibrary.from_name('libraryscope.TestCase'), 'TEST')

    def test_task_scope_is_mapped_to_test_scope(self):
        self._verify_scope(TestLibrary.from_name('libraryscope.Task'), 'TEST')

    def test_invalid_scope_is_mapped_to_test_scope(self):
        for libname in ['libraryscope.InvalidValue',
                        'libraryscope.InvalidEmpty',
                        'libraryscope.InvalidMethod',
                        'libraryscope.InvalidNone']:
            self._verify_scope(TestLibrary.from_name(libname), 'TEST')

    def _verify_lib(self, lib, libname, keywords):
        assert_equal(libname, lib.name)
        for name, _ in keywords:
            kw = lib.find_keywords(name)[0]
            assert_equal(normalize(kw.full_name), normalize(f"{libname}.{name}"))


class TestLibraryInit(unittest.TestCase):

    def test_python_library_without_init(self):
        self._test_init_handler('ExampleLibrary')

    def test_python_library_with_init(self):
        self._test_init_handler('ParameterLibrary', ['foo'], 0, 2)

    def test_new_style_class_without_init(self):
        self._test_init_handler('newstyleclasses.NewStyleClassLibrary')

    def test_new_style_class_with_init(self):
        lib = self._test_init_handler('newstyleclasses.NewStyleClassArgsLibrary', ['value'], 1, 1)
        assert_equal(len(lib.keywords), 1)

    def test_library_with_metaclass(self):
        self._test_init_handler('newstyleclasses.MetaClassLibrary')

    def test_library_with_zero_len(self):
        self._test_init_handler('LenLibrary')

    def _test_init_handler(self, libname, args=None, min=0, max=0):
        lib = TestLibrary.from_name(libname, args=args)
        assert_equal(lib.init.args.minargs, min)
        assert_equal(lib.init.args.maxargs, max)
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
        assert_equal(TestLibrary.from_name(name).version, version)


class TestDocFormat(unittest.TestCase):

    def test_no_doc_format(self):
        self._verify_doc_format('classes.NameLibrary', '')

    def test_doc_format_in_python_libarary(self):
        self._verify_doc_format('classes.VersionLibrary', 'HTML')

    def _verify_doc_format(self, name, doc_format):
        assert_equal(TestLibrary.from_name(name).doc_format, doc_format)


class _TestScopes(unittest.TestCase):
    lib: TestLibrary

    def start_suite(self, instance=False):
        self.lib.scope_manager.start_suite()
        assert_none(self.lib._instance)
        if instance:
            inst = self.lib.instance
            assert_not_none(inst)
            return inst

    def end_suite(self):
        self.lib.scope_manager.end_suite()

    def start_test(self):
        self.lib.scope_manager.start_test()

    def end_test(self):
        self.lib.scope_manager.end_test()

    def _verify_end_suite_restores_previous_instance(self, prev_inst):
        self.lib.scope_manager.end_suite()
        assert_true(self.lib._instance is prev_inst)
        if prev_inst is not None:
            assert_true(self.lib.instance is prev_inst)


class GlobalScope(_TestScopes):

    def test_global_scope(self):
        lib = TestLibrary.from_name('BuiltIn')
        instance = lib._instance
        assert_not_none(instance)
        for mname in ['start_suite', 'start_suite', 'start_test', 'end_test',
                      'start_test', 'end_test', 'end_suite', 'start_suite',
                      'start_test', 'end_test', 'end_suite', 'end_suite']:
            getattr(lib.scope_manager, mname)()
            assert_true(instance is lib._instance)


class TestSuiteScope(_TestScopes):

    def setUp(self):
        self.lib = TestLibrary.from_name('libraryscope.Suite')
        self.lib.instance = None
        self.start_suite()
        assert_none(self.lib._instance)

    def test_start_suite_flushes_instance(self):
        assert_none(self.lib._instance)
        assert_not_none(self.lib.instance)

    def test_start_test_or_end_test_do_not_flush_instance(self):
        inst = self.lib.instance
        for _ in range(10):
            self.start_test()
            assert_true(inst is self.lib._instance)
            assert_true(inst is self.lib.instance)
            self.end_test()
            assert_true(inst is self.lib._instance)
            assert_true(inst is self.lib.instance)

    def test_end_suite_restores_previous_instance_with_one_suite(self):
        inst = self.lib.instance
        assert_not_none(self.lib._instance)
        self.start_test()
        assert_true(inst, self.lib.instance)
        self.end_test()
        assert_true(inst, self.lib.instance)
        self.end_suite()
        assert_none(self.lib._instance)

    def test_instance_caching(self):
        inst1 = self.lib.instance
        inst2 = self.start_suite(instance=True)
        assert_false(inst1 is inst2)
        self._run_tests(inst2)
        self._verify_end_suite_restores_previous_instance(inst1)
        inst3 = self.start_suite(instance=True)
        inst4 = self.start_suite(instance=True)
        self._run_tests(inst4, 10)
        self._verify_end_suite_restores_previous_instance(inst3)
        self._verify_end_suite_restores_previous_instance(inst1)
        self._verify_end_suite_restores_previous_instance(None)

    def _run_tests(self, exp_inst, count=3):
        for _ in range(count):
            self.start_test()
            assert_true(self.lib.instance is exp_inst)
            self.end_test()
            assert_true(self.lib.instance is exp_inst)


class TestCaseScope(_TestScopes):

    def setUp(self):
        self.lib = TestLibrary.from_name('libraryscope.Test')
        self.lib.instance = None
        self.start_suite()

    def test_different_instances_for_all_tests(self):
        self._run_tests(None)
        inst = self.lib.instance
        self._run_tests(inst, 5)
        self.end_suite()
        assert_none(self.lib._instance)

    def test_nested_suites(self):
        top_inst = self.lib.instance
        self._run_tests(top_inst, 4)
        self.start_suite()
        self._run_tests(None, 3)
        self.start_suite()
        self._run_tests(self.lib.instance, 3)
        self.end_suite()
        self.end_suite()
        assert_true(self.lib._instance is top_inst)

    def _run_tests(self, suite_inst, count=3):
        old_insts = [suite_inst]
        for _ in range(count):
            self.start_test()
            assert_none(self.lib._instance)
            inst = self.lib.instance
            assert_false(inst in old_insts)
            old_insts.append(inst)
            self.end_test()
            assert_true(self.lib._instance is suite_inst)


class TestKeywords(unittest.TestCase):

    def test_keywords(self):
        for lib in [NameLibrary, DocLibrary, ArgInfoLibrary, GetattrLibrary, SynonymLibrary]:
            keywords = TestLibrary.from_class(lib).keywords
            assert_equal(lib.handler_count, len(keywords), lib.__name__)
            for kw in keywords:
                name = kw.method.__name__
                assert_false(name.startswith('_'))
                assert_false('skip' in name)

    def test_non_global_dynamic_keywords(self):
        lib = TestLibrary.from_name("RunKeywordLibrary")
        kw1, kw2 = lib.keywords
        assert_equal(kw1.name, 'Run Keyword That Passes')
        assert_equal(kw2.name, 'Run Keyword That Fails')

    def test_global_dynamic_keywords(self):
        lib = TestLibrary.from_name("RunKeywordLibrary.GlobalRunKeywordLibrary")
        kw1, kw2 = lib.keywords
        assert_equal(kw1.name, 'Run Keyword That Passes')
        assert_equal(kw2.name, 'Run Keyword That Fails')

    def test_synonyms(self):
        lib = TestLibrary.from_name('classes.SynonymLibrary')
        kw1, kw2, kw3 = lib.keywords
        assert_equal(kw1.name, 'Another Synonym')
        assert_equal(kw2.name, 'Handler')
        assert_equal(kw3.name, 'Synonym Handler')

    def test_global_handlers_are_created_only_once(self):
        lib = TestLibrary.from_name('classes.RecordingLibrary')
        assert_true(lib.scope is lib.scope.GLOBAL)
        instance = lib._instance
        assert_true(instance is not None)
        assert_equal(instance.kw_accessed, 2)
        assert_equal(instance.kw_called, 0)
        kw, = lib.keywords
        for _ in range(42):
            kw.create_runner('kw')._run(kw, [], None, _FakeContext())
        assert_true(lib._instance is instance)
        assert_equal(instance.kw_accessed, 44)
        assert_equal(instance.kw_called, 42)


class TestDynamicLibrary(unittest.TestCase):

    def test_get_keyword_doc_is_used_if_present(self):
        lib = TestLibrary.from_name('classes.ArgDocDynamicLibrary')
        assert_equal(self.find(lib, 'No Arg').doc,
                     'Keyword documentation for No Arg')
        assert_equal(self.find(lib, 'Multiline').doc,
                     'Multiline\nshort doc!\n\nBody\nhere.')

    def find(self, lib, name):
        kws = lib.find_keywords(name)
        assert len(kws) == 1
        return kws[0]

    def test_get_keyword_doc_and_args_are_ignored_if_not_callable(self):
        lib = TestLibrary.from_name('classes.InvalidAttributeDynamicLibrary')
        assert_equal(len(lib.keywords), 7)
        assert_equal(self.find(lib, 'No Arg').doc, '')
        assert_args(self.find(lib, 'No Arg'), 0, sys.maxsize)

    def test_handler_is_not_created_if_get_keyword_doc_fails(self):
        lib = TestLibrary.from_name('classes.InvalidGetDocDynamicLibrary',
                                    logger=NullLogger())
        assert_equal(len(lib.keywords), 0)

    def test_handler_is_not_created_if_get_keyword_args_fails(self):
        lib = TestLibrary.from_name('classes.InvalidGetArgsDynamicLibrary',
                                    logger=NullLogger())
        assert_equal(len(lib.keywords), 0)

    def test_arguments_without_kwargs(self):
        lib = TestLibrary.from_name('classes.ArgDocDynamicLibrary')
        for name, (mina, maxa) in [('No Arg', (0, 0)),
                                   ('One Arg', (1, 1)),
                                   ('One or Two Args', (1, 2)),
                                   ('Many Args', (0, sys.maxsize)),
                                   ('No Arg Spec', (0, sys.maxsize))]:
            assert_args(self.find(lib, name), mina, maxa)

    def test_arguments_with_kwargs(self):
        lib = TestLibrary.from_name('classes.ArgDocDynamicLibraryWithKwargsSupport')
        for name, (mina, maxa) in [('No Arg', (0, 0)),
                                   ('One Arg', (1, 1)),
                                   ('One or Two Args', (1, 2)),
                                   ('Many Args', (0, sys.maxsize))]:
            assert_args(self.find(lib, name), mina, maxa)
        for name, (mina, maxa) in [('Kwargs', (0, 0)),
                                   ('Varargs and Kwargs', (0, sys.maxsize)),
                                   ('No Arg Spec', (0, sys.maxsize))]:
            assert_args(self.find(lib, name), mina, maxa, kwargs=True)


def assert_args(kw, minargs=0, maxargs=0, kwargs=False):
    assert_equal(kw.args.minargs, minargs)
    assert_equal(kw.args.maxargs, maxargs)
    assert_equal(bool(kw.args.var_named), kwargs)


class TestDynamicLibraryIntroDocumentation(unittest.TestCase):

    def test_doc_from_class_definition(self):
        self._assert_intro_doc('dynlibs.StaticDocsLib', 'This is lib intro.')

    def test_doc_from_dynamic_method(self):
        self._assert_intro_doc('dynlibs.DynamicDocsLib', 'Dynamic intro doc.')

    def test_dynamic_doc_overrides_class_doc(self):
        self._assert_intro_doc('dynlibs.StaticAndDynamicDocsLib', 'dynamic override')

    def test_failure_in_dynamic_resolving_of_doc(self):
        lib = TestLibrary.from_name('dynlibs.FailingDynamicDocLib')
        assert_raises_with_msg(
            DataError,
            "Calling dynamic method 'get_keyword_documentation' failed: "
            "Failing in 'get_keyword_documentation' with '__intro__'.",
            getattr, lib, 'doc'
        )

    def _assert_intro_doc(self, name, expected_doc):
        assert_equal(TestLibrary.from_name(name).doc, expected_doc)


class TestDynamicLibraryInitDocumentation(unittest.TestCase):

    def test_doc_from_class_init(self):
        self._assert_init_doc('dynlibs.StaticDocsLib', 'Init doc.')

    def test_doc_from_dynamic_method(self):
        self._assert_init_doc('dynlibs.DynamicDocsLib', 'Dynamic init doc.')

    def test_dynamic_doc_overrides_method_doc(self):
        self._assert_init_doc('dynlibs.StaticAndDynamicDocsLib', 'dynamic override')

    def test_failure_in_dynamic_resolving_of_doc(self):
        init = TestLibrary.from_name('dynlibs.FailingDynamicDocLib').init
        assert_raises(DataError, getattr, init, 'doc')

    def _assert_init_doc(self, name, expected_doc):
        assert_equal(TestLibrary.from_name(name).init.doc, expected_doc)


class TestSourceAndLineno(unittest.TestCase):

    def test_class(self):
        lib = TestLibrary.from_name('classes.NameLibrary')
        self._verify(lib, classes_source, 10)

    def test_class_in_package(self):
        from robot.variables.variables import __file__ as source
        lib = TestLibrary.from_name('robot.variables.Variables')
        self._verify(lib, source, 24)

    def test_dynamic(self):
        lib = TestLibrary.from_name('classes.ArgDocDynamicLibrary')
        self._verify(lib, classes_source, 215)

    def test_module(self):
        from module_library import __file__ as source
        lib = TestLibrary.from_name('module_library')
        self._verify(lib, source, 1)

    def test_package(self):
        from robot.variables import __file__ as source
        lib = TestLibrary.from_name('robot.variables')
        self._verify(lib, source, 1)

    def test_decorated(self):
        lib = TestLibrary.from_name('classes.Decorated')
        self._verify(lib, classes_source, 322)

    def test_no_class_statement(self):
        lib = TestLibrary.from_name('classes.NoClassDefinition')
        self._verify(lib, classes_source, 1)

    def _verify(self, lib, source, lineno):
        if source:
            source = re.sub(r'(\.pyc|\$py\.class)$', '.py', source)
            source = Path(os.path.normpath(source))
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
            raise DataError(f"Non-existing variable '{variable}'")
    def __setitem__(self, key, value):
        self.variables.__setitem__(key, value)
    def __getitem__(self, key):
        return self.variables.get(key)


class _FakeOutput:
    def trace(self, str, write_if_flat=True):
        pass
    def log_output(self, output):
        pass


class _FakeAsynchronous:
    def is_loop_required(self, obj):
        return False


class _FakeContext:
    def __init__(self):
        self.output = _FakeOutput()
        self.namespace = _FakeNamespace()
        self.dry_run = False
        self.in_teardown = False
        self.variables = _FakeVariableScope()
        self.timeouts = set()
        self.test = None
        self.asynchronous = _FakeAsynchronous()


if __name__ == '__main__':
    unittest.main()
