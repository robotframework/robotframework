import unittest

from robot.model import Message
from robot.utils.asserts import assert_equal, assert_raises


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

    def test_repr(self):
        assert_equal(repr(self.empty), "''")
        assert_equal(repr(self.ascii), "'Kekkonen'")
        assert_equal(repr(self.non_ascii), "'hyv? nimi'")

    def test_slots(self):
        assert_raises(AttributeError, setattr, Message(), 'attr', 'value')
