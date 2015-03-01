import random
import unittest
from robot.output.loggerhelper import LEVELS

from robot.reporting.jsmodelbuilders import JsBuildingContext
from robot.utils.asserts import assert_equals


class TestStringContext(unittest.TestCase):

    def test_add_empty_string(self):
        self._verify([''], [0], [])

    def test_add_string(self):
        self._verify(['Hello!'], [1], ['Hello!'])

    def test_add_several_strings(self):
        self._verify(['Hello!', 'Foo'], [1, 2], ['Hello!', 'Foo'])

    def test_cache_strings(self):
        self._verify(['Foo', '', 'Foo', 'Foo', ''], [1, 0, 1, 1, 0], ['Foo'])

    def test_escape_strings(self):
        self._verify(['</script>', '&', '&'], [1, 2, 2], ['&lt;/script&gt;', '&amp;'])

    def test_no_escape(self):
        self._verify(['</script>', '&', '&'], [1, 2, 2], ['</script>', '&'], escape=False)

    def test_none_string(self):
        self._verify([None, '', None], [0, 0, 0], [])

    def _verify(self, strings, exp_ids, exp_strings, escape=True):
        exp_strings = tuple('*'+s for s in [''] + exp_strings)
        ctx = JsBuildingContext()
        results = [ctx.string(s, escape=escape) for s in strings]
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
        levels = list(levels)
        random.shuffle(levels)
        for level in levels:
            self._context.message_level(level)


if __name__ == '__main__':
    unittest.main()
