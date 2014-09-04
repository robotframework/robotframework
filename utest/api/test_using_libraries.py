import unittest

from robot.utils.asserts import assert_raises_with_msg
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError


class TestBuiltIn(unittest.TestCase):

    def test_using_namespace_when_robot_not_running(self):
        assert_raises_with_msg(RobotNotRunningError,
                               'Cannot access execution context',
                               BuiltIn().get_variables)

    def test_using_namespace_when_robot_not_running_backwards_compatibility(self):
        assert_raises_with_msg(AttributeError,
                               'Cannot access execution context',
                               BuiltIn().get_variables)


if __name__ == '__main__':
    unittest.main()
