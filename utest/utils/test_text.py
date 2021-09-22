import unittest
import os
from os.path import abspath

from robot.utils.asserts import assert_equal, assert_true
from robot.utils.text import (
    cut_long_message, get_console_length, getdoc, getshortdoc,
    pad_console_length, split_tags_from_doc, split_args_from_name_or_path,
    _count_line_lengths, MAX_ERROR_LINES, _MAX_ERROR_LINE_LENGTH,
    _ERROR_CUT_EXPLN
)


_HALF_ERROR_LINES = MAX_ERROR_LINES // 2


class NoCutting(unittest.TestCase):

    def test_empty_string(self):
        self._assert_no_cutting('')

    def test_short_message(self):
        self._assert_no_cutting('bar')

    def test_few_short_lines(self):
        self._assert_no_cutting('foo\nbar\nzap\nphello World!')

    def test_max_number_of_short_lines(self):
        self._assert_no_cutting('short line\n' * MAX_ERROR_LINES)

    def _assert_no_cutting(self, msg):
        assert_equal(cut_long_message(msg), msg)


class TestCutting(unittest.TestCase):

    def setUp(self):
        self.lines = ['my error message %d' % i for i in range(MAX_ERROR_LINES+1)]
        self.result = cut_long_message('\n'.join(self.lines)).splitlines()
        self.limit = _HALF_ERROR_LINES

    def test_more_than_max_number_of_lines(self):
        assert_equal(len(self.result), MAX_ERROR_LINES+1)

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
        self.lines = ['line %d' % i for i in range(MAX_ERROR_LINES-1)]
        self.lines.append('x' * (_MAX_ERROR_LINE_LENGTH+1))
        self.result = cut_long_message('\n'.join(self.lines)).splitlines()

    def test_cut_message_present(self):
        assert_true(_ERROR_CUT_EXPLN in self.result)

    def test_correct_number_of_lines(self):
        assert_equal(sum(_count_line_lengths(self.result)), MAX_ERROR_LINES+1)

    def test_correct_lines(self):
        expected = self.lines[:_HALF_ERROR_LINES] + [_ERROR_CUT_EXPLN] \
                + self.lines[-_HALF_ERROR_LINES+1:]
        assert_equal(self.result, expected)

    def test_every_line_longer_than_limit(self):
        # sanity check
        lines = [('line %d' % i) * _MAX_ERROR_LINE_LENGTH for i in range(MAX_ERROR_LINES+2)]
        result = cut_long_message('\n'.join(lines)).splitlines()
        assert_true(_ERROR_CUT_EXPLN in result)
        assert_equal(result[0], lines[0])
        assert_equal(result[-1], lines[-1])
        assert_true(sum(_count_line_lengths(result)) <= MAX_ERROR_LINES+1)


class TestCutHappensInsideLine(unittest.TestCase):

    def test_long_line_cut_before_cut_message(self):
        lines = ['line %d' % i for i in range(MAX_ERROR_LINES)]
        index = _HALF_ERROR_LINES - 1
        lines[index] = 'abcdefgh' * _MAX_ERROR_LINE_LENGTH
        result = cut_long_message('\n'.join(lines)).splitlines()
        self._assert_basics(result, lines)
        expected = lines[index][:_MAX_ERROR_LINE_LENGTH-3] + '...'
        assert_equal(result[index], expected)

    def test_long_line_cut_after_cut_message(self):
        lines = ['line %d' % i for i in range(MAX_ERROR_LINES)]
        index = _HALF_ERROR_LINES
        lines[index] = 'abcdefgh' * _MAX_ERROR_LINE_LENGTH
        result = cut_long_message('\n'.join(lines)).splitlines()
        self._assert_basics(result, lines)
        expected = '...' + lines[index][-_MAX_ERROR_LINE_LENGTH+3:]
        assert_equal(result[index+1], expected)

    def test_one_huge_line(self):
        result = cut_long_message('0123456789' * MAX_ERROR_LINES * _MAX_ERROR_LINE_LENGTH)
        self._assert_basics(result.splitlines())
        assert_true(result.startswith('0123456789'))
        assert_true(result.endswith('0123456789'))
        assert_true('...\n'+_ERROR_CUT_EXPLN+'\n...' in result)

    def _assert_basics(self, result, input=None):
        assert_equal(sum(_count_line_lengths(result)), MAX_ERROR_LINES+1)
        assert_true(_ERROR_CUT_EXPLN in result)
        if input:
            assert_equal(result[0], input[0])
            assert_equal(result[-1], input[-1])


