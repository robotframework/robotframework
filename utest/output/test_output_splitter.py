import unittest

from robot.utils.asserts import *

from robot.output.output import _OutputSplitter

        
class TestOutputSplitter(unittest.TestCase):
    
    def test_empty_output_should_result_in_empty_messages_list(self):
        splitter = _OutputSplitter('')
        assert_equals([], splitter.messages)
        
    def test_plain_output_should_have_info_level(self):
        splitter = _OutputSplitter('this is an output message\nin many\nlines.')
        assert_equals(1, len(splitter.messages))
        self._verify_message(splitter, 'this is an output message\nin many\nlines.')
        
    def test_leading_and_trailing_space_should_be_stripped(self):
        splitter = _OutputSplitter('\t  \n My message    \t\r\n')
        self._verify_message(splitter, 'My message')

    def test_legal_level_is_correctly_read(self):
        splitter = _OutputSplitter('*DEBUG* My message details')
        self._verify_message(splitter, 'My message details', 'DEBUG')
        
    def test_it_is_possible_to_define_multiple_levels(self):
        splitter = _OutputSplitter('*WARN*WARNING!\n*DEBUG*msg')
        assert_equals(2, len(splitter.messages))
        self._verify_message(splitter, 'WARNING!', 'WARN')
        self._verify_message(splitter, 'msg', 'DEBUG', index=1)

    def test_html_flag_should_be_parsed_correctly_and_uses_info_level(self):
        splitter = _OutputSplitter('*HTML* <div><a href="">link</a></div>')
        self._verify_message(splitter, '<div><a href="">link</a></div>', 'INFO', True)
                        
    def test_default_level_for_first_message_in_info(self):
        splitter = _OutputSplitter('<img src="foo bar">\n*DEBUG*bar foo')
        self._verify_message(splitter, '<img src="foo bar">')
        self._verify_message(splitter, 'bar foo', 'DEBUG', index=1)
        
        
    def _verify_message(self, splitter, msg, level='INFO', html=False, index=0):
        assert_equals(splitter.messages[index].message, msg)
        assert_equals(splitter.messages[index].level, level)
        assert_equals(splitter.messages[index].html, html)

        
if __name__ == '__main__':
    unittest.main()
