import json
import unittest
from io import StringIO

from robot.utils.asserts import assert_equal, assert_raises
from robot.htmldata.jsonwriter import JsonDumper


class TestJsonDumper(unittest.TestCase):

    def _dump(self, data):
        output = StringIO()
        JsonDumper(output).dump(data)
        return output.getvalue()

    def _test(self, data, expected):
        assert_equal(self._dump(data), expected)

    def test_dump_string(self):
        self._test('', '""')
        self._test('hello world', '"hello world"')
        self._test('123', '"123"')

    def test_dump_non_ascii_string(self):
        self._test(u'hyv\xe4', u'"hyv\xe4"')

    def test_escape_string(self):
        self._test('"-\\-\n-\t-\r', '"\\"-\\\\-\\n-\\t-\\r"')

    def test_escape_closing_tags(self):
        self._test('<script><></script>', '"<script><>\\x3c/script>"')

    def test_dump_boolean(self):
        self._test(True, 'true')
        self._test(False, 'false')

    def test_dump_integer(self):
        self._test(12, '12')
        self._test(-12312, '-12312')
        self._test(0, '0')
        self._test(1, '1')

    def test_dump_long(self):
        self._test(12345678901234567890, '12345678901234567890')

    def test_dump_list(self):
        self._test([1, 2, True, 'hello', 'world'], '[1,2,true,"hello","world"]')
        self._test(['*nes"ted', [1, 2, [4]]], '["*nes\\"ted",[1,2,[4]]]')

    def test_dump_tuple(self):
        self._test(('hello', '*world'), '["hello","*world"]')
        self._test((1, 2, (3, 4)), '[1,2,[3,4]]')

    def test_dump_dictionary(self):
        self._test({'key': 1}, '{"key":1}')
        self._test({'nested': [-1, {42: None}]}, '{"nested":[-1,{42:null}]}')

    def test_dictionaries_are_sorted(self):
        self._test({'key': 1, 'hello': ['wor', 'ld'], 'z': 'a', 'a': 'z'},
                   '{"a":"z","hello":["wor","ld"],"key":1,"z":"a"}')

    def test_dump_none(self):
        self._test(None, 'null')

    def test_json_dump_mapping(self):
        output = StringIO()
        dumper = JsonDumper(output)
        mapped1 = object()
        mapped2 = 'string'
        dumper.dump([mapped1, [mapped2, {mapped2: mapped1}]],
                    mapping={mapped1: '1', mapped2: 'a'})
        assert_equal(output.getvalue(), '[1,[a,{a:1}]]')
        assert_raises(ValueError, dumper.dump, [mapped1])

    def test_against_standard_json(self):
        data = ['\\\'\"\r\t\n' + ''.join(chr(i) for i in range(32, 127)),
                {'A': 1, 'b': 2, 'C': ()}, None, (1, 2, 3)]
        expected = json.dumps(data, sort_keys=True, separators=(',', ':'))
        self._test(data, expected)


if __name__ == '__main__':
    unittest.main()
