import unittest
from robot.running.runerrors import SuiteRunErrors
from robot.utils.asserts import assert_true, assert_false
from robot.errors import ExecutionFailed


class TestSuiteRunErrors(unittest.TestCase):

    def setUp(self):
        self.errs = SuiteRunErrors()
        self.errs.start_suite()

    def test_errorless_suite_run(self):
        self._setup_and_teardown_allowed()

    def test_suite_run_with_errors(self):
        self.errs.suite_initialized('Awfulness happened!')
        self._setup_and_teardown_disallowed()

    def test_teardown_executed_after_setup_errs(self):
        self.errs.setup_executed(ExecutionFailed('Terriblesness occured!'))
        self.errs.setup_executed()
        assert_true(self.errs.is_suite_teardown_allowed())

    def test_higher_level_setup_err_prevents_all_lower_level_setups(self):
        self.errs.setup_executed(ExecutionFailed('Terriblesness occured!'))
        self.errs.start_suite()
        self._setup_and_teardown_disallowed()
        self.errs.end_suite()
        self.errs.start_suite()
        self._setup_and_teardown_disallowed()
        self.errs.end_suite()

    def test_higher_level_init_err_prevents_lower_level_setup(self):
        self.errs.suite_initialized('Terriblesness occured!')
        self.errs.start_suite()
        self._setup_and_teardown_disallowed()

    def test_sibling_errors_dont_affect_each_other(self):
        self.errs.start_suite()
        self.errs.setup_executed(ExecutionFailed('Terriblesness occured!'))
        self.errs.start_suite()
        self._setup_and_teardown_disallowed()
        self.errs.end_suite()
        self.errs.end_suite()
        self.errs.start_suite()
        self._setup_and_teardown_allowed()

    def test_fatal_error(self):
        self.errs.start_suite()
        self.errs.test_failed(exit=True)
        self.errs.end_suite()
        self.errs.start_suite()
        assert_false(self.errs.is_suite_setup_allowed())
        assert_false(self.errs.is_suite_setup_allowed())

    def test_teardown_is_run_after_setup_called(self):
        self.errs.start_suite()
        self.errs.setup_executed()
        self.errs.test_failed(exit=True)
        assert_true(self.errs.is_suite_teardown_allowed())

    def _setup_and_teardown_allowed(self):
        assert_true(self.errs.is_suite_setup_allowed())
        self.errs.setup_executed()
        assert_true(self.errs.is_suite_teardown_allowed())

    def _setup_and_teardown_disallowed(self):
        assert_false(self.errs.is_suite_setup_allowed())
        assert_false(self.errs.is_suite_teardown_allowed())


if __name__ == '__main__':
    unittest.main()
