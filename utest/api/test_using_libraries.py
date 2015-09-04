import unittest

from robot.utils.asserts import assert_raises_with_msg
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError


class TestBuiltInWhenRobotNotRunning(unittest.TestCase):

    def test_using_namespace(self):
        assert_raises_with_msg(RobotNotRunningError,
                               'Cannot access execution context',
                               BuiltIn().get_variables)

    def test_using_namespace_backwards_compatibility(self):
        assert_raises_with_msg(AttributeError,
                               'Cannot access execution context',
                               BuiltIn().get_variables)

    def test_suite_doc_and_metadata(self):
        assert_raises_with_msg(RobotNotRunningError,
                               'Cannot access execution context',
                               BuiltIn().set_suite_documentation, 'value')
        assert_raises_with_msg(RobotNotRunningError,
                               'Cannot access execution context',
                               BuiltIn().set_suite_metadata, 'name', 'value')


if __name__ == '__main__':
    unittest.main()
