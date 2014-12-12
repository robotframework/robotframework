import unittest
import sys

from robot.utils.frange import frange
from robot.utils.asserts import assert_equals


class TestFrangeUtils(unittest.TestCase):

    def test_frange(self):
        for input, expected in [([7],[0, 1, 2, 3, 4, 5, 6]),
                                ([3.14],[0, 1.0, 2.0, 3.0]),
                                ([1,7],[1, 2, 3, 4, 5, 6]),
                                ([1.3,7.8],[1.3, 2.3, 3.3, 4.3, 5.3, 6.3, 7.3]),
                                ([1,12,3],[1, 4, 7, 10]),
                                ([0.1,11.2,4.6],[0.1, 4.7, 9.3])]:
            assert_equals(frange(*input), expected)


if __name__ == "__main__":
    unittest.main()
