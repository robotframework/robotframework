import StringIO
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None
import unittest
from robot.utils.asserts import assert_equals, assert_true
from robot.result.json import json_dump

class JsonTestCase(unittest.TestCase):

    if json:
        def test_json_dump_string(self):
            string = u'string\u00A9\v\\\'\"\r\b\t\0\n\fjee'
            for i in range(1024):
                string += unichr(i)
            buffer = StringIO.StringIO()
            json_dump(string, buffer)
            expected = StringIO.StringIO()
            json.dump(string, expected)
            assert_equals(buffer.getvalue(), expected.getvalue())

    def test_json_dump_integer(self):
        buffer = StringIO.StringIO()
        json_dump(12, buffer)
        assert_equals('12', buffer.getvalue())

    def test_json_dump_long(self):
        buffer = StringIO.StringIO()
        json_dump(12345678901234567890L, buffer)
        assert_equals('12345678901234567890', buffer.getvalue())

    def test_json_dump_list(self):
        buffer = StringIO.StringIO()
        json_dump([1,2,3, 'hello', 'world'], buffer)
        assert_equals('[1,2,3,"hello","world"]', buffer.getvalue())

    def test_json_dump_dictionary(self):
        buffer = StringIO.StringIO()
        json_dump({'key': 1}, buffer)
        assert_equals(buffer.getvalue(), '{"key":1}')

    def test_json_dictionaries_are_sorted(self):
        buffer = StringIO.StringIO()
        json_dump({'key':1, 'hello':['wor','ld'], 'z': 'a', 'a': 'z'}, buffer)
        assert_equals(buffer.getvalue(),
                      '{"a":"z","hello":["wor","ld"],"key":1,"z":"a"}')

    def test_json_dump_None(self):
        buffer = StringIO.StringIO()
        json_dump(None, buffer)
        assert_equals('null', buffer.getvalue())

    def test_json_dump_mapping(self):
        buffer = StringIO.StringIO()
        mapped1 = object()
        mapped2 = object()
        json_dump([mapped1, [mapped2, {mapped2:mapped1}]], buffer,
                  mappings={mapped1:'1', mapped2:'a'})
        assert_equals('[1,[a,{a:1}]]', buffer.getvalue())


if __name__ == '__main__':
    unittest.main()
