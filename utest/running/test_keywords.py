import unittest
import sys
    
from robot.errors import DataError, ExecutionFailed
from robot.parsing.keywords import SetKeyword as SetKeywordData
from robot.parsing.keywords import RepeatKeyword as RepeatKeywordData
from robot.running.timeouts import KeywordTimeout
from robot.running.keywords import Keyword, SetKeyword, RepeatKeyword
from robot.utils.asserts import *
from test_testlibrary import _MockNamespace


class LoggerStub:
    
    def __getattr__(self, name):
        def accept_all(*args, **kwargs):
            pass
        return accept_all


class MockHandler:

    type = 'mock'
    
    def __init__(self, name='Mock Handler', doc='Mock Doc', error=False):
        self.name = self.longname = name
        self.doc = self.shortdoc = doc
        self.error = error
        self.timeout = KeywordTimeout()
        
    def run(self, output, namespace, args):
        """Sets given args to self.ags and optionally returns something.
        
        Returning works so that if two args are given and the first one is
        string 'return' (case insensitive) the second argument is returned.
        """
        if self.error:
            raise DataError
        self.args = args
        if len(args) == 2 and args[0].lower() == 'return':
            return args[1]


class MockNamespace(_MockNamespace):
    
    def __init__(self, error=False):
        _MockNamespace.__init__(self)
        self.error = error
    
    def get_handler(self, kwname):
        return MockHandler('Mocked.'+kwname, error=self.error)


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
        assert_raises(ExecutionFailed, kw.run, LoggerStub(), MockNamespace(error=True))
        
    def _verify_run(self, args):
        kw = Keyword('handler_name', args)
        assert_equals(kw.name, 'handler_name')
        assert_equals(kw.args, args)
        kw.run(LoggerStub(), MockNamespace())
        assert_equals(kw.name, 'Mocked.handler_name')
        assert_equals(kw.doc, 'Mock Doc')
        assert_equals(kw.handler_name, 'handler_name')


