import unittest

from robot.writer.formatters import Formatter, TxtFormatter
from robot.utils.asserts import assert_equals


class TestFormatter(unittest.TestCase):

    def test_escaping_empty_cells_at_eol(self):
        formatter = Formatter(cols=3)
        assert_equals(formatter.format(['Some', 'text', '', 'with empty'], 0),
                                       [['Some', 'text', '${EMPTY}'],
                                        ['...', 'with empty']])

    def test_escaping(self):
        formatter = TxtFormatter()
        assert_equals(formatter.format(['so  me']), [['so \ me']])


if __name__ == "__main__":
    unittest.main()