class TestCountLines(unittest.TestCase):

    def test_no_lines(self):
        assert_equal(_count_line_lengths([]), [])

    def test_empty_line(self):
        assert_equal(_count_line_lengths(['']), [1])

    def test_shorter_than_max_lines(self):
        lines = ['', '1', 'foo', 'barz and fooz', '', 'a bit longer line', '',
                 'This is a somewhat longer (but not long enough) error message']
        assert_equal(_count_line_lengths(lines), [1] * len(lines))

    def test_longer_than_max_lines(self):
        lines = [ '1' * i * (_MAX_ERROR_LINE_LENGTH+3) for i in range(4) ]
        assert_equal(_count_line_lengths(lines), [1,2,3,4])

    def test_boundary(self):
        b = _MAX_ERROR_LINE_LENGTH
        lengths = [b-1, b, b+1, 2*b-1, 2*b, 2*b+1, 7*b-1, 7*b, 7*b+1]
        lines = [ 'e'*length for length in lengths ]
        assert_equal(_count_line_lengths(lines), [1, 1, 2, 2, 2, 3, 7, 7, 8])


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


class TestDocSplitter(unittest.TestCase):

    def test_doc_without_tags(self):
        docs = ["Single doc line.",
                """Hello, we dont have tags here.

                No sir. No tags.""",
                "Now Tags: must, start from beginning of the row",
                "   We strip  the trailing whitespace  \n \n"]
        for doc in docs:
            self._assert_doc_and_tags(doc, doc.rstrip(), [])

    def _assert_doc_and_tags(self, original, expected_doc, expected_tags):
        doc, tags = split_tags_from_doc(original)
        assert_equal(doc, expected_doc)
        assert_equal(tags, expected_tags)

    def test_doc_with_tags(self):
        sets = [
            ('Tags: foo, bar',                  '',             ['foo', 'bar']),
            ('  Tags: foo   ',                  '',             ['foo']),
            ('Hello\nTags: foo, bar',           'Hello',        ['foo', 'bar']),
            ('Tags: bar\n   Tags: foo   ',      'Tags: bar',    ['foo']),
            ('Tags: bar, Tags:, foo   ',        '',             ['bar', 'Tags:', 'foo']),
            ('tags: foo',                       '',             ['foo']),
            ('   tags: foo ,  bar  ',           '',             ['foo', 'bar']),
            ('Hello\n   taGS: foo, bar',        'Hello',        ['foo', 'bar']),
            (' Hello\n   taGS: f, b \n\n \n',   ' Hello',       ['f', 'b']),
            ('Hello\nNl  \n  \nTags: foo',      'Hello\nNl',    ['foo']),
        ]
        for original, exp_doc, exp_tags in sets:
            self._assert_doc_and_tags(original, exp_doc, exp_tags)
            self._assert_doc_and_tags(original+'\n', exp_doc, exp_tags)


