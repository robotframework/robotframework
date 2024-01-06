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
        assert_equal([n.name for n in info.nested], ['int'])

    def test_multiple_parameters(self):
        info = TypeInfoParser('Mapping[str, int]').parse()
        assert_equal(info.name, 'Mapping')
        assert_equal([n.name for n in info.nested], ['str', 'int'])

    def test_trailing_comma_is_ok(self):
        info = TypeInfoParser('list[str,]').parse()
        assert_equal(info.name, 'list')
        assert_equal([n.name for n in info.nested], ['str'])
        info = TypeInfoParser('tuple[str, int, float,]').parse()
        assert_equal(info.name, 'tuple')
        assert_equal([n.name for n in info.nested], ['str', 'int', 'float'])

    def test_unrecognized_with_parameters(self):
        info = TypeInfoParser('x[y, z]').parse()
        assert_equal(info.name, 'x')
        assert_equal([n.name for n in info.nested], ['y', 'z'])

    def test_no_parameters(self):
        info = TypeInfoParser('x[]').parse()
        assert_equal(info.name, 'x')
        assert_equal(info.nested, ())

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

    def test_literal_with_unrecognized_name(self):
        info = TypeInfoParser("Literal[xxx, foo_bar, int, v4]").parse()
        assert_equal(len(info.nested), 4)
        for nested, value in zip(info.nested, ['xxx', 'foo_bar', 'int', 'v4']):
            assert_equal(nested.name, value)
            assert_equal(nested.type, None)

    def test_invalid_literal(self):
        for info, position, error in [
              ("Literal[1.0]",    11, "Invalid literal value '1.0'."),
              ("Literal[2x]",     10, "Invalid literal value '2x'."),
              ("Literal[3/0]",    11, "Invalid literal value '3/0'."),
              ("Literal['+', -]", 14, "Invalid literal value '-'."),
              ("Literal[']",   'end', "Invalid literal value \"']\"."),
              ("Literal[]",    'end', "Literal cannot be empty."),
              ("Literal[,]",       8, "Type missing before ','."),
              ("Literal[[1], 2]", 11, "Invalid literal value '[1]'."),
              ("Literal[1, []]",  13, "Invalid literal value '[]'."),
        ]:
            position = f'index {position}' if isinstance(position, int) else position
            assert_raises_with_msg(
                ValueError,
                f"Parsing type {info!r} failed: Error at {position}: {error}",
                TypeInfoParser(info).parse
            )

    def test_parens_instead_of_type_name(self):
        info = TypeInfoParser('Callable[[], None]').parse()
        assert_equal(info.name, 'Callable')
        assert_equal(info.nested[0].name, None)
        assert_equal(info.nested[0].nested, ())
        assert_equal(info.nested[1].name, 'None')
        info = TypeInfoParser('Callable[[str, int], float]').parse()
        assert_equal(info.name, 'Callable')
        assert_equal(info.nested[0].name, None)
        assert_equal(info.nested[0].nested[0].name, 'str')
        assert_equal(info.nested[0].nested[1].name, 'int')
        assert_equal(info.nested[1].name, 'float')
        info = TypeInfoParser('x[[], [[]], [[y]]]').parse()
        assert_equal(info.name, 'x')
        assert_equal(info.nested[0].name, None)
        assert_equal(info.nested[0].nested, ())
        assert_equal(info.nested[1].name, None)
        assert_equal(info.nested[1].nested[0].name, None)
        assert_equal(info.nested[1].nested[0].nested, ())
        assert_equal(info.nested[2].name, None)
        assert_equal(info.nested[2].nested[0].name, None)
        assert_equal(info.nested[2].nested[0].nested[0].name, 'y')

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
                ('x[',     'end', "Closing ']' missing."),
                ('x]',     1,     "Extra content after 'x'."),
                ('x,',     1,     "Extra content after 'x'."),
                ('x|',     'end', 'Type name missing.'),
                ('x[y][',  4,     "Extra content after 'x[y]'."),
                ('x[y]]',  4,     "Extra content after 'x[y]'."),
                ('x[y],',  4,     "Extra content after 'x[y]'."),
                ('x[y]|',  'end', 'Type name missing.'),
                ('x[y]z',  4,     "Extra content after 'x[y]'."),
                ('x[y',    'end', "Closing ']' missing."),
                ('x[y,',   'end', "Closing ']' missing."),
                ('x[y,z',  'end', "Closing ']' missing."),
                ('x[,',    2,     "Type missing before ','."),
                ('x[,]',   2,     "Type missing before ','."),
                ('x[y,,]', 4,     "Type missing before ','."),
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
