import unittest
import sys

from robot.utils import unic, is_jython, safe_repr
from robot.utils.unic import _unrepresentable_msg
from robot.utils.asserts import assert_equals, assert_true
is_ironpython = sys.platform == 'cli'

if is_jython:

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

            unic(ToStringFails())


class TestUnic(unittest.TestCase):

    if not (is_jython or is_ironpython):
        def test_unicode_nfc_and_nfd_decomposition_equality(self):
            import unicodedata
            text = u'Hyv\xe4'
            assert_equals(unic(unicodedata.normalize('NFC', text)), text)
            # In Mac filesystem umlaut characters are presented in NFD-format.
            # This is to check that unic normalizes all strings to NFC
            assert_equals(unic(unicodedata.normalize('NFD', text)), text)

    def test_object_containing_unicode_repr(self):
        assert_equals(unic(UnicodeRepr()), u'Hyv\xe4')

    def test_list_with_objects_containing_unicode_repr(self):
        objects = [UnicodeRepr(), UnicodeRepr()]
        result = unic(objects)
        if is_jython:
            # This is actually wrong behavior
            assert_equals(result, '[Hyv\\xe4, Hyv\\xe4]')
        elif is_ironpython:
            # And so is this.
            assert_equals(result, '[Hyv\xe4, Hyv\xe4]')
        else:
            expected = _unrepresentable_msg[:-1] % ('list', 'UnicodeEncodeError: ')
            assert_true(result.startswith(expected))

    def test_failure_in_unicode(self):
        assert_equals(unic(UnicodeFails()),
                      _unrepresentable_msg % ('UnicodeFails', 'Failure in __unicode__'))

    def test_failure_in_str(self):
        assert_equals(unic(StrFails()),
                      _unrepresentable_msg % ('StrFails', 'Failure in __str__'))


class TestSafeRepr(unittest.TestCase):

    def test_failure_in_repr(self):
        assert_equals(safe_repr(ReprFails()),
                      _unrepresentable_msg % ('ReprFails', 'Failure in __repr__'))


class UnicodeRepr:

    def __repr__(self):
        return u'Hyv\xe4'


class UnicodeFails(object):
    def __unicode__(self): raise RuntimeError('Failure in __unicode__')

class StrFails(object):
    def __unicode__(self): raise UnicodeError()
    def __str__(self): raise RuntimeError('Failure in __str__')

class ReprFails(object):
    def __repr__(self): raise RuntimeError('Failure in __repr__')

if __name__ == '__main__':
    unittest.main()