class TestSetKeyword(unittest.TestCase):
    
    def test_init_one_scalar_var(self):
        skw = SetKeyword(SetKeywordData(['${var}','Set','x']))
        assert_equal(skw.name, 'Set')
        assert_equal(skw.scalar_vars, ['${var}'])
        assert_none(skw.list_var)
        assert_equal(skw.args, ['x'])
                
    def test_init_three_scalar_vars(self):
        skw = SetKeyword(SetKeywordData('${v1} ${v2} ${v3} Set x y z'.split()))
        assert_equal(skw.scalar_vars, ['${v1}','${v2}','${v3}'])
        assert_none(skw.list_var)
        assert_equal(skw.args, ['x','y','z'])
    
    def test_init_list_var(self):
        skw = SetKeyword(SetKeywordData(['@{list}','Set','x','y','z']))
        assert_equal(skw.scalar_vars, [])
        assert_equal(skw.list_var, '@{list}')
        assert_equal(skw.args, ['x','y','z'])
                
    def test_init_two_scalar_and_one_list_vars(self):
        skw = SetKeyword(SetKeywordData('${v1} ${v2} @{list} Set x y z'.split()))
        assert_equal(skw.scalar_vars, ['${v1}','${v2}'])
        assert_equal(skw.list_var, '@{list}')
        assert_equal(skw.args, ['x','y','z'])
                
    def test_init_no_vars_raises(self):
        assert_raises(TypeError, SetKeywordData, ['Set','a'])
        
    def test_init_list_in_wrong_place_raises(self):
        assert_raises(DataError, SetKeywordData, ['@{list}','${str}','Set','a'])
        
    def test_init_no_keyword_raises(self):
        assert_raises(DataError, SetKeywordData, ['${var}'])
    
    def test_set_string_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN','value']))
        namespace = MockNamespace()
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${var}'], 'value')

    def test_set_object_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN',self]))
        namespace = MockNamespace()
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${var}'], self)

    def test_set_empty_list_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN',[]]))
        namespace = MockNamespace()
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${var}'], [])

    def test_set_list_with_one_element_to_scalar(self):
        skw = SetKeyword(SetKeywordData(['${var}','KW','RETURN',['hi']]))
        namespace = MockNamespace()
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${var}'], ['hi'])

    def test_set_strings_to_three_scalars(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','${v3}','KW','RETURN',['x','y','z']]))
        namespace = MockNamespace()
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${v1}'], 'x')
        assert_equal(namespace.variables['${v2}'], 'y')
        assert_equal(namespace.variables['${v3}'], 'z')

    def test_set_objects_to_three_scalars(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','${v3}','KW','RETURN',[['x','y'],{},None]]))
        namespace = MockNamespace()        
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${v1}'], ['x','y'])
        assert_equal(namespace.variables['${v2}'], {})
        assert_equal(namespace.variables['${v3}'], None)

    def test_set_list_of_strings_to_list(self):
        skw = SetKeyword(SetKeywordData(['@{var}','KW','RETURN',['x','y','z']]))
        namespace = MockNamespace()        
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['@{var}'], ['x','y','z'])

    def test_set_empty_list_to_list(self):
        skw = SetKeyword(SetKeywordData(['@{var}','KW','RETURN',[]]))
        namespace = MockNamespace()        
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['@{var}'], [])

    def test_set_objects_to_two_scalars_and_list(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','@{v3}','KW','RETURN',['a',None,'x','y',{}]]))
        namespace = MockNamespace()        
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${v1}'], 'a')
        assert_equal(namespace.variables['${v2}'], None)
        assert_equal(namespace.variables['@{v3}'], ['x','y',{}])

    def test_set_scalars_and_list_so_that_list_is_empty(self):
        skw = SetKeyword(SetKeywordData(['${scal}','@{list}','KW','RETURN',['a']]))
        namespace = MockNamespace()        
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${scal}'], 'a')
        assert_equal(namespace.variables['@{list}'], [])

    def test_set_more_values_than_variables(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','KW','RETURN',['x','y','z']]))
        namespace = MockNamespace()        
        skw.run(LoggerStub(), namespace)
        assert_equal(namespace.variables['${v1}'], 'x')
        assert_equal(namespace.variables['${v2}'], ['y','z'])

    def test_set_too_few_scalars_raises(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','KW','RETURN',['x']]))
        assert_raises(ExecutionFailed, skw.run, LoggerStub(), MockNamespace())

    def test_set_list_but_no_list_raises(self):
        skw = SetKeyword(SetKeywordData(['@{list}','KW','RETURN','not a list']))
        assert_raises(ExecutionFailed, skw.run, LoggerStub(), MockNamespace())

    def test_set_too_few_scalars_with_list_raises(self):
        skw = SetKeyword(SetKeywordData(['${v1}','${v2}','@{list}','KW','RETURN',['x']]))
        assert_raises(ExecutionFailed, skw.run, LoggerStub(), MockNamespace())


        
class TestRepeatKeyword(unittest.TestCase):
    
    def test_init_valid(self):
        for repeat in ['10 x', '10 X', '10x', '10X', '10  x', '10      X']:
            data = [repeat,'Log','hello']
            rkw = RepeatKeywordData(data)
            assert_equal(rkw.repeat, 10)
            
    def test_init_with_zero_and_negative_repeat(self):
        for repeat in ['0 x', '-1 X', '-1111X', '-42                      X']:
            data = [repeat,'Log','hello']
            rkw = RepeatKeywordData(data)
            assert_equal(rkw.repeat, int(repeat[:-1].strip()))

    def test_init_no_repeat(self):
        assert_raises(TypeError, RepeatKeywordData, ['Log','hello'])
        
    def test_init_no_keyword(self):
        assert_raises(DataError, RepeatKeywordData, ['10 x'])

    def test_init_invalid_repeat(self):
        for repeat in ['Foo x', '10.0 X', '10y', '10Z', '10 xx', 'xxx', 'X', 'x']:
            assert_raises(TypeError, RepeatKeywordData, [repeat,'Log','hello'])

    def test_repeat_with_variable(self):        
        for repeat, var in [('${var} x',4), ('${var} X','4'), ('${4}x',None)]:
            rkw = RepeatKeyword(RepeatKeywordData([repeat,'Log','hello']))
            namespace = MockNamespace()
            if var is not None:
                namespace.variables['${var}'] = var
            rkw.run(LoggerStub(), namespace)
            assert_equal(rkw._repeat, 4)
            assert_equal(rkw._orig_repeat, repeat[:-1].strip())
            assert_equal(rkw.name, '4x Mocked.Log')
            
    def test_repeat_with_variable_using_different_values(self):
        variable = '${var}'
        rkw = RepeatKeyword(RepeatKeywordData([variable+' X','Log','hello']))
        namespace = MockNamespace()
        for value in [ -123, '-1', 0, '0', 3, '42' ]:
            namespace.variables[variable] = value
            exp_repeat = int(value)
            rkw.run(LoggerStub(), namespace)
            assert_equal(rkw._repeat, exp_repeat, 'Wrong repeat returned')
            assert_equal(rkw._orig_repeat, variable, 'Wrong self.repeat')
            assert_equal(rkw.name, str(exp_repeat) + 'x Mocked.Log', 'Wrong name')
        
    def test_repeat_with_non_existing_variable(self):        
        rkw = RepeatKeyword(RepeatKeywordData(['${non_existing} x','Log','hello']))
        assert_raises(ExecutionFailed, rkw.run, LoggerStub(), MockNamespace())
        assert_equal(rkw.name, '${non_existing}x Mocked.Log')

    def test_repeat_with_non_integer_variable(self):        
        rkw = RepeatKeyword(RepeatKeywordData(['${non_int} x','Log','hello']))
        namespace = MockNamespace()
        namespace.variables['${non_int}'] = 'xxx'
        assert_raises(ExecutionFailed, rkw.run, LoggerStub(), namespace)
        assert_equal(rkw.name, '${non_int}x Mocked.Log')
        
        
if __name__ == '__main__':
    unittest.main()
