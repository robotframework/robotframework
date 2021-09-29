import io
import sys
import unittest

from robot.utils import isatty
from robot.utils.asserts import assert_equal, assert_false, assert_raises
# Should be tested in own module but util only needed with Jython so can be here.
from robot.utils.platform import _version_to_tuple


class TestIsATty(unittest.TestCase):

    def test_with_stdout_and_stderr(self):
        # file class based in PY2, io module based in PY3
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


class TestPlatform(unittest.TestCase):

    def test_version_to_tuple(self):
        for inp, exp in [('1.2.3', (1, 2, 3)),
                         ('1.2.3-dev1', (1, 2, 3)),
                         ('192.168.0.1', (192, 168, 0)),
                         ('17', (17, 0, 0)),
                         ('18-ea', (18, 0, 0))]:
            assert_equal(_version_to_tuple(inp), exp)


if __name__ == '__main__':
    unittest.main()
