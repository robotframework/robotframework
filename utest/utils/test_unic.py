import unittest
import re

from robot.utils import unic, unicode, prepr, DotDict, JYTHON, IRONPYTHON, PY3
from robot.utils.asserts import assert_equal, assert_true


if JYTHON:

    from java.lang import String, Object, RuntimeException
    import JavaObject
    import UnicodeJavaLibrary


    class TestJavaUnic(unittest.TestCase):

        def test_with_java_object(self):
            data = u'This is unicode \xe4\xf6'
            assert_equal(unic(JavaObject(data)), data)

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
            class ToStringFails(Object, UnRepr):
                def toString(self):
                    raise RuntimeException(self.error)
            failing = ToStringFails()
            assert_equal(unic(failing), failing.unrepr)


class TestUnic(unittest.TestCase):

    if not (JYTHON or IRONPYTHON):
        def test_unicode_nfc_and_nfd_decomposition_equality(self):
            import unicodedata
            text = u'Hyv\xe4'
            assert_equal(unic(unicodedata.normalize('NFC', text)), text)
            # In Mac filesystem umlaut characters are presented in NFD-format.
            # This is to check that unic normalizes all strings to NFC
            assert_equal(unic(unicodedata.normalize('NFD', text)), text)

    def test_object_containing_unicode_repr(self):
        assert_equal(unic(UnicodeRepr()), u'Hyv\xe4')

    def test_list_with_objects_containing_unicode_repr(self):
        objects = [UnicodeRepr(), UnicodeRepr()]
        result = unic(objects)
        if JYTHON:
            # This is actually wrong behavior
            assert_equal(result, '[Hyv\\xe4, Hyv\\xe4]')
        elif IRONPYTHON or PY3:
            # And so is this.
            assert_equal(result, '[Hyv\xe4, Hyv\xe4]')
        elif PY3:
            assert_equal(result, '[Hyv\xe4, Hyv\xe4]')
        else:
            expected = UnRepr.format('list', 'UnicodeEncodeError: ')[:-1]
            assert_true(result.startswith(expected))

    def test_bytes_below_128(self):
        assert_equal(unic('\x00-\x01-\x02-\x7f'), u'\x00-\x01-\x02-\x7f')

    def test_bytes_above_128(self):
        assert_equal(unic(b'hyv\xe4'), u'hyv\\xe4')
        assert_equal(unic(b'\x00-\x01-\x02-\xe4'), u'\x00-\x01-\x02-\\xe4')

    def test_bytes_with_newlines_tabs_etc(self):
        assert_equal(unic(b"\x00\xe4\n\t\r\\'"), u"\x00\\xe4\n\t\r\\'")

    def test_bytearray(self):
        assert_equal(unic(bytearray(b'hyv\xe4')), u'hyv\\xe4')
        assert_equal(unic(bytearray(b'\x00-\x01-\x02-\xe4')), u'\x00-\x01-\x02-\\xe4')
        assert_equal(unic(bytearray(b"\x00\xe4\n\t\r\\'")), u"\x00\\xe4\n\t\r\\'")

    def test_failure_in_unicode(self):
        failing = UnicodeFails()
        assert_equal(unic(failing), failing.unrepr)

    def test_failure_in_str(self):
        failing = StrFails()
        assert_equal(unic(failing), failing.unrepr)


class TestPrettyRepr(unittest.TestCase):

    def _verify(self, item, expected=None, **config):
        if not expected:
            expected = repr(item).lstrip('u')
        assert_equal(prepr(item, **config), expected)
        if isinstance(item, (unicode, bytes)) and not config:
            assert_equal(prepr([item]), '[%s]' % expected)
            assert_equal(prepr((item,)), '(%s,)' % expected)
            assert_equal(prepr({item: item}), '{%s: %s}' % (expected, expected))
            assert_equal(prepr({item}), ('{%s}' if PY3 else 'set([%s])') % expected)

    def test_ascii_unicode(self):
        self._verify(u'foo', "'foo'")
        self._verify(u"f'o'o", "\"f'o'o\"")

    def test_non_ascii_unicode(self):
        self._verify(u'hyv\xe4', "'hyv\xe4'" if PY3 else "'hyv\\xe4'")

    def test_unicode_in_nfd(self):
        self._verify(u'hyva\u0308', "'hyv\xe4'" if PY3 else "'hyva\\u0308'")

    def test_ascii_bytes(self):
        self._verify(b'ascii', "b'ascii'")

    def test_non_ascii_bytes(self):
        self._verify(b'non-\xe4scii', "b'non-\\xe4scii'")

    def test_bytearray(self):
        self._verify(bytearray(b'foo'), "bytearray(b'foo')")

    def test_non_strings(self):
        for inp in [1, -2.0, True, None, -2.0, (), [], {},
                    StrFails(), UnicodeFails()]:
            self._verify(inp)

    def test_failing_repr(self):
        failing = ReprFails()
        self._verify(failing, failing.unrepr)

    def test_unicode_repr(self):
        obj = UnicodeRepr()
        if JYTHON:
            expected = 'Hyv\\xe4'
        elif IRONPYTHON or PY3:
            expected = u'Hyv\xe4'
        else:
            expected = obj.unrepr
        self._verify(obj, expected)

    def test_bytes_repr(self):
        obj = BytesRepr()
        if PY3 or IRONPYTHON:
            expected = obj.unrepr
        else:
            expected = 'Hyv\\xe4'
        self._verify(obj, expected)

    def test_collections(self):
        self._verify([u'foo', b'bar', 3], "['foo', b'bar', 3]")
        self._verify([u'foo', b'b\xe4r', (u'x', b'y')], "['foo', b'b\\xe4r', ('x', b'y')]")
        self._verify({u'x': b'\xe4'}, "{'x': b'\\xe4'}")
        self._verify([u'\xe4'], "['\xe4']" if PY3 else "['\\xe4']")
        self._verify({u'\xe4'}, "{'\xe4'}" if PY3 else "set(['\\xe4'])")

    def test_dotdict(self):
        self._verify(DotDict({u'x': b'\xe4'}), "{'x': b'\\xe4'}")

    def test_recursive(self):
        x = [1, 2]
        x.append(x)
        match = re.match(r'\[1, 2. <Recursion on list with id=\d+>\]', prepr(x))
        assert_true(match is not None)

    def test_split_big_collections(self):
        self._verify(list(range(20)))
        self._verify(list(range(100)), width=400)
        self._verify(list(range(100)),
                     '[%s]' % ',\n '.join(str(i) for i in range(100)))
        self._verify([u'Hello, world!'] * 4,
                     '[%s]' % ', '.join(["'Hello, world!'"] * 4))
        self._verify([u'Hello, world!'] * 25,
                     '[%s]' % ', '.join(["'Hello, world!'"] * 25), width=500)
        self._verify([u'Hello, world!'] * 25,
                     '[%s]' % ',\n '.join(["'Hello, world!'"] * 25))

    def test_dont_split_long_strings(self):
        self._verify(' '.join([u'Hello world!'] * 1000))
        self._verify(b' '.join([b'Hello world!'] * 1000),
                     "b'%s'" % ' '.join(['Hello world!'] * 1000))
        self._verify(bytearray(b' '.join([b'Hello world!'] * 1000)))


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
    def __str__(self):
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


class BytesRepr(UnRepr):

    def __init__(self):
        try:
            repr(self)
        except TypeError as err:
            self.error = 'TypeError: %s' % err

    def __repr__(self):
        return b'Hyv\xe4'


if __name__ == '__main__':
    unittest.main()
