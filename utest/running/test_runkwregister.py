import unittest
import warnings

from robot.utils.asserts import assert_equal, assert_true

from robot.running.runkwregister import _RunKeywordRegister as Register


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

    def setUp(self):
        self.reg = Register()

    def register_run_keyword(self, libname, keyword, args_to_process=None):
        self.reg.register_run_keyword(libname, keyword, args_to_process,
                                      deprecation_warning=False)

    def test_register_run_keyword_method_with_kw_name_and_arg_count(self):
        self._verify_reg('My Lib', 'myKeyword', 'My Keyword', 3, 3)

    def test_get_arg_count_with_non_existing_keyword(self):
        assert_equal(self.reg.get_args_to_process('My Lib', 'No Keyword'), -1)

    def test_get_arg_count_with_non_existing_library(self):
        self._verify_reg('My Lib', 'get_arg', 'Get Arg', 3, 3)
        assert_equal(self.reg.get_args_to_process('No Lib', 'Get Arg'), -1)

    def _verify_reg(self, lib_name, keyword, keyword_name, arg_count, given_count):
        self.register_run_keyword(lib_name, keyword, given_count)
        assert_equal(self.reg.get_args_to_process(lib_name, keyword_name), arg_count)

    def test_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as w:
            self.reg.register_run_keyword('Library', 'Keyword', 0)
        [warning] = w
        assert_equal(
            str(warning.message),
            "The API to register run keyword variants and to disable variable resolving "
            "in keyword arguments will change in the future. For more information see "
            "https://github.com/robotframework/robotframework/issues/2190. "
            "Use with `deprecation_warning=False` to avoid this warning."
        )
        assert_true(issubclass(warning.category, UserWarning))


if __name__ == '__main__':
    unittest.main()
