import unittest
import time

from robot.utils.asserts import assert_equal
from robot.utils import format_time

from robot.output.stdoutlogsplitter import StdoutLogSplitter as Splitter


class TestOutputSplitter(unittest.TestCase):

    def test_empty_output_should_result_in_empty_messages_list(self):
        splitter = Splitter('')
        assert_equal(list(splitter), [])

    def test_plain_output_should_have_info_level(self):
        splitter = Splitter('this is message\nin many\nlines.')
        self._verify_message(splitter, 'this is message\nin many\nlines.')
        assert_equal(len(list(splitter)), 1)

    def test_leading_and_trailing_space_should_be_stripped(self):
        splitter = Splitter('\t  \n My message    \t\r\n')
        self._verify_message(splitter, 'My message')
        assert_equal(len(list(splitter)), 1)

    def test_legal_level_is_correctly_read(self):
        splitter = Splitter('*DEBUG* My message details')
        self._verify_message(splitter, 'My message details', 'DEBUG')
        assert_equal(len(list(splitter)), 1)

    def test_space_after_level_is_optional(self):
        splitter = Splitter('*WARN*No space!')
        self._verify_message(splitter, 'No space!', 'WARN')
        assert_equal(len(list(splitter)), 1)

    def test_it_is_possible_to_define_multiple_levels(self):
        splitter = Splitter('*WARN* WARNING!\n'
                            '*TRACE*msg')
        self._verify_message(splitter, 'WARNING!', 'WARN')
        self._verify_message(splitter, 'msg', 'TRACE', index=1)
        assert_equal(len(list(splitter)), 2)

    def test_html_flag_should_be_parsed_correctly_and_uses_info_level(self):
        splitter = Splitter('*HTML* <b>Hello</b>')
        self._verify_message(splitter, '<b>Hello</b>', level='INFO', html=True)
        assert_equal(len(list(splitter)), 1)

    def test_default_level_for_first_message_is_info(self):
        splitter = Splitter('<img src="foo bar">\n'
                                   '*DEBUG*bar foo')
        self._verify_message(splitter, '<img src="foo bar">')
        self._verify_message(splitter, 'bar foo', 'DEBUG', index=1)
        assert_equal(len(list(splitter)), 2)

    def test_timestamp_given_as_integer(self):
        now = int(time.time())
        splitter = Splitter('*INFO:xxx* No timestamp\n'
                            '*INFO:0* Epoch\n'
                            '*HTML:%d*X' % (now*1000))
        self._verify_message(splitter, '*INFO:xxx* No timestamp')
        self._verify_message(splitter, 'Epoch', timestamp=0, index=1)
        self._verify_message(splitter, html=True, timestamp=now, index=2)
        assert_equal(len(list(splitter)), 3)

    def test_timestamp_given_as_float(self):
        splitter = Splitter('*INFO:1x2* No timestamp\n'
                            '*HTML:1000.123456789* X\n'
                            '*INFO:12345678.9*X')
        self._verify_message(splitter, '*INFO:1x2* No timestamp')
        self._verify_message(splitter, html=True, timestamp=1, index=1)
        self._verify_message(splitter, timestamp=12345.679, index=2)
        assert_equal(len(list(splitter)), 3)

    def _verify_message(self, splitter, msg='X', level='INFO', html=False,
                        timestamp=None, index=0):
        message = list(splitter)[index]
        assert_equal(message.message, msg)
        assert_equal(message.level, level)
        assert_equal(message.html, html)
        if timestamp:
            assert_equal(message.timestamp,
                          format_time(timestamp, millissep='.'))


if __name__ == '__main__':
    unittest.main()
