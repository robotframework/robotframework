import unittest

from robot.model import Message
from robot.utils.asserts import assert_equal, assert_raises


class TestHtmlMessage(unittest.TestCase):

    def test_empty(self):
        assert_equal(Message().html_message, '')
        assert_equal(Message(html=True).html_message, '')

    def test_no_html(self):
        assert_equal(Message('Hello, Kitty!').html_message, 'Hello, Kitty!')
        assert_equal(Message('<b> & ftp://x').html_message,
                             '&lt;b&gt; &amp; <a href="ftp://x">ftp://x</a>')

    def test_html(self):
        assert_equal(Message('Hello, Kitty!', html=True).html_message, 'Hello, Kitty!')
        assert_equal(Message('<b> & ftp://x', html=True).html_message, '<b> & ftp://x')


class TestStringRepresentation(unittest.TestCase):

    def setUp(self):
        self.empty = Message()
        self.ascii = Message('Kekkonen')
        self.non_ascii = Message(u'hyv\xe4 nimi')

    def test_unicode(self):
        assert_equal(unicode(self.empty), '')
        assert_equal(unicode(self.ascii), 'Kekkonen')
        assert_equal(unicode(self.non_ascii), u'hyv\xe4 nimi')

    def test_str(self):
        assert_equal(str(self.empty), '')
        assert_equal(str(self.ascii), 'Kekkonen')
        assert_equal(str(self.non_ascii), 'hyv? nimi')

    def test_slots(self):
        assert_raises(AttributeError, setattr, Message(), 'attr', 'value')


if __name__ == '__main__':
    unittest.main()