class TestSplitArgsFromNameOrPath(unittest.TestCase):

    def setUp(self):
        self.method = split_args_from_name_or_path

    def test_with_no_args(self):
        assert not os.path.exists('name'), 'does not work if you have name folder!'
        assert_equal(self.method('name'), ('name', []))

    def test_with_args(self):
        assert not os.path.exists('name'), 'does not work if you have name folder!'
        assert_equal(self.method('name:arg'), ('name', ['arg']))
        assert_equal(self.method('listener:v1:v2:v3'), ('listener', ['v1', 'v2', 'v3']))
        assert_equal(self.method('aa:bb:cc'), ('aa', ['bb', 'cc']))

    def test_empty_args(self):
        assert not os.path.exists('foo'), 'does not work if you have foo folder!'
        assert_equal(self.method('foo:'), ('foo', ['']))
        assert_equal(self.method('bar:arg1::arg3'), ('bar', ['arg1', '', 'arg3']))
        assert_equal(self.method('3:'), ('3', ['']))

    def test_semicolon_as_separator(self):
        assert_equal(self.method('name;arg'), ('name', ['arg']))
        assert_equal(self.method('name;1;2;3'), ('name', ['1', '2', '3']))
        assert_equal(self.method('name;'), ('name', ['']))

    def test_alternative_separator_in_value(self):
        assert_equal(self.method('name;v:1;v:2'), ('name', ['v:1', 'v:2']))
        assert_equal(self.method('name:v;1:v;2'), ('name', ['v;1', 'v;2']))

    def test_windows_path_without_args(self):
        assert_equal(self.method('C:\\name.py'), ('C:\\name.py', []))
        assert_equal(self.method('X:\\APPS\\listener'), ('X:\\APPS\\listener', []))
        assert_equal(self.method('C:/varz.py'), ('C:/varz.py', []))

    def test_windows_path_with_args(self):
        assert_equal(self.method('C:\\name.py:arg1'), ('C:\\name.py', ['arg1']))
        assert_equal(self.method('D:\\APPS\\listener:v1:b2:z3'),
                      ('D:\\APPS\\listener', ['v1', 'b2', 'z3']))
        assert_equal(self.method('C:/varz.py:arg'), ('C:/varz.py', ['arg']))
        assert_equal(self.method('C:\\file.py:arg;with;alternative;separator'),
                      ('C:\\file.py', ['arg;with;alternative;separator']))

    def test_windows_path_with_semicolon_separator(self):
        assert_equal(self.method('C:\\name.py;arg1'), ('C:\\name.py', ['arg1']))
        assert_equal(self.method('D:\\APPS\\listener;v1;b2;z3'),
                      ('D:\\APPS\\listener', ['v1', 'b2', 'z3']))
        assert_equal(self.method('C:/varz.py;arg'), ('C:/varz.py', ['arg']))
        assert_equal(self.method('C:\\file.py;arg:with:alternative:separator'),
                      ('C:\\file.py', ['arg:with:alternative:separator']))

    def test_existing_paths_are_made_absolute(self):
        path = 'robot-framework-unit-test-file-12q3405909qasf'
        open(path, 'w').close()
        try:
            assert_equal(self.method(path), (abspath(path), []))
            assert_equal(self.method(path+':arg'), (abspath(path), ['arg']))
        finally:
            os.remove(path)

    def test_existing_path_with_colons(self):
        # Colons aren't allowed in Windows paths (other than in "c:")
        if os.sep == '\\':
            return
        path = 'robot:framework:test:1:2:42'
        os.mkdir(path)
        try:
            assert_equal(self.method(path), (abspath(path), []))
        finally:
            os.rmdir(path)


class TestGetdoc(unittest.TestCase):

    def test_no_doc(self):
        def func():
            pass
        assert_equal(getdoc(func), '')

    def test_one_line_doc(self):
        def func():
            """My documentation."""
        assert_equal(getdoc(func), 'My documentation.')

    def test_multiline_doc(self):
        class Class:
            """My doc.

            In multiple lines.
            """
        assert_equal(getdoc(Class), 'My doc.\n\nIn multiple lines.')
        assert_equal(getdoc(Class), getdoc(Class()))

    def test_unicode_doc(self):
        class Class:
            def meth(self):
                u"""Hyv\xe4 \xe4iti!"""
        assert_equal(getdoc(Class.meth), u'Hyv\xe4 \xe4iti!')
        assert_equal(getdoc(Class.meth), getdoc(Class().meth))


class TestGetshortdoc(unittest.TestCase):

    def test_empty(self):
        self._verify('', '')

    def test_one_line(self):
        self._verify('Hello, world!', 'Hello, world!')

    def test_multiline_with_one_line_short_doc(self):
        self._verify('''\
This is the short doc. Nicely in one line.

This is the remainder of the doc.
''', 'This is the short doc. Nicely in one line.')

    def test_only_short_doc_split_to_many_lines(self):
        self._verify('This time short doc is\nsplit to multiple lines.',
                     'This time short doc is\nsplit to multiple lines.')

    def test_multiline_with_multiline_short_doc(self):
        self._verify('''\
This is the short doc.
Nicely in multiple
lines.

This is the remainder of the doc.
''', 'This is the short doc.\nNicely in multiple\nlines.')

    def test_line_with_only_spaces_is_considered_empty(self):
        self._verify('Short\ndoc\n\n    \nignored', 'Short\ndoc')

    def test_doc_from_object(self):
        def func():
            """This is short doc
            in multiple lines.

            This is the remainder.
            """
        self._verify(func, 'This is short doc\nin multiple lines.')

    def _verify(self, doc, expected):
        assert_equal(getshortdoc(doc), expected)
        assert_equal(getshortdoc(doc, linesep=' '), expected.replace('\n', ' '))


if __name__ == '__main__':
    unittest.main()
