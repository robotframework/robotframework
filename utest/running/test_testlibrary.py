import unittest
import sys
    
from robot.running.testlibraries import TestLibrary, _ClassLibrary, \
        _ModuleLibrary, _DynamicLibrary
from robot.utils.asserts import *
from robot import utils
from robot.errors import DataError

from classes import NameLibrary, DocLibrary, ArgInfoLibrary, GetattrLibrary, \
        SynonymLibrary
if utils.is_jython:
    import ArgumentTypes, Extended, MultipleArguments, MultipleSignatures, NoHandlers


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
        assert_equals(lib.__class__, _ClassLibrary)
        assert_equals(lib.positional_args, [])
        
    def test_python_library_with_args(self):
        lib = TestLibrary("ParameterLibrary", ['my_host', '8080'])
        assert_equals(lib.__class__, _ClassLibrary)
        assert_equals(lib.positional_args, ['my_host', '8080'])
        
    def test_module_library(self):
        lib = TestLibrary("module_library")
        assert_equals(lib.__class__, _ModuleLibrary)
        
    def test_module_library_with_args(self):
        assert_raises(DataError, TestLibrary, "module_library", ['arg'] )
        
    def test_dynamic_python_library(self):
        lib = TestLibrary("RunKeywordLibrary")
        assert_equals(lib.__class__, _DynamicLibrary)
        
    if utils.is_jython:
        def test_java_library(self):
            lib = TestLibrary("ExampleJavaLibrary")
            assert_equals(lib.__class__, _ClassLibrary)
            

class TestImports(unittest.TestCase):
        
    def test_import_python_class(self):
        lib = TestLibrary("BuiltIn")
        self._verify_lib(lib, "BuiltIn", default_keywords)
            
    def test_import_python_class_from_module(self):
        lib = TestLibrary("BuiltIn.BuiltIn")
        self._verify_lib(lib, "BuiltIn.BuiltIn", default_keywords)
        
    def test_import_python_module(self):
        lib = TestLibrary("module_library")
        kws = ["passing", "two arguments from class", "lambdakeyword", "argument"]
        self._verify_lib(lib, "module_library", [ (kw, None) for kw in kws ])
        
    def test_import_python_module_from_module(self):
        lib = TestLibrary("pythonmodule.library")
        self._verify_lib(lib, "pythonmodule.library", 
                         [("keyword from submodule", None)])
        
    def test_import_non_existing_module(self):
        exp = ("Importing test library '%s' failed: " 
               "ImportError: No module named %s\nPYTHONPATH:")
        for name in 'nonexisting', 'nonexi.sting':
            try:
                TestLibrary(name)
            except DataError, err:
                module = name.split('.')[0]
                assert_true(str(err).startswith(exp % (name, module)), err)
            else:
                raise AssertionError("DataError not raised")
    
    def test_import_non_existing_class_from_existing_module(self):
        msg = "Test library module 'pythonmodule' does not contain 'NonExisting'"
        assert_raises_with_msg(DataError, msg, 
                               TestLibrary, 'pythonmodule.NonExisting')
        
    def test_import_invalid_type(self):
        msg = "Imported test library is not a class or module, got '%s' instead"
        assert_raises_with_msg(DataError, msg % 'StringType', 
                               TestLibrary, 'pythonmodule.some_string')
        assert_raises_with_msg(DataError, msg % 'InstanceType', 
                               TestLibrary, 'pythonmodule.some_object')

    def test_import_with_unicode_name(self):
        self._verify_lib(TestLibrary(u"BuiltIn"), "BuiltIn", default_keywords)
        self._verify_lib(TestLibrary(u"BuiltIn.BuiltIn"), "BuiltIn.BuiltIn", default_keywords)
        self._verify_lib(TestLibrary(u"pythonmodule.library"), "pythonmodule.library", 
                         [("keyword from submodule", None)])
    
    def test_set_global_scope(self):
        assert_equals(TestLibrary('libraryscope.Global').scope, 'GLOBAL')
        
    def test_set_suite_scope(self): 
        assert_equals(TestLibrary('libraryscope.Suite').scope, 'TESTSUITE')

    def test_set_test_scope(self): 
        assert_equals(TestLibrary('libraryscope.Test').scope, 'TESTCASE')
        
    def test_set_invalid_scope(self):
        for libname in ['libraryscope.InvalidValue', 
                        'libraryscope.InvalidEmpty',
                        'libraryscope.InvalidMethod', 
                        'libraryscope.InvalidNone']:
            lib = TestLibrary(libname)
            assert_equals(lib.scope, 'TESTCASE')
            
    if utils.is_jython:
        
        def test_import_java(self):
            lib = TestLibrary("ExampleJavaLibrary")
            self._verify_lib(lib, "ExampleJavaLibrary", java_keywords)
            
        def test_import_java_with_dots(self):
            lib = TestLibrary("javapkg.JavaPackageExample")
            self._verify_lib(lib, "javapkg.JavaPackageExample", java_keywords)
            
        def test_set_global_scope_java(self):
            lib = TestLibrary('javalibraryscope.Global')
            assert_equals(lib.scope, 'GLOBAL')

        def test_set_suite_scope_java(self):
            lib = TestLibrary('javalibraryscope.Suite')
            assert_equals(lib.scope, 'TESTSUITE')
    
        def test_set_test_scope_java(self):
            lib = TestLibrary('javalibraryscope.Test')
            assert_equals(lib.scope, 'TESTCASE')
            
        def test_set_invalid_scope_java(self):
            for libname in [ 'javalibraryscope.InvalidEmpty', 
                             'javalibraryscope.InvalidMethod', 
                             'javalibraryscope.InvalidNull', 
                             'javalibraryscope.InvalidPrivate',
                             'javalibraryscope.InvalidProtected',
                             'javalibraryscope.InvalidValue' ]:
                lib = TestLibrary(libname)
                assert_equals(lib.scope, 'TESTCASE')
            
    def _verify_lib(self, lib, libname, keywords):
        assert_equals(libname, lib.name)
        for name, _ in keywords:
            handler = lib.get_handler(name)
            exp = "%s.%s" % (libname, name)
            assert_equals(utils.normalize(handler.longname), 
                          utils.normalize(exp))


