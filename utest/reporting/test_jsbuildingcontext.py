import unittest

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


if __name__ == '__main__':
    unittest.main()
