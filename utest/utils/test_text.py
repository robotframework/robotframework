import unittest

from robot.utils.asserts import *

from robot.utils.text import cut_long_message, _count_line_lenghts, \
    _MAX_ERROR_LINES, _MAX_ERROR_LINE_LENGTH, _ERROR_CUT_EXPLN,\
    get_console_length, pad_console_length


class NoCutting(unittest.TestCase):

    def test_empty_string(self):
        self._assert_no_cutting('')

    def test_short_message(self):
        self._assert_no_cutting('bar')

    def test_few_short_lines(self):
        self._assert_no_cutting('foo\nbar\zap\hello World!')

    def test_max_number_of_short_lines(self):
        self._assert_no_cutting('short line\n' * _MAX_ERROR_LINES)

    def _assert_no_cutting(self, msg):
        assert_equal(cut_long_message(msg), msg)


class TestCutting(unittest.TestCase):

    def setUp(self):
        self.lines = [ 'my error message %d' % i for i in range(_MAX_ERROR_LINES+1) ]
        self.result = cut_long_message('\n'.join(self.lines)).splitlines()
        self.limit = _MAX_ERROR_LINES/2

    def test_more_than_max_number_of_lines(self):
        assert_equal(len(self.result), _MAX_ERROR_LINES+1)

    def test_cut_message_is_present(self):
        assert_true(_ERROR_CUT_EXPLN in self.result)

    def test_cut_message_starts_with_original_lines(self):
        expected = self.lines[:self.limit]
        actual = self.result[:self.limit]
        assert_equal(actual, expected)

    def test_cut_message_ends_with_original_lines(self):
        expected = self.lines[-self.limit:]
        actual = self.result[-self.limit:]
        assert_equal(actual, expected)


class TestCuttingWithLinesLongerThanMax(unittest.TestCase):

    def setUp(self):
        self.lines = ['line %d' % i for i in range(_MAX_ERROR_LINES-1)]
        self.lines.append('x' * (_MAX_ERROR_LINE_LENGTH+1) )
        self.result = cut_long_message('\n'.join(self.lines)).splitlines()

    def test_cut_message_present(self):
        assert_true(_ERROR_CUT_EXPLN in self.result)

    def test_correct_number_of_lines(self):
        assert_equal(sum(_count_line_lenghts(self.result)), _MAX_ERROR_LINES+1)

    def test_correct_lines(self):
        excpected = self.lines[:_MAX_ERROR_LINES/2] + [_ERROR_CUT_EXPLN] \
                + self.lines[-_MAX_ERROR_LINES/2+1:]
        assert_equal(self.result, excpected)

    def test_every_line_longer_than_limit(self):
        # sanity check
        lines = [('line %d' % i) * _MAX_ERROR_LINE_LENGTH for i in range(_MAX_ERROR_LINES+2)]
        result = cut_long_message('\n'.join(lines)).splitlines()
        assert_true(_ERROR_CUT_EXPLN in result)
        assert_equal(result[0], lines[0])
        assert_equal(result[-1], lines[-1])
        assert_true(sum(_count_line_lenghts(result)) <= _MAX_ERROR_LINES+1)


class TestCutHappensInsideLine(unittest.TestCase):

    def test_long_line_cut_before_cut_message(self):
        lines = ['line %d' % i for i in range(_MAX_ERROR_LINES)]
        index = _MAX_ERROR_LINES/2-1
        lines[index] = 'abcdefgh' * _MAX_ERROR_LINE_LENGTH
        result = cut_long_message('\n'.join(lines)).splitlines()
        self._assert_basics(result, lines)
        expected = lines[index][:_MAX_ERROR_LINE_LENGTH-3] + '...'
        assert_equal(result[index], expected)

    def test_long_line_cut_after_cut_message(self):
        lines = ['line %d' % i for i in range(_MAX_ERROR_LINES)]
        index = _MAX_ERROR_LINES/2
        lines[index] = 'abcdefgh' * _MAX_ERROR_LINE_LENGTH
        result = cut_long_message('\n'.join(lines)).splitlines()
        self._assert_basics(result, lines)
        expected = '...' + lines[index][-_MAX_ERROR_LINE_LENGTH+3:]
        assert_equal(result[index+1], expected)

    def test_one_huge_line(self):
        result = cut_long_message('0123456789' * _MAX_ERROR_LINES * _MAX_ERROR_LINE_LENGTH)
        self._assert_basics(result.splitlines())
        assert_true(result.startswith('0123456789'))
        assert_true(result.endswith('0123456789'))
        assert_true('...\n'+_ERROR_CUT_EXPLN+'\n...' in result)

    def _assert_basics(self, result, input=None):
        assert_equal(sum(_count_line_lenghts(result)), _MAX_ERROR_LINES+1)
        assert_true(_ERROR_CUT_EXPLN in result)
        if input:
            assert_equal(result[0], input[0])
            assert_equal(result[-1], input[-1])


class TestCountLines(unittest.TestCase):

    def test_no_lines(self):
        assert_equal(_count_line_lenghts([]), [])

    def test_empty_line(self):
        assert_equal(_count_line_lenghts(['']), [1])

    def test_shorter_than_max_lines(self):
        lines = ['', '1', 'foo', 'barz and fooz', '', 'a bit longer line', '',
                 'This is a somewhat longer (but not long enough) error message']
        assert_equal(_count_line_lenghts(lines), [1] * len(lines))

    def test_longer_than_max_lines(self):
        lines = [ '1' * i * (_MAX_ERROR_LINE_LENGTH+3) for i in range(4) ]
        assert_equal(_count_line_lenghts(lines), [1,2,3,4])

    def test_boundary(self):
        b = _MAX_ERROR_LINE_LENGTH
        lengths = [b-1, b, b+1, 2*b-1, 2*b, 2*b+1, 7*b-1, 7*b, 7*b+1]
        lines = [ 'e'*length for length in lengths ]
        assert_equal(_count_line_lenghts(lines), [1, 1, 2, 2, 2, 3, 7, 7, 8])


class TestConsoleWidth(unittest.TestCase):
    len16_asian = u'\u6c49\u5b57\u5e94\u8be5\u6b63\u786e\u5bf9\u9f50'
    ten_normal = u'1234567890'
    mixed_26 = u'012345\u6c49\u5b57\u5e94\u8be5\u6b63\u786e\u5bf9\u9f567890'
    nfd = u'A\u030Abo'

    def test_console_width(self):
        assert_equal(get_console_length(self.ten_normal), 10)

    def test_east_asian_width(self):
        assert_equal(get_console_length(self.len16_asian), 16)

    def test_combining_width(self):
        assert_equal(get_console_length(self.nfd), 3)

    def test_cut_right(self):
        assert_equal(pad_console_length(self.ten_normal, 5), '12...')
        assert_equal(pad_console_length(self.ten_normal, 15), self.ten_normal+' '*5)
        assert_equal(pad_console_length(self.ten_normal, 10), self.ten_normal)

    def test_cut_east_asian(self):
        assert_equal(pad_console_length(self.len16_asian, 10), u'\u6c49\u5b57\u5e94... ')
        assert_equal(pad_console_length(self.mixed_26, 11), u'012345\u6c49...')


if __name__ == '__main__':
    unittest.main()