class TestLibraryInit(unittest.TestCase):
    
    def test_python_library_without_init(self):
        self._test_init_handler('ExampleLibrary')
        
    def test_python_library_with_init(self):
        self._test_init_handler('ParameterLibrary', ['foo'], 0, 2)
        
    def test_new_style_class_without_init(self):
        self._test_init_handler('newstyleclasses.NewStyleClassLibrary')
        
    def test_new_style_class_with_init(self):
        lib = self._test_init_handler('newstyleclasses.NewStyleClassArgsLibrary', ['value'], 1, 1)
        assert_equals(len(lib.handlers), 1)
        
    def test_library_with_metaclass(self):
        self._test_init_handler('newstyleclasses.MetaClassLibrary')
    
    def _test_init_handler(self, libname, args=None, min=0, max=0):
        lib = TestLibrary(libname, args)
        assert_equals(lib.init.minargs, min)
        assert_equals(lib.init.maxargs, max)
        return lib
    
    if utils.is_jython:
        
        def test_java_library_without_constructor(self):
            self._test_init_handler('ExampleJavaLibrary', None, 0, 0)
            
        def test_java_library_with_constructor(self):
            self._test_init_handler('JavaVarArgsConstructor', ['arg1', 'arg2'], 1, 3)
            
        def test_extended_java_lib_with_no_init_and_no_constructor(self):
            self._test_init_handler('extendingjava.ExtendJavaLib', None, 0, 0)
            
        def test_extended_java_lib_with_no_init_and_contructor(self):
            self._test_init_handler('extendingjava.ExtendJavaLibWithConstructor', ['arg'], 1, 3)
            
        def test_extended_java_lib_with_init_and_no_constructor(self):
            self._test_init_handler('extendingjava.ExtendJavaLibWithInit', [1,2,3], 0, sys.maxint)
            
        def test_extended_java_lib_with_init_and_constructor(self):
            self._test_init_handler('extendingjava.ExtendJavaLibWithInitAndConstructor', ['arg'], 0, sys.maxint)
           
            
class TestVersion(unittest.TestCase):
    
    def test_version_of_python_libarary(self):
        self._test_version('classes.VersionLibrary', '0.1')
        self._test_version('classes.VersionObjectLibrary', 'ver')
        
    def test_version_with_no_version_info_defined(self):
        self._test_version('classes.NameLibrary', '<unknown>')
        
    def test_version_of_module_library(self):
        self._test_version('module_library', 'test')

    def _test_version(self, name, version):
        lib = TestLibrary(name)
        assert_equals(lib.version, version)
        
    if utils.is_jython:
        
        def test_version_of_java_library(self):
            self._test_version('JavaVersionLibrary', '1.0')
            
        def test_version_of_java_library_with_no_version_defined(self):
            self._test_version('ExampleJavaLibrary', '<unknown>')
        

