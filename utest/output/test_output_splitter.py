import unittest

from robot.utils.asserts import *

from robot.output.output import _OutputSplitter


class TestOutputSplitter(unittest.TestCase):

    def test_empty_output_should_result_in_empty_messages_list(self):
        splitter = _OutputSplitter('')
        assert_equals(list(splitter), [])

    def test_plain_output_should_have_info_level(self):
        splitter = _OutputSplitter('this is message\nin many\nlines.')
        self._verify_message(splitter, 'this is message\nin many\nlines.')
        assert_equals(len(list(splitter)), 1)

    def test_leading_and_trailing_space_should_be_stripped(self):
        splitter = _OutputSplitter('\t  \n My message    \t\r\n')
        self._verify_message(splitter, 'My message')
        assert_equals(len(list(splitter)), 1)

    def test_legal_level_is_correctly_read(self):
        splitter = _OutputSplitter('*DEBUG* My message details')
        self._verify_message(splitter, 'My message details', 'DEBUG')
        assert_equals(len(list(splitter)), 1)

    def test_space_after_level_is_optional(self):
        splitter = _OutputSplitter('*WARN*No space!')
        self._verify_message(splitter, 'No space!', 'WARN')
        assert_equals(len(list(splitter)), 1)

    def test_it_is_possible_to_define_multiple_levels(self):
        splitter = _OutputSplitter('*WARN* WARNING!\n'
                                   '*TRACE*msg')
        self._verify_message(splitter, 'WARNING!', 'WARN')
        self._verify_message(splitter, 'msg', 'TRACE', index=1)
        assert_equals(len(list(splitter)), 2)

    def test_html_flag_should_be_parsed_correctly_and_uses_info_level(self):
        splitter = _OutputSplitter('*HTML* <b>Hello</b>')
        self._verify_message(splitter, '<b>Hello</b>', level='INFO', html=True)
        assert_equals(len(list(splitter)), 1)

    def test_default_level_for_first_message_is_info(self):
        splitter = _OutputSplitter('<img src="foo bar">\n'
                                   '*DEBUG*bar foo')
        self._verify_message(splitter, '<img src="foo bar">')
        self._verify_message(splitter, 'bar foo', 'DEBUG', index=1)
        assert_equals(len(list(splitter)), 2)

    def _verify_message(self, splitter, msg, level='INFO', html=False, index=0):
        message = list(splitter)[index]
        assert_equals(message.message, msg)
        assert_equals(message.level, level)
        assert_equals(message.html, html)


if __name__ == '__main__':
    unittest.main()
