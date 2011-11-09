import unittest

from robot.errors import DataError
from robot.output.loggerhelper import AbstractLogger


class TestAbstractLogger(unittest.TestCase):

    def test_set_invalid_threshold(self):
        logger = AbstractLogger('trace')
        self.assertRaises(DataError, logger.set_level,'INVALID THRESHOLD')


if __name__ == '__main__':
    unittest.main()