class _TestScopes(unittest.TestCase):
    
    def _get_lib_and_instance(self, name):
        lib = TestLibrary(name)
        if lib.scope == 'GLOBAL':
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
        for lib in [ NameLibrary, DocLibrary, ArgInfoLibrary, GetattrLibrary,
                     SynonymLibrary ]:
            testlib = TestLibrary('classes.%s' % lib.__name__)
            handlers = testlib.handlers.values()
            assert_equals(lib.handler_count, len(handlers), lib.__name__)
            for handler in handlers:
                assert_false(handler._handler_name.startswith('_'))
                assert_equals(handler._handler_name.count('skip'), 0)
                
    def test_non_global_dynamic_handlers(self):
        lib = TestLibrary("RunKeywordLibrary")
        assert_equals(len(lib.handlers), 2)
        assert_true(lib.handlers.has_key('Run Keyword That Passes'))
        assert_true(lib.handlers.has_key('Run Keyword That Fails'))
        assert_none(lib.handlers['Run Keyword That Passes']._method)
        assert_none(lib.handlers['Run Keyword That Fails']._method)
        
    def test_global_dynamic_handlers(self):
        lib = TestLibrary("RunKeywordLibrary.GlobalRunKeywordLibrary")
        assert_equals(len(lib.handlers), 2)
        for name in 'Run Keyword That Passes', 'Run Keyword That Fails':
            handler = lib.handlers[name]
            assert_not_none(handler._method)
            assert_not_equals(handler._method, lib._libinst.run_keyword)
            assert_equals(handler._method.__name__, 'handler')
                
    def test_synonym_handlers(self):
        testlib = TestLibrary('classes.SynonymLibrary')
        names = [ 'handler', 'synonym_handler', 'another_synonym' ]
        for handler in testlib.handlers.values():
            # test 'handler_name' -- raises ValueError if it isn't in 'names'
            names.remove(handler._handler_name)
        assert_equals(len(names), 0, 'handlers %s not created' % names, False)
        
    def test_global_handlers_are_created_only_once(self):
        lib = TestLibrary('classes.RecordingLibrary')
        calls_after_init = lib._libinst.calls_to_getattr
        for _ in range(5): 
            lib.handlers['kw'].run(_FakeOutput(), _FakeNamespace(), [])
        assert_equals(lib._libinst.calls_to_getattr, calls_after_init)
                    
    if utils.is_jython:

        def test_get_java_handlers(self):
            for lib in [ ArgumentTypes, 
                         MultipleArguments,
                         MultipleSignatures, 
                         NoHandlers,
                         Extended ]:
                testlib = TestLibrary(lib.__name__)
                handlers = testlib.handlers.values()
                assert_equals(len(handlers), lib().handler_count, lib.__name__)
                for handler in handlers:
                    assert_false(handler._handler_name.startswith('_'))
                    assert_equals(handler._handler_name.count('skip'), 0)


class TestDynamicLibrary(unittest.TestCase):
    
    def test_get_keyword_doc_is_used_if_present(self):
        lib = TestLibrary('classes.ArgDocDynamicLibrary')
        assert_equals(lib.handlers['No Arg'].doc, 'Keyword documentation for No Arg')

    def test_get_keyword_doc_and_args_are_ignored_if_not_callable(self):
        lib = TestLibrary('classes.InvalidAttributeDynamicLibrary')
        assert_equals(len(lib.handlers), 4)
        assert_equals(lib.handlers['No Arg'].doc, '')
        self._assert_handler_args(lib.handlers['No Arg'], 0, sys.maxint)
        
    def test_handler_is_not_created_if_get_keyword_doc_fails(self):
        lib = TestLibrary('classes.InvalidGetDocDynamicLibrary')
        assert_equals(len(lib.handlers), 0)

    def test_handler_is_not_created_if_get_keyword_args_fails(self):
        lib = TestLibrary('classes.InvalidGetArgsDynamicLibrary')
        assert_equals(len(lib.handlers), 0)

    def test_get_keyword_arguments_is_used_if_present(self):
        lib = TestLibrary('classes.ArgDocDynamicLibrary')
        for name, exp in [ ('No Arg', ()) , ('One Arg', (1,1)), 
                           ('One or Two Args', (1, 2)),
                           ('Many Args', (0, sys.maxint))]:
            self._assert_handler_args(lib.handlers[name], *exp)
            
    def _assert_handler_args(self, handler, minargs=0, maxargs=0):
        assert_equals(handler.minargs, minargs)
        assert_equals(handler.maxargs, maxargs)
        
    if utils.is_jython:
        def test_dynamic_java_handlers(self):
            lib = TestLibrary('ArgDocDynamicJavaLibrary')
            for name, min, max in [ ('Java No Arg', 0, 0), ('Java One Arg', 1, 1),
                                    ('Java One or Two Args', 1, 2), 
                                    ('Java Many Args', 0, sys.maxint) ]:
                self._assert_java_handler(lib.handlers[name], 
                                          'Keyword documentation for %s' % name, 
                                          min, max)
                
        def test_get_keyword_doc_and_args_are_ignored_if_not_callable_in_java(self):
            lib = TestLibrary('InvalidAttributeArgDocDynamicJavaLibrary')
            assert_equals(len(lib.handlers), 1)
            self._assert_handler_args(lib.handlers['keyword'], 0, sys.maxint)

        def test_handler_is_not_created_if_get_keyword_doc_fails_in_java(self):
            lib = TestLibrary('InvalidSignatureArgDocDynamicJavaLibrary')
            assert_equals(len(lib.handlers), 0)
            
        def _assert_java_handler(self, handler, doc, minargs, maxargs):
            assert_equals(handler.doc, doc)
            self._assert_handler_args(handler, minargs, maxargs)
    
        
class _FakeNamespace:
    def __init__(self):
        self.variables = _FakeVariableScope()
        self.uk_handlers = []
        self.test = None


class _FakeVariableScope:
    def __init__(self):
        self.variables = {}
    def replace_list(self, args):
        return []
    def replace_string(self, variable):
        try:
            var = variable.replace('$', '').replace('{', '').replace('}', '')
            return int(var)
        except:
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


if __name__ == '__main__':
    unittest.main()
