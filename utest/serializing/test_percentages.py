import os
import unittest
import sys

from robot.utils.asserts import assert_equals
from robot.serializing.statserializers import _Percents


class TestPercents(unittest.TestCase):

    def _verify_percents(self, input, expected):
        p = _Percents(*input)
        assert_equals(p.pass_percent, expected[0])
        assert_equals(p.fail_percent, expected[1])

    def test_calc_percents_zeros(self):
        self._verify_percents((0, 0), (0, 0))

    def test_calc_percents_below_limit(self):
        for in1, in2 in [ (1, 9999), (2, 9998), (9, 9991), (1244, 145431435) ]:
            self._verify_percents((in1, in2), (0.1, 99.9))
            self._verify_percents((in2, in1), (99.9, 0.1))

    def test_calc_percents_one_zero(self):
        for count in [ 1, 2, 10, 42, 100, 1234, 999999999 ]:
            self._verify_percents((count, 0), (100.0, 0))
            self._verify_percents((0, count), (0, 100.0))

    def test_calc_percents_same(self):
        for count in [ 1, 2, 10, 42, 100, 1234, 999999999 ]:
            self._verify_percents((count, count), (50.0, 50.0))

    def test_calc_percents_no_rounding(self):
        for in1, in2, ex1, ex2 in [ (3, 1, 75.0, 25.0),
                                    (99, 1, 99.0, 1.0),
                                    (999, 1, 99.9, 0.1),
                                    (87, 13, 87.0, 13.0),
                                    (601, 399, 60.1, 39.9),
                                    (857, 143, 85.7, 14.3) ]:
            self._verify_percents((in1, in2), (ex1, ex2))
            self._verify_percents((in2, in1), (ex2, ex1))

    def test_calc_percents_rounding(self):
        for in1, in2, ex1, ex2 in [ (2, 1, 66.7, 33.3),
                                    (6, 1, 85.7, 14.3),
                                    (3, 8, 27.3, 72.7),
                                    (5, 4, 55.6, 44.4),
                                    (28, 2, 93.3, 6.7),
                                    (70, 1, 98.6, 1.4),
                                    (999, 2, 99.8, 0.2),
                                    (7778, 2222, 77.8, 22.2) ]:
            self._verify_percents((in1, in2), (ex1, ex2))
            self._verify_percents((in2, in1), (ex2, ex1))

    def test_calc_percents_rounding_both_up(self):
        for in1, in2, ex1, ex2 in [ (3, 13, 18.8, 81.3),
                                    (105, 9895, 1.1, 99.0),
                                    (4445, 5555, 44.5, 55.6) ]:
            self._verify_percents((in1, in2), (ex1, ex2))
            self._verify_percents((in2, in1), (ex2, ex1))


class TestWidths(unittest.TestCase):

    def _verify_percentages_to_widths(self, inp1, inp2, exp1=None, exp2=None):
        act1, act2 = _Percents(0, 0)._calculate_widths(inp1, inp2)
        if exp1 is None:
            exp1, exp2 = inp1, inp2
        if exp1 + exp2 > 0:
            if exp1 > exp2:
                exp1 -= 0.01
            else:
                exp2 -= 0.01
        inp_msg = ' with inputs (%s, %s)' % (inp1, inp2)
        assert_equals(act1, exp1, 'Wrong pass percentage' + inp_msg)
        assert_equals(act2, exp2, 'Wrong fail percentage' + inp_msg)

    def test_percentages_to_widths_zeros(self):
        self._verify_percentages_to_widths(0.0, 0.0)

    def test_percentages_to_widths_no_changes(self):
        for in1, in2 in [ (0.0, 100.0),
                          (1.0, 99.0),
                          (33.3, 66.7),
                          (50.0, 50.0) ]:
            self._verify_percentages_to_widths(in1, in2)
            self._verify_percentages_to_widths(in2, in1)

    def test_percentages_to_widths_below_limit(self):
        for in1, in2 in [ (0.1, 99.9), (0.2, 99.8), (0.9, 99.1) ]:
            self._verify_percentages_to_widths(in1, in2, 1.0, 99.0)
            self._verify_percentages_to_widths(in2, in1, 99.0, 1.0)

    def test_percentages_to_widths_when_both_rounded_up(self):
        for in1, in2, ex1, ex2 in [ (1.1, 99.0, 1.1, 98.9),
                                    (18.8, 81.3, 18.8, 81.2),
                                    (44.5, 55.6, 44.5, 55.5),
                                    (50.0, 50.1, 50.0, 50.0) ]:
            self._verify_percentages_to_widths(in1, in2, ex1, ex2)
            self._verify_percentages_to_widths(in2, in1, ex2, ex1)


if __name__ == "__main__":
    unittest.main()
