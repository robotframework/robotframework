# encoding=utf-8

import unittest
from enum import Enum

from robot.running.arguments.argumentspec import ArgumentSpec, ArgInfo
from robot.utils.asserts import assert_equal
from robot.utils import unicode


class TestStringRepr(unittest.TestCase):

    def test_empty(self):
        self._verify('')

    def test_normal_only(self):
        self._verify('a, b', positional=['a', 'b'])

    def test_non_ascii_names(self):
        self._verify(u'nön, äscii', positional=[u'nön', u'äscii'])

    def test_default(self):
        self._verify('a, b=c', positional=['a', 'b'], defaults={'b': 'c'})
        self._verify(u'nön=äscii', positional=[u'nön'], defaults={u'nön': u'äscii'})
        self._verify('i=42', positional=['i'], defaults={'i': 42})

    def test_default_as_bytes(self):
        self._verify('b=ytes', positional=['b'], defaults={'b': b'ytes'})
        self._verify(u'ä=\\xe4', positional=[u'ä'], defaults={u'ä': b'\xe4'})

    def test_type_as_class(self):
        self._verify('a: int, b: bool', positional=['a', 'b'],
                     types={'a': int, 'b': bool})

    def test_type_as_string(self):
        self._verify('a: Integer, b: Boolean', positional=['a', 'b'],
                     types={'a': 'Integer', 'b': 'Boolean'})

    def test_type_and_default(self):
        self._verify('arg: int = 1', positional=['arg'], types=[int],
                     defaults={'arg': 1})

    def test_varargs(self):
        self._verify('*varargs', varargs='varargs')
        self._verify('a, *b', positional=['a'], varargs='b')

    def test_kwonly_without_varargs(self):
        self._verify('*, kwo', kwonlyargs=['kwo'])

    def test_kwonly_with_varargs(self):
        self._verify('*varargs, k1, k2', varargs='varargs', kwonlyargs=['k1', 'k2'])

    def test_kwonly_with_default(self):
        self._verify('*, k=1, w, o=3', kwonlyargs=['k', 'w', 'o'], defaults={'k': 1, 'o': 3})

    def test_kwargs(self):
        self._verify('**kws', kwargs='kws')
        self._verify('a, b=c, *d, e=f, g, **h', positional=['a', 'b'], varargs='d',
                     kwonlyargs=['e', 'g'], kwargs='h', defaults={'b': 'c', 'e': 'f'})

    def test_enum_with_few_members(self):
        class Small(Enum):
            ONLY_FEW_MEMBERS = 1
            SO_THEY_CAN = 2
            BE_PRETTY_LONG = 3
        self._verify('e: Small { ONLY_FEW_MEMBERS | SO_THEY_CAN | BE_PRETTY_LONG }',
                     positional=['e'], types=[Small])

    def test_enum_with_many_short_members(self):
        class ManyShort(Enum):
            ONE = 1
            TWO = 2
            THREE = 3
            FOUR = 4
            FIVE = 5
            SIX = 6
        self._verify('e: ManyShort { ONE | TWO | THREE | FOUR | FIVE | SIX }',
                     positional=['e'], types=[ManyShort])

    def test_enum_with_many_long_members(self):
        class Big(Enum):
            MANY_MEMBERS = 1
            THAT_ARE_LONGISH = 2
            MEANS_THEY_ALL_DO_NOT_FIT = 3
            AND_SOME_ARE_OMITTED = 4
            FROM_THE_END = 5
        self._verify('e: Big { MANY_MEMBERS | THAT_ARE_LONGISH | ... }',
                     positional=['e'], types=[Big])

    def _verify(self, expected, **spec):
        assert_equal(unicode(ArgumentSpec(**spec)), expected)


class TestArgInfo(unittest.TestCase):

    def test_required_without_default(self):
        for kind in (ArgInfo.POSITIONAL_OR_KEYWORD,
                     ArgInfo.KEYWORD_ONLY):
            assert_equal(ArgInfo(kind).required, True)
            assert_equal(ArgInfo(kind, default=None).required, False)

    def test_never_required(self):
        for kind in (ArgInfo.VAR_POSITIONAL,
                     ArgInfo.VAR_KEYWORD,
                     ArgInfo.KEYWORD_ONLY_MARKER):
            assert_equal(ArgInfo(kind).required, False)


if __name__ == '__main__':
    unittest.main()
