from StringIO import StringIO
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None
import unittest

from robot.utils.asserts import assert_equals, assert_raises
from robot.result.jsondump import JsonDumper
from robot.utils.abstractxmlwriter import _ILLEGAL_CHARS_IN_XML


class JsonTestCase(unittest.TestCase):

    def _dump(self, data):
        output = StringIO()
        JsonDumper(output).dump(data)
        return output.getvalue()

    def _test(self, data, expected):
        assert_equals(self._dump(data), expected)

    def test_dump_string(self):
        self._test('', '""')
        self._test('xxx', '"xxx"')
        self._test('123', '"123"')

    def test_dump_non_ascii_string(self):
        self._test(u'hyv\xe4', '"hyv\\u00e4"')

    def test_escape_string(self):
        self._test('"-\\-\n-\t-\r', '"\\"-\\\\-\\n-\\t-\\r"')

    def test_dump_integer(self):
        self._test(12, '12')
        self._test(-12312, '-12312')
        self._test(0, '0')

    def test_dump_long(self):
        self._test(12345678901234567890L, '12345678901234567890')
        self._test(0L, '0')

    def test_dump_list(self):
        self._test([1,2,3, 'hello', 'world'], '[1,2,3,"hello","world"]')
        self._test(['nested', [1,2,[4]]], '["nested",[1,2,[4]]]')

    def test_dump_other_iterables(self):
        self._test((1,2,(3,4)), '[1,2,[3,4]]')
        self._test(xrange(5), '[0,1,2,3,4]')

    def test_dump_dictionary(self):
        self._test({'key': 1}, '{"key":1}')
        self._test({'nested': [-1L, {42: None}]}, '{"nested":[-1,{42:null}]}')

    def test_dictionaries_are_sorted(self):
        self._test({'key':1, 'hello':['wor','ld'], 'z': 'a', 'a': 'z'},
                   '{"a":"z","hello":["wor","ld"],"key":1,"z":"a"}')

    def test_dump_none(self):
        self._test(None, 'null')

    def test_json_dump_mapping(self):
        output = StringIO()
        dumper = JsonDumper(output)
        mapped1 = object()
        mapped2 = 'string'
        dumper.dump([mapped1, [mapped2, {mapped2: mapped1}]],
                    mapping={mapped1:'1', mapped2:'a'})
        assert_equals(output.getvalue(),  '[1,[a,{a:1}]]')
        assert_raises(ValueError, dumper.dump, [mapped1])

    if json:
        def test_agains_standard_json(self):
            string = u'string\u00A9\v\\\'\"\r\t\njee'
            for i in range(1024):
                c = unichr(i)
                if c not in _ILLEGAL_CHARS_IN_XML:
                    string += c
            data = [string, {'A': 1}, None]
            expected = StringIO()
            json.dump(data, expected, separators=(',', ':'))
            self._test(data, expected.getvalue())


if __name__ == '__main__':
    unittest.main()
