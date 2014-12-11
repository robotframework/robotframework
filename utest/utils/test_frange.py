import unittest
import sys

from robot.utils.frange import frange
from robot.utils.asserts import assert_equals

if sys.platform.startswith('java'):
    import JavaExceptions


IPY = sys.platform == 'cli'


class TestFrangeUtils(unittest.TestCase):

    def test_frange(self):
        for input, expected in [([7],[0, 1, 2, 3, 4, 5, 6]),
                                (['6'],[0, 1, 2, 3, 4, 5]),
                                ([3.14],[0, 1.0, 2.0, 3.0]),
                                (['7.9'],[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]),
                                ([2+3],[0, 1, 2, 3, 4]),
                                (['6-1'],[0, 1, 2, 3, 4]),
                                ([3.14*2.0],[0, 1.0, 2.0, 3.0, 4.0 ,5.0, 6.0]),
                                (['9.3/3'],[0, 1.0, 2.0, 3.0]),
                                ([1,7],[1, 2, 3, 4, 5, 6]),
                                (['3','9'],[3, 4, 5, 6, 7, 8]),
                                ([1.3,7.8],[1.3, 2.3, 3.3, 4.3, 5.3, 6.3, 7.3]),
                                (['-3.4','2.3'],[-3.4, -2.4, -1.4, -0.4, 0.6, 1.6]),
                                (['1+5.2',11],[6.2, 7.2, 8.2, 9.2, 10.2]),
                                ([1,12,3],[1, 4, 7, 10]),
                                (['3','-3','-1'],[3, 2, 1, 0, -1, -2]),
                                ([1,12,3+2],[1, 6, 11]),
                                (['-7.9','12.5','2*2'],[-7.9, -3.9, 0.1, 4.1, 8.1, 12.1]),
                                (['0.1','10+1.2','2*2.3'],[0.1, 4.7, 9.3])]:
            assert_equals(frange(*input), expected)


if __name__ == "__main__":
    unittest.main()
