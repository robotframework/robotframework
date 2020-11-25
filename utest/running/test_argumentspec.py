# encoding=utf-8

import unittest
from enum import Enum

from robot.running.arguments.argumentspec import ArgumentSpec, ArgInfo
from robot.utils.asserts import assert_equal
from robot.utils import unicode


class TestStringRepr(unittest.TestCase):

    def test_empty(self):
        self._verify('')

    def test_normal(self):
        self._verify('a, b', ['a', 'b'])

    def test_non_ascii_names(self):
        self._verify(u'nön, äscii', [u'nön', u'äscii'])

    def test_default(self):
        self._verify('a, b=c', ['a', 'b'], defaults={'b': 'c'})
        self._verify(u'nön=äscii', [u'nön'], defaults={u'nön': u'äscii'})
        self._verify('i=42', ['i'], defaults={'i': 42})

    def test_default_as_bytes(self):
        self._verify('b=ytes', ['b'], defaults={'b': b'ytes'})
        self._verify(u'ä=\\xe4', [u'ä'], defaults={u'ä': b'\xe4'})

    def test_type_as_class(self):
        self._verify('a: int, b: bool', ['a', 'b'], types={'a': int, 'b': bool})

    def test_type_as_string(self):
        self._verify('a: Integer, b: Boolean', ['a', 'b'],
                     types={'a': 'Integer', 'b': 'Boolean'})

    def test_type_and_default(self):
        self._verify('arg: int = 1', ['arg'], types=[int], defaults={'arg': 1})

    def test_positional_only(self):
        self._verify('a, /', positional_only=['a'])
        self._verify('a, /, b', positional_only=['a'], positional_or_named=['b'])

    def test_positional_only_with_default(self):
        self._verify('a, b=2, /', positional_only=['a', 'b'], defaults={'b': 2})

    def test_positional_only_with_type(self):
        self._verify('a: int, b, /', positional_only=['a', 'b'], types=[int])
        self._verify('a: int, b: float, /, c: bool, d',
                     positional_only=['a', 'b'],
                     positional_or_named=['c', 'd'],
                     types=[int, float, bool])

    def test_positional_only_with_type_and_default(self):
        self._verify('a: int = 1, b=2, /',
                     positional_only=['a', 'b'],
                     types={'a': int},
                     defaults={'a': 1, 'b': 2})

    def test_varargs(self):
        self._verify('*varargs',
                     var_positional='varargs')
        self._verify('a, *b',
                     positional_or_named=['a'],
                     var_positional='b')

    def test_varargs_with_type(self):
        self._verify('*varargs: float',
                     var_positional='varargs',
                     types={'varargs': float})
        self._verify('a: int, *b: list[int]',
                     positional_or_named=['a'],
                     var_positional='b',
                     types=[int, 'list[int]'])

    def test_named_only_without_varargs(self):
        self._verify('*, kwo',
                     named_only=['kwo'])

    def test_named_only_with_varargs(self):
        self._verify('*varargs, k1, k2',
                     var_positional='varargs',
                     named_only=['k1', 'k2'])

    def test_named_only_with_default(self):
        self._verify('*, k=1, w, o=3',
                     named_only=['k', 'w', 'o'],
                     defaults={'k': 1, 'o': 3})

    def test_named_only_with_types(self):
        self._verify('*, k: int, w: float, o',
                     named_only=['k', 'w', 'o'],
                     types=[int, float])
        self._verify('x: int, *y: float, z: bool',
                     positional_or_named=['x'],
                     var_positional='y',
                     named_only=['z'],
                     types=[int, float, bool])

    def test_named_only_with_types_and_defaults(self):
        self._verify('x: int = 1, *, y: float, z: bool = 3',
                     positional_or_named=['x'],
                     named_only=['y', 'z'],
                     types=[int, float, bool],
                     defaults={'x': 1, 'z': 3})

    def test_kwargs(self):
        self._verify('**kws',
                     var_named='kws')
        self._verify('a, b=c, *d, e=f, g, **h',
                     positional_or_named=['a', 'b'],
                     var_positional='d',
                     named_only=['e', 'g'],
                     var_named='h',
                     defaults={'b': 'c', 'e': 'f'})

    def test_kwargs_with_types(self):
        self._verify('**kws: dict[str, int]',
                     var_named='kws',
                     types={'kws': 'dict[str, int]'})
        self._verify('a: int, /, b: float, *c: list[int], d: bool, **e: dict[int, str]',
                     positional_only=['a'],
                     positional_or_named=['b'],
                     var_positional='c',
                     named_only=['d'],
                     var_named='e',
                     types=[int, float, 'list[int]', bool, 'dict[int, str]'])

    def test_enum_with_few_members(self):
        class Small(Enum):
            ONLY_FEW_MEMBERS = 1
            SO_THEY_CAN = 2
            BE_PRETTY_LONG = 3
        self._verify('e: Small',
                     ['e'], types=[Small])

    def test_enum_with_many_short_members(self):
        class ManyShort(Enum):
            ONE = 1
            TWO = 2
            THREE = 3
            FOUR = 4
            FIVE = 5
            SIX = 6
        self._verify('e: ManyShort',
                     ['e'], types=[ManyShort])

    def test_enum_with_many_long_members(self):
        class Big(Enum):
            MANY_MEMBERS = 1
            THAT_ARE_LONGISH = 2
            MEANS_THEY_ALL_DO_NOT_FIT = 3
            AND_SOME_ARE_OMITTED = 4
            FROM_THE_END = 5
        self._verify('e: Big',
                     ['e'], types=[Big])

    def _verify(self, expected, positional_or_named=None, **config):
        spec = ArgumentSpec(positional_or_named=positional_or_named, **config)
        assert_equal(unicode(spec), expected)


class TestArgInfo(unittest.TestCase):

    def test_required_without_default(self):
        for kind in (ArgInfo.POSITIONAL_ONLY,
                     ArgInfo.POSITIONAL_OR_NAMED,
                     ArgInfo.NAMED_ONLY):
            assert_equal(ArgInfo(kind).required, True)
            assert_equal(ArgInfo(kind, default=None).required, False)

    def test_never_required(self):
        for kind in (ArgInfo.VAR_POSITIONAL,
                     ArgInfo.VAR_NAMED,
                     ArgInfo.POSITIONAL_ONLY_MARKER,
                     ArgInfo.NAMED_ONLY_MARKER):
            assert_equal(ArgInfo(kind).required, False)


if __name__ == '__main__':
    unittest.main()
