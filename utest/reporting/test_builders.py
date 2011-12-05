from StringIO import StringIO
import unittest
from robot.reporting.builders import LogBuilder
from robot.utils.asserts import assert_true, assert_equals


class _LogBuilderWithMockedWriting(LogBuilder):

    def __init__(self, model):
        LogBuilder.__init__(self, model)
        self._split_write_calls = []
        self._write_called = False

    def _write_split_log(self, index, keywords, strings, path):
        self._split_write_calls.append((index, keywords, strings, path))

    def _write_file(self, output, config, template):
        self._write_called = True


class TestLogBuilder(unittest.TestCase):

    def test_splitting_log(self):
        model = lambda:0
        splitted_result1 = [[1],['*']]
        splitted_result2 = [[4],['A']]
        model.split_results = [splitted_result1, splitted_result2]
        log_builder = _LogBuilderWithMockedWriting(model)
        log_builder.build(object(), object())
        assert_true(log_builder._write_called)
        assert_equals([(1, [1], ['*'], '-1.js'),
                       (2, [4], ['A'], '-2.js')],
                      log_builder._split_write_calls)


if __name__ == '__main__':
    unittest.main()
