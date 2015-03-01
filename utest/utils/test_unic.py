from six import PY3

import unittest
import re

from robot.utils import unic, prepr, DotDict, JYTHON, IRONPYTHON
from robot.utils.asserts import assert_equals, assert_true


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
            assert_true('Circle is 360' in next(iterator))

        def test_failure_in_toString(self):
            class ToStringFails(Object, UnRepr):
                def toString(self):
                    raise RuntimeException(self.error)
            failing = ToStringFails()
            assert_equals(unic(failing), failing.unrepr)


class TestUnic(unittest.TestCase):

    if not (JYTHON or IRONPYTHON):
        def test_unicode_nfc_and_nfd_decomposition_equality(self):
            import unicodedata
            text = u'Hyv\xe4'
            assert_equals(unic(unicodedata.normalize('NFC', text)), text)
            # In Mac filesystem umlaut characters are presented in NFD-format.
            # This is to check that unic normalizes all strings to NFC
            assert_equals(unic(unicodedata.normalize('NFD', text)), text)

    if not IRONPYTHON:
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
        elif IRONPYTHON or PY3:
            # And so is this.
            assert_equals(result, '[Hyv\xe4, Hyv\xe4]')
        else:
            expected = UnRepr.format('list', 'UnicodeEncodeError: ')[:-1]
            assert_true(result.startswith(expected))

    def test_bytes_below_128(self):
        assert_equals(unic('\x00-\x01-\x02-\x7f'), u'\x00-\x01-\x02-\x7f')

    if not (IRONPYTHON or PY3):

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

    if not PY3:
        def test_failure_in_unicode(self):
            failing = UnicodeFails()
            assert_equals(unic(failing), failing.unrepr)

    def test_failure_in_str(self):
        failing = StrFails()
        assert_equals(unic(failing), failing.unrepr)


class TestPrettyRepr(unittest.TestCase):

    def _verify(self, item, expected=None):
        if not expected:
            expected = repr(item)
        elif (IRONPYTHON or PY3) and "b'" in expected:
            expected = expected.replace("b'", "'")
        assert_equals(prepr(item), expected)

    def test_no_u_prefix(self):
        self._verify(u'foo', "'foo'")
        self._verify(u"f'o'o", "\"f'o'o\"")
        self._verify(u'hyv\xe4', "'hyv\\xe4'")

    def test_b_prefix(self):
        self._verify('foo', "b'foo'")
        self._verify('hyv\xe4', "b'hyv\\xe4'")

    def test_non_strings(self):
        for inp in [1, -2.0, True, None, -2.0, (), [], {},
                    StrFails(), UnicodeFails()]:
            self._verify(inp)

    def test_failing_repr(self):
        failing = ReprFails()
        self._verify(failing, failing.unrepr)

    def test_unicode_repr(self):
        invalid = UnicodeRepr()
        if JYTHON:
            expected = 'Hyv\\xe4'
        elif IRONPYTHON or PY3:
            expected = u'Hyv\xe4'
        else:
            expected = invalid.unrepr  # This is correct.
        self._verify(invalid, expected)

    def test_non_ascii_repr(self):
        non_ascii = NonAsciiRepr()
        if IRONPYTHON or PY3:
            expected = u'Hyv\xe4'
        else:
            expected = 'Hyv\\xe4'  # This is correct.
        self._verify(non_ascii, expected)

    def test_collections(self):
        self._verify([u'foo', 'bar', 3], "['foo', b'bar', 3]")
        self._verify([u'foo', 'bar', (u'x', 'y')], "['foo', b'bar', ('x', b'y')]")
        inp1, inp2 = ReprFails(), StrFails()
        exp1, exp2 = inp1.unrepr, repr(inp2)
        self._verify((inp1, inp2, [inp1]),
                     '(%s, %s, [%s])' % (exp1, exp2, exp1))
        self._verify({'x': 1, 2: u'y'},
                     "{2: 'y', b'x': 1}")
        self._verify({1: inp1, None: ()},
                     '{None: (), 1: %s}' % exp1)

    def test_dotdict(self):
        self._verify(DotDict({'x': 1, 2: u'y'}),
                     "{2: 'y', b'x': 1}")

    def test_recursive(self):
        x = [1, 2]
        x.append(x)
        match = re.match(r'\[1, 2. <Recursion on list with id=\d+>\]', prepr(x))
        assert_true(match is not None)

    def test_split_big_collections(self):
        self._verify(range(100))
        self._verify([u'Hello, world!'] * 10,
                     '[%s]' % ', '.join(["'Hello, world!'"] * 10))
        self._verify(range(300),
                     '[%s]' % ',\n '.join(str(i) for i in range(300)))
        self._verify([u'Hello, world!'] * 30,
                     '[%s]' % ',\n '.join(["'Hello, world!'"] * 30))


class UnRepr(object):
    error = 'This, of course, should never happen...'

    @property
    def unrepr(self):
        return self.format(type(self).__name__, self.error)

    @staticmethod
    def format(name, error):
        return "<Unrepresentable object %s. Error: %s>" % (name, error)


class UnicodeFails(UnRepr):
    def __unicode__(self):
        raise RuntimeError(self.error)


class StrFails(UnRepr):
    def __unicode__(self):
        raise UnicodeError()
    def __str__(self):
        raise RuntimeError(self.error)


class ReprFails(UnRepr):
    def __repr__(self):
        raise RuntimeError(self.error)


class UnicodeRepr(UnRepr):

    def __init__(self):
        try:
            repr(self)
        except UnicodeEncodeError as err:
            self.error = 'UnicodeEncodeError: %s' % err

    def __repr__(self):
        return u'Hyv\xe4'


class NonAsciiRepr(UnRepr):

    def __init__(self):
        try:
            repr(self)
        except UnicodeEncodeError as err:
            self.error = 'UnicodeEncodeError: %s' % err

    def __repr__(self):
        return 'Hyv\xe4'


if __name__ == '__main__':
    unittest.main()
