import unittest

from robot.result.builders import _get_webcontent_file,\
    _get_file_content_from_robot
from robot.utils.asserts import assert_true, assert_raises, assert_equals


class TestRobotFileReading(unittest.TestCase):

    def test_get_file(self):
        log = _get_file_content_from_robot('robot/webcontent/log.html')
        assert_true(len(log) > 1)

    def test_get_webcontent_file(self):
        log = _get_webcontent_file('log.html')
        assert_true(len(log) > 1)

    def test_lines_have_line_breaks(self):
        log = _get_webcontent_file('log.html')
        for line in log:
            assert_equals(line[-1], '\n')

    def test_get_non_existing(self):
        assert_raises(IOError, _get_webcontent_file, 'non_existing.html')
        assert_raises(IOError, _get_file_content_from_robot, 'non_existing.html')

    def test_path_must_be_unixy(self):
        assert_raises(IOError, _get_webcontent_file, 'testdata\\data.js')
        assert_raises(IOError, _get_file_content_from_robot, 'robot\\webcontent\\log.html')

    def test_path_must_be_relative(self):
        assert_raises(IOError, _get_file_content_from_robot, '/robot/webcontent/log.html')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()