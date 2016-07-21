import time
import unittest

from robot.utils.asserts import assert_equal
from robot.utils.robottime import TimestampCache


class FakeTimestampCache(TimestampCache):

    def __init__(self, epoch):
        TimestampCache.__init__(self)
        self.epoch = epoch + self.timezone_correction()

    def _get_epoch(self):
        return self.epoch

    def timezone_correction(self):
        dst = 3600 if time.daylight == 0 else 0
        tz = 7200 + time.timezone
        return (tz + dst)


class TestTimestamp(unittest.TestCase):

    def test_new_timestamp(self):
        actual = FakeTimestampCache(1338816626.999).get_timestamp()
        assert_equal(actual, '20120604 16:30:26.999')

    def test_cached(self):
        cache = FakeTimestampCache(1338816626.900)
        cache.get_timestamp()
        cache.epoch += 0.099
        assert_equal(cache.get_timestamp(), '20120604 16:30:26.999')

    def test_round_to_next_second(self):
        cache = FakeTimestampCache(1338816626.0)
        assert_equal(cache.get_timestamp(), '20120604 16:30:26.000')
        cache.epoch += 0.9995
        assert_equal(cache.get_timestamp(), '20120604 16:30:27.000')

    def test_cache_timestamp_without_millis_separator(self):
        cache = FakeTimestampCache(1338816626.0)
        assert_equal(cache.get_timestamp(millissep=None), '20120604 16:30:26')
        assert_equal(cache.get_timestamp(millissep=None), '20120604 16:30:26')
        assert_equal(cache.get_timestamp(), '20120604 16:30:26.000')

    def test_separators(self):
        cache = FakeTimestampCache(1338816626.001)
        assert_equal(cache.get_timestamp(daysep='-', daytimesep='T'),
                      '2012-06-04T16:30:26.001')
        assert_equal(cache.get_timestamp(timesep='', millissep='X'),
                      '20120604 163026X001')


if __name__ == "__main__":
    unittest.main()
