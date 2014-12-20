import unittest
import sys

from robot.utils.frange import frange
from robot.utils.asserts import assert_equals


class TestFrangeUtils(unittest.TestCase):

    def test_frange(self):
        for input, expected in [([7.01],[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]),
                                ([3.14],[0.0, 1.0, 2.0, 3.0]),
                                ([-2.4, 6.1],[-2.4, -1.4, -0.4, 0.6, 1.6, 2.6, 3.6, 4.6, 5.6]),
                                ([1.3, 7.8],[1.3, 2.3, 3.3, 4.3, 5.3, 6.3, 7.3]),
                                ([1.205e20, 1.205e21, 1.205e20],[1.205e20, 2.41e20, 3.615e20, 4.82e20, 6.025e20, 7.23e20, 8.435e20, 9.64e20, 1.0845e21]),
                                ([1.205e-6, 1.205e-5, 1.205e-6],[1.205e-6, 2.41e-6, 3.615e-6, 4.82e-6, 6.025e-6, 7.23e-6, 8.435e-6, 9.64e-6, 1.0845e-5]),
                                ([-5.0145, 12.2132, 3.999],[-5.0145, -1.0155, 2.9835, 6.9825, 10.9815]),
                                ([0.1, 11.2, 4.6],[0.1, 4.7, 9.3])]:
            assert_equals(frange(*input), expected)
    
    def test_integers_only(self):
        for input in [(10,), (-10,), (1, 10), (1, 10, 2), (10, -5, -2)]:
            assert_equals(frange(*input), range(*input))

if __name__ == "__main__":
    unittest.main()
