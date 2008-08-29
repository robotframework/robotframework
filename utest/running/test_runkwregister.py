import unittest

from robot.running.runkwregister import RUN_KW_REGISTER


class Lib:
    
    def method_without_arg(self):
        pass
    
    def method_with_one(self, name, *args):
        pass
    
    def method_with_default(self, one, two, three='default', *args):
        pass


def function_without_arg():
    pass

def function_with_one(name, *args):
    pass

def function_with_three(one, two, three, *args):
    pass


class TestRunKeywordRegister(unittest.TestCase):
    
    def test_register_run_keyword_method_with_kw_name_and_arg_count(self):
        self._test_registering('My Lib', 'myKeyword', 
                               'My Keyword', 3, 3)

    def test_register_run_keyword_method_with_kw_name_without_arg_count(self):
        self.assertRaises(ValueError, RUN_KW_REGISTER.register_run_keyword, 
                          'My Lib', 'my_keyword')
        
    def test_register_run_keyword_method_with_function_without_arg(self):
        self._test_registering('My Lib', function_without_arg, 
                               'Function Without Arg', 0)
    
    def test_register_run_keyword_method_with_function_with_one_arg(self):
        self._test_registering('My Lib', function_with_one, 
                               'Function With One', 1)


    def test_register_run_keyword_method_with_function_with_three_arg(self):
        self._test_registering('My Lib', function_with_three, 
                               'Function With Three', 3)

    def test_register_run_keyword_method_with_method_without_arg(self):
        self._test_registering('My Lib', Lib().method_without_arg, 
                               'Method Without Arg', 0)

    def test_register_run_keyword_method_with_method_with_one_arg(self):
        self._test_registering('My Lib', Lib().method_with_one, 
                               'Method With One', 1)


    def test_register_run_keyword_method_with_method_with_default_arg(self):
        self._test_registering('My Lib', Lib().method_with_default, 
                               'Method With Default', 3)

    def test_register_run_keyword_method_with_invalid_keyword_type(self):
        self.assertRaises(ValueError, RUN_KW_REGISTER.register_run_keyword, 
                          'My Lib', 1)
    
    def test_get_arg_count_with_non_existing_keyword(self):
        self.assertEqual(RUN_KW_REGISTER.get_args_to_process('My Lib', 'No Keyword'), -1)

    def test_get_arg_count_with_non_existing_library(self):
        self._test_registering('My Lib', 'get_arg', 
                               'Get Arg', 3, 3)
        self.assertEqual(RUN_KW_REGISTER.get_args_to_process('No Lib', 'Get Arg'), -1)

    
    def _test_registering(self, lib_name, keyword, keyword_name, arg_count, 
                          given_arg_count=None):
        if given_arg_count is None:
            RUN_KW_REGISTER.register_run_keyword(lib_name, keyword)
        else:
            RUN_KW_REGISTER.register_run_keyword(lib_name, keyword, given_arg_count)
        self.assertEqual(RUN_KW_REGISTER.get_args_to_process(lib_name, keyword_name), arg_count)

if __name__ == '__main__':
    unittest.main()
