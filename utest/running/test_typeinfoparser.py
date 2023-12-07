import unittest
from typing import Literal

from robot.running.arguments.typeinfoparser import TypeInfoParser, TypeInfoTokenizer
from robot.utils.asserts import assert_equal, assert_raises_with_msg


class TestTypeInfoTokenizer(unittest.TestCase):

    def test_quotes(self):
        for value in "'hi'", '"hi"', "'h, i'", '"[h|i]"', '"\'hi\'"', "'\"hi\"'":
            token, = TypeInfoTokenizer(value).tokenize()
            assert_equal(token.value, value)
            token, = TypeInfoTokenizer('b' + value).tokenize()
            assert_equal(token.value, 'b' + value)


class TestTypeInfoParser(unittest.TestCase):

    def test_simple(self):
        for name in 'str', 'Integer', 'whatever', 'two parts', 'non-alpha!?':
            info = TypeInfoParser(name).parse()
            assert_equal(info.name, name)

    def test_parameterized(self):
        info = TypeInfoParser('list[int]').parse()
        assert_equal(info.name, 'list')
        assert_equal(info.nested[0].name, 'int')

    def test_multiple_parameters(self):
        info = TypeInfoParser('Mapping[str, int]').parse()
        assert_equal(info.name, 'Mapping')
        assert_equal(info.nested[0].name, 'str')
        assert_equal(info.nested[1].name, 'int')

    def test_union(self):
        info = TypeInfoParser('int | float').parse()
        assert_equal(info.name, 'Union')
        assert_equal(info.nested[0].name, 'int')
        assert_equal(info.nested[1].name, 'float')

    def test_union_with_multiple_types(self):
        types = list('abcdefg')
        info = TypeInfoParser('|'.join(types)).parse()
        assert_equal(info.name, 'Union')
        assert_equal(len(info.nested), 7)
        for nested, name in zip(info.nested, types):
            assert_equal(nested.name, name)

    def test_literal(self):
        info = TypeInfoParser("Literal[1, '2', \"3\", b'4', True, None, '']").parse()
        assert_equal(info.name, 'Literal')
        assert_equal(info.type, Literal)
        assert_equal(len(info.nested), 7)
        for nested, value in zip(info.nested, [1, '2', '3', b'4', True, None, '']):
            assert_equal(nested.name, repr(value))
            assert_equal(nested.type, value)

    def test_markers_in_literal_values(self):
        info = TypeInfoParser("Literal[',', \"|\", '[', ']', '\"', \"'\"]").parse()
        assert_equal(info.name, 'Literal')
        assert_equal(info.type, Literal)
        assert_equal(len(info.nested), 6)
        for nested, value in zip(info.nested, [',', '|', '[', ']', '"', "'"]):
            assert_equal(nested.name, repr(value))
            assert_equal(nested.type, value)

    def test_invalid_literal(self):
        for info, index, error in [
              ("Literal['ok', bad]", 14, "Invalid literal value 'bad'."),
              ("Literal[1.0]",        8, "Invalid literal value '1.0'."),
              ("Literal[1/0]",        8, "Invalid literal value '1/0'."),
              ("Literal['+', -]",    13, "Invalid literal value '-'."),
              ("Literal[']",          8, "Invalid literal value \"']\"."),
              ("Literal[]",           8, "Type name missing."),
              ("Literal[,]",          8, "Type name missing."),
        ]:
            assert_raises_with_msg(
                ValueError,
                f"Parsing type {info!r} failed: Error at index {index}: {error}",
                TypeInfoParser(info).parse
            )

    def test_mixed(self):
        info = TypeInfoParser('int | list[int] |tuple[int,int|tuple[int, int|str]]').parse()
        assert_equal(info.name, 'Union')
        assert_equal(info.nested[0].name, 'int')
        assert_equal(info.nested[1].name, 'list')
        assert_equal(info.nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].name, 'tuple')
        assert_equal(info.nested[2].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].name, 'Union')
        assert_equal(info.nested[2].nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].nested[1].name, 'tuple')
        assert_equal(info.nested[2].nested[1].nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].nested[1].nested[1].name, 'Union')
        assert_equal(info.nested[2].nested[1].nested[1].nested[1].nested[0].name, 'int')
        assert_equal(info.nested[2].nested[1].nested[1].nested[1].nested[1].name, 'str')

    def test_errors(self):
        for info, position, error in [
                ('',       'end', 'Type name missing.'),
                ('[',      0,     'Type name missing.'),
                (']',      0,     'Type name missing.'),
                (',',      0,     'Type name missing.'),
                ('|',      0,     'Type name missing.'),
                ('x[',     'end', 'Type name missing.'),
                ('x]',     1,     "Extra content after 'x'."),
                ('x,',     1,     "Extra content after 'x'."),
                ('x|',     'end', 'Type name missing.'),
                ('x[y][',  4,     "Extra content after 'x[y]'."),
                ('x[y]]',  4,     "Extra content after 'x[y]'."),
                ('x[y],',  4,     "Extra content after 'x[y]'."),
                ('x[y]|',  'end', 'Type name missing.'),
                ('x[y]z',  4,     "Extra content after 'x[y]'."),
                ('x[y',    'end', "Closing ']' missing."),
                ('x[y,',   'end', 'Type name missing.'),
                ('x[y,z',  'end', "Closing ']' missing."),
                ('x[,',    2,     'Type name missing.'),
                ('x[[y]]', 2,     'Type name missing.'),
                ('x | ,',  4,     'Type name missing.'),
                ('x|||',   2,     'Type name missing.'),
                ('"x"y',   3,     'Extra content after \'"x"\'.'),
        ]:
            position = f'index {position}' if isinstance(position, int) else position
            assert_raises_with_msg(
                ValueError,
                f"Parsing type '{info}' failed: Error at {position}: {error}",
                TypeInfoParser(info).parse
            )


if __name__ == '__main__':
    unittest.main()
