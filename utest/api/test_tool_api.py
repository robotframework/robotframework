import unittest

from robot.utils.asserts import assert_true


class TestRunningAPI(unittest.TestCase):

    def test_namespace_reference(self):
        from robot.running import EXECUTION_CONTEXTS
        from robot.running.context import _ExecutionContext
        assert_true(EXECUTION_CONTEXTS.current is None)
        assert_true(_ExecutionContext(object(), None).namespace is not None)
