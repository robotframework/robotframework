import unittest

from robot.utils.frange import frange, _digits
from robot.utils.asserts import assert_equals, assert_true, assert_raises


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

    def test_compatibility_with_range(self):
        for input in [(10,), (-10,), (1, 10), (1, 10, 2), (10, -5, -2)]:
            assert_equals(frange(*input), range(*input))
            assert_equals(frange(*(float(i) for i in input)), range(*input))

    def test_preserve_type(self):
        for input in [(2,), (0, 2), (0, 2, 1)]:
            assert_true(all(isinstance(item, int) for item in frange(*input)))
        for input in [(2.0,), (0, 2.0), (0.0, 2), (0, 2, 1.0), (0, 2.0, 1)]:
            assert_true(all(isinstance(item, float) for item in frange(*input)))

    def test_invalid_args(self):
        assert_raises(TypeError, frange, ())
        assert_raises(TypeError, frange, (1, 2, 3, 4))

    def test_digits(self):
        for input, expected in [(3, 0),
                                (3.0, 0),
                                (3.1, 1),
                                (3.14, 2),
                                (3.141592653589793, len('141592653589793')),
                                (1000.1000, 1),
                                (-2.458, 3),
                                (1e50, 0),
                                (1.23e50, 0),
                                (1e-50, 50),
                                (1.23e-50, 52),
                                # using strings to avoid Python converting
                                # e.g. 1.23e3 -> 1230.0
                                ('1.23e3', 0),
                                ('1.23e2', 0),
                                ('1.23e1', 1),
                                ('1.23e0', 2),
                                ('1.23e-1', 3),
                                ('1.23e-2', 4)]:
            assert_equals(_digits(input), expected, input)


if __name__ == "__main__":
    unittest.main()
