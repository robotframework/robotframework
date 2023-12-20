import unittest
from pathlib import Path

from robot.reporting.logreportwriters import LogWriter
from robot.utils.asserts import assert_true, assert_equal


class LogWriterWithMockedWriting(LogWriter):

    def __init__(self, model):
        LogWriter.__init__(self, model)
        self.split_write_calls = []
        self.write_called = False

    def _write_split_log(self, index, keywords, strings, path):
        self.split_write_calls.append((index, keywords, strings, path))

    def _write_file(self, output, config, template):
        self.write_called = True


class TestLogWriter(unittest.TestCase):

    def test_splitting_log(self):
        class model:
            split_results = [((0, 1, 2, -1), ('*', '*1', '*2')),
                             ((0, 1, 0, 42), ('*','*x')),
                             (((1, 2), (3, 4, ())), ('*',))]
        writer = LogWriterWithMockedWriting(model)
        writer.write('mylog.html', None)
        assert_true(writer.write_called)
        assert_equal([(1, (0, 1, 2, -1), ('*', '*1', '*2'), Path('mylog-1.js')),
                       (2, (0, 1, 0, 42), ('*', '*x'), Path('mylog-2.js')),
                       (3, ((1, 2), (3, 4, ())), ('*',), Path('mylog-3.js'))],
                     writer.split_write_calls)


if __name__ == '__main__':
    unittest.main()
