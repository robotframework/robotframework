import unittest
import re

from robot.utils import safe_str, prepr, DotDict
from robot.utils.asserts import assert_equal, assert_true


class TestSafeStr(unittest.TestCase):

    def test_unicode_nfc_and_nfd_decomposition_equality(self):
        import unicodedata
        text = 'Hyvä'
        assert_equal(safe_str(unicodedata.normalize('NFC', text)), text)
        # In Mac filesystem umlaut characters are presented in NFD-format.
        # This is to check that unic normalizes all strings to NFC
        assert_equal(safe_str(unicodedata.normalize('NFD', text)), text)

    def test_object_containing_unicode_repr(self):
        assert_equal(safe_str(NonAsciiRepr()), 'Hyvä')

    def test_list_with_objects_containing_unicode_repr(self):
        objects = [NonAsciiRepr(), NonAsciiRepr()]
        result = safe_str(objects)
        assert_equal(result, '[Hyvä, Hyvä]')

    def test_bytes_below_128(self):
        assert_equal(safe_str('\x00-\x01-\x02-\x7f'), '\x00-\x01-\x02-\x7f')

    def test_bytes_above_128(self):
        assert_equal(safe_str(b'hyv\xe4'), 'hyv\\xe4')
        assert_equal(safe_str(b'\x00-\x01-\x02-\xe4'), '\x00-\x01-\x02-\\xe4')

    def test_bytes_with_newlines_tabs_etc(self):
        assert_equal(safe_str(b"\x00\xe4\n\t\r\\'"), "\x00\\xe4\n\t\r\\'")

    def test_bytearray(self):
        assert_equal(safe_str(bytearray(b'hyv\xe4')), 'hyv\\xe4')
        assert_equal(safe_str(bytearray(b'\x00-\x01-\x02-\xe4')), '\x00-\x01-\x02-\\xe4')
        assert_equal(safe_str(bytearray(b"\x00\xe4\n\t\r\\'")), "\x00\\xe4\n\t\r\\'")

    def test_failure_in_str(self):
        failing = StrFails()
        assert_equal(safe_str(failing), failing.unrepr)


class TestPrettyRepr(unittest.TestCase):

    def _verify(self, item, expected=None, **config):
        if not expected:
            expected = repr(item).lstrip('')
        assert_equal(prepr(item, **config), expected)
        if isinstance(item, (str, bytes)) and not config:
            assert_equal(prepr([item]), '[%s]' % expected)
            assert_equal(prepr((item,)), '(%s,)' % expected)
            assert_equal(prepr({item: item}), '{%s: %s}' % (expected, expected))
            assert_equal(prepr({item}), '{%s}' % expected)

    def test_ascii_string(self):
        self._verify('foo', "'foo'")
        self._verify("f'o'o", "\"f'o'o\"")

    def test_non_ascii_string(self):
        self._verify('hyvä', "'hyvä'")

    def test_string_in_nfd(self):
        self._verify('hyva\u0308', "'hyvä'")

    def test_ascii_bytes(self):
        self._verify(b'ascii', "b'ascii'")

    def test_non_ascii_bytes(self):
        self._verify(b'non-\xe4scii', "b'non-\\xe4scii'")

    def test_bytearray(self):
        self._verify(bytearray(b'foo'), "bytearray(b'foo')")

    def test_non_strings(self):
        for inp in [1, -2.0, True, None, -2.0, (), [], {}, StrFails()]:
            self._verify(inp)

    def test_failing_repr(self):
        failing = ReprFails()
        self._verify(failing, failing.unrepr)

    def test_non_ascii_repr(self):
        obj = NonAsciiRepr()
        self._verify(obj, 'Hyvä')

    def test_bytes_repr(self):
        obj = BytesRepr()
        self._verify(obj, obj.unrepr)

    def test_collections(self):
        self._verify(['foo', b'bar', 3], "['foo', b'bar', 3]")
        self._verify(['foo', b'b\xe4r', ('x', b'y')], "['foo', b'b\\xe4r', ('x', b'y')]")
        self._verify({'x': b'\xe4'}, "{'x': b'\\xe4'}")
        self._verify(['ä'], "['ä']")
        self._verify({'ä'}, "{'ä'}")

    def test_dont_sort_dicts_by_default(self):
        self._verify({'x': 1, 'D': 2, 'ä': 3, 'G': 4, 'a': 5},
                     "{'x': 1, 'D': 2, 'ä': 3, 'G': 4, 'a': 5}")
        self._verify({'a': 1, 1: 'a'}, "{'a': 1, 1: 'a'}")

    def test_allow_sorting_dicts(self):
        self._verify({'x': 1, 'D': 2, 'ä': 3, 'G': 4, 'a': 5},
                     "{'D': 2, 'G': 4, 'a': 5, 'x': 1, 'ä': 3}", sort_dicts=True)
        self._verify({'a': 1, 1: 'a'}, "{1: 'a', 'a': 1}", sort_dicts=True)

    def test_dotdict(self):
        self._verify(DotDict({'x': b'\xe4'}), "{'x': b'\\xe4'}")

    def test_recursive(self):
        x = [1, 2]
        x.append(x)
        match = re.match(r'\[1, 2. <Recursion on list with id=\d+>]', prepr(x))
        assert_true(match is not None)

    def test_split_big_collections(self):
        self._verify(list(range(20)))
        self._verify(list(range(100)), width=400)
        self._verify(list(range(100)),
                     '[%s]' % ',\n '.join(str(i) for i in range(100)))
        self._verify(['Hello, world!'] * 4,
                     '[%s]' % ', '.join(["'Hello, world!'"] * 4))
        self._verify(['Hello, world!'] * 25,
                     '[%s]' % ', '.join(["'Hello, world!'"] * 25), width=500)
        self._verify(['Hello, world!'] * 25,
                     '[%s]' % ',\n '.join(["'Hello, world!'"] * 25))

    def test_dont_split_long_strings(self):
        self._verify(' '.join(['Hello world!'] * 1000))
        self._verify(b' '.join([b'Hello world!'] * 1000),
                     "b'%s'" % ' '.join(['Hello world!'] * 1000))
        self._verify(bytearray(b' '.join([b'Hello world!'] * 1000)))


class UnRepr:
    error = 'This, of course, should never happen...'

    @property
    def unrepr(self):
        return self.format(type(self).__name__, self.error)

    @staticmethod
    def format(name, error):
        return "<Unrepresentable object %s. Error: %s>" % (name, error)


class StrFails(UnRepr):
    def __str__(self):
        raise RuntimeError(self.error)


class ReprFails(UnRepr):
    def __repr__(self):
        raise RuntimeError(self.error)


class NonAsciiRepr(UnRepr):

    def __init__(self):
        try:
            repr(self)
        except UnicodeEncodeError as err:
            self.error = f'UnicodeEncodeError: {err}'

    def __repr__(self):
        return 'Hyvä'


class BytesRepr(UnRepr):

    def __init__(self):
        try:
            repr(self)
        except TypeError as err:
            self.error = f'TypeError: {err}'

    def __repr__(self):
        return b'Hyv\xe4'


if __name__ == '__main__':
    unittest.main()
