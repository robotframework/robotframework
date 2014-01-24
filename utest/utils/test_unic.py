import unittest
import sys

from robot.utils import unic, safe_repr
from robot.utils.asserts import assert_equals, assert_true


JYTHON = sys.platform.startswith('java')
IPY = sys.platform == 'cli'
UNREPR = u"<Unrepresentable object '%s'. Error: %s>"


if JYTHON:

    from java.lang import String, Object, RuntimeException
    import JavaObject
    import UnicodeJavaLibrary

    class TestJavaUnic(unittest.TestCase):

        def test_with_java_object(self):
            data = u'This is unicode \xe4\xf6'
            assert_equals(unic(JavaObject(data)), data)

        def test_with_class_type(self):
            assert_true('java.lang.String' in unic(String('').getClass()))

        def test_with_array_containing_unicode_objects(self):
            assert_true('Circle is 360' in
                        unic(UnicodeJavaLibrary().javaObjectArray()))

        def test_with_iterator(self):
            iterator = UnicodeJavaLibrary().javaIterator()
            assert_true('java.util' in unic(iterator))
            assert_true('Circle is 360' in iterator.next())

        def test_failure_in_toString(self):
            class ToStringFails(Object):
                def toString(self):
                    raise RuntimeException('failure in toString')
            assert_equals(unic(ToStringFails()),
                          UNREPR % ('ToStringFails', 'failure in toString'))


class TestUnic(unittest.TestCase):

    if not (JYTHON or IPY):
        def test_unicode_nfc_and_nfd_decomposition_equality(self):
            import unicodedata
            text = u'Hyv\xe4'
            assert_equals(unic(unicodedata.normalize('NFC', text)), text)
            # In Mac filesystem umlaut characters are presented in NFD-format.
            # This is to check that unic normalizes all strings to NFC
            assert_equals(unic(unicodedata.normalize('NFD', text)), text)

    if not IPY:
        def test_encoding(self):
            good = u'hyv\xe4'
            assert_equals(unic(good.encode('UTF-8'), 'UTF-8'), good)
            assert_equals(unic(good.encode('UTF-8'), 'ASCII', 'ignore'), 'hyv')

    def test_object_containing_unicode_repr(self):
        assert_equals(unic(UnicodeRepr()), u'Hyv\xe4')

    def test_list_with_objects_containing_unicode_repr(self):
        objects = [UnicodeRepr(), UnicodeRepr()]
        result = unic(objects)
        if JYTHON:
            # This is actually wrong behavior
            assert_equals(result, '[Hyv\\xe4, Hyv\\xe4]')
        elif IPY:
            # And so is this.
            assert_equals(result, '[Hyv\xe4, Hyv\xe4]')
        else:
            expected = UNREPR[:-1] % ('list', 'UnicodeEncodeError: ')
            assert_true(result.startswith(expected))

    def test_bytes_below_128(self):
        assert_equals(unic('\x00-\x01-\x02-\x7f'), u'\x00-\x01-\x02-\x7f')

    if not IPY:

        def test_bytes_above_128(self):
            assert_equals(unic('hyv\xe4'), u'hyv\\xe4')
            assert_equals(unic('\x00-\x01-\x02-\xe4'), u'\x00-\x01-\x02-\\xe4')

        def test_bytes_with_newlines_tabs_etc(self):
            # 'string_escape' escapes some chars we don't want to be escaped
            assert_equals(unic("\x00\xe4\n\t\r\\'"), u"\x00\\xe4\n\t\r\\'")

    else:

        def test_bytes_above_128(self):
            assert_equals(unic('hyv\xe4'), u'hyv\xe4')
            assert_equals(unic('\x00-\x01-\x02-\xe4'), u'\x00-\x01-\x02-\xe4')

        def test_bytes_with_newlines_tabs_etc(self):
            # 'string_escape' escapes some chars we don't want to be escaped
            assert_equals(unic("\x00\xe4\n\t\r\\'"), u"\x00\xe4\n\t\r\\'")

    def test_failure_in_unicode(self):
        assert_equals(unic(UnicodeFails()),
                      UNREPR % ('UnicodeFails', 'Failure in __unicode__'))

    def test_failure_in_str(self):
        assert_equals(unic(StrFails()),
                      UNREPR % ('StrFails', 'Failure in __str__'))


class TestSafeRepr(unittest.TestCase):

    def test_failure_in_repr(self):
        assert_equals(safe_repr(ReprFails()),
                      UNREPR % ('ReprFails', 'Failure in __repr__'))

    def test_repr_of_unicode_has_u_prefix(self):
        assert_equals(safe_repr(u'foo'), "u'foo'")
        assert_equals(safe_repr(u"f'o'o"), "u\"f'o'o\"")

    def test_unicode_items_in_list_repr_have_u_prefix(self):
        assert_equals(safe_repr([]), '[]')
        assert_equals(safe_repr([u'foo']), "[u'foo']")
        assert_equals(safe_repr([u'a', 1, u"'"]), "[u'a', 1, u\"'\"]")


class UnicodeRepr(object):
    def __repr__(self):
        return u'Hyv\xe4'


class UnicodeFails(object):
    def __unicode__(self):
        raise RuntimeError('Failure in __unicode__')


class StrFails(object):
    def __unicode__(self):
        raise UnicodeError()
    def __str__(self):
        raise RuntimeError('Failure in __str__')


class ReprFails(object):
    def __repr__(self):
        raise RuntimeError('Failure in __repr__')


if __name__ == '__main__':
    unittest.main()
