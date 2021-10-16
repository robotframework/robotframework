import io
import sys
import unittest

from robot.utils import isatty
from robot.utils.asserts import assert_equal, assert_false, assert_raises


class TestIsATty(unittest.TestCase):

    def test_with_stdout_and_stderr(self):
        assert_equal(isatty(sys.__stdout__), sys.__stdout__.isatty())
        assert_equal(isatty(sys.__stderr__), sys.__stderr__.isatty())

    def test_with_io(self):
        with io.StringIO() as stream:
            assert_false(isatty(stream))
            wrapper = io.TextIOWrapper(stream, 'UTF-8')
            assert_false(isatty(wrapper))

    def test_with_detached_io_buffer(self):
        with io.StringIO() as stream:
            wrapper = io.TextIOWrapper(stream, 'UTF-8')
            wrapper.detach()
            assert_raises((ValueError, AttributeError), wrapper.isatty)
            assert_false(isatty(wrapper))

    def test_open_and_closed_file(self):
        with open(__file__) as file:
            assert_false(isatty(file))
        assert_false(isatty(file))


if __name__ == '__main__':
    unittest.main()
