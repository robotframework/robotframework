import random
import unittest
from robot.output.loggerhelper import LEVELS

from robot.reporting.jsmodelbuilders import JsBuildingContext
from robot.utils.asserts import assert_equals


class TestStringContext(unittest.TestCase):

    def test_add_empty_string(self):
        self._verify([''], [0] , ('*',))

    def test_add_text(self):
        self._verify(['Hello!'], [1] , ('*', '*Hello!'))

    def test_add_several_texts(self):
        self._verify(['Hello!', '', 'Foo'], [1, 0, 2] , ('*', '*Hello!', '*Foo'))

    def _verify(self, strings, exp_ids, exp_strings):
        ctx = JsBuildingContext()
        results = [ctx.string(s) for s in strings]
        assert_equals(results, exp_ids)
        assert_equals(ctx.strings, exp_strings)


class TestTimestamp(unittest.TestCase):

    def setUp(self):
        self._context = JsBuildingContext()

    def test_timestamp(self):
        assert_equals(self._context.timestamp('20110603 12:00:00.042'), 0)
        assert_equals(self._context.timestamp('20110603 12:00:00.043'), 1)
        assert_equals(self._context.timestamp('20110603 12:00:00.000'), -42)
        assert_equals(self._context.timestamp('20110603 12:00:01.041'), 999)
        assert_equals(self._context.timestamp('20110604 12:00:00.042'),
                      24 * 60 * 60 * 1000)

    def test_none_timestamp(self):
        assert_equals(self._context.timestamp(None), None)


class TestMinLogLevel(unittest.TestCase):

    def setUp(self):
        self._context = JsBuildingContext()

    def test_trace_is_identified_as_smallest_log_level(self):
        self._messages(LEVELS.keys())
        assert_equals('TRACE', self._context.min_level)

    def test_debug_is_identified_when_no_trace(self):
        self._messages([l for l in LEVELS if l != 'TRACE'])
        assert_equals('DEBUG', self._context.min_level)

    def test_info_is_smallest_when_no_debug_or_trace(self):
        self._messages(['INFO', 'WARN', 'ERROR', 'FAIL'])
        assert_equals('INFO', self._context.min_level)

    def _messages(self, levels):
        levels = levels[:]
        random.shuffle(levels)
        for level in levels:
            self._context.message_level(level)


if __name__ == '__main__':
    unittest.main()
