from datetime import date, datetime
from typing import Dict, List, Set, Tuple, Union
from types import ModuleType
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from robot.api.deco import not_keyword


not_keyword(TypedDict)


class Number:
    pass


def string_to_int(value: str) -> int:
    try:
        return ['zero', 'one', 'two', 'three', 'four'].index(value.lower())
    except ValueError:
        raise ValueError(f"Don't know number {value!r}.")


class String:
    pass


def int_to_string_with_lib(value: int, library) -> str:
    if library is None:
        raise AssertionError('Expected library, got none')
    if not isinstance(library, ModuleType):
        raise AssertionError(f'Expected library to be instance of {ModuleType}, was {type(library)}')
    return str(value)


def parse_bool(value: Union[str, int, bool]):
    if isinstance(value, str):
        value = value.lower()
    return value not in ['false', '', 'epätosi', '\u2639', False, 0]


class UsDate(date):
    @classmethod
    def from_string(cls, value) -> date:
        if not isinstance(value, str):
            raise TypeError("Only strings accepted!")
        try:
            return cls.fromordinal(datetime.strptime(value, '%m/%d/%Y').toordinal())
        except ValueError:
            raise ValueError("Value does not match '%m/%d/%Y'.")


class FiDate(date):
    @classmethod
    def from_string(cls, value: str, ign1=None, *ign2, ign3=None, **ign4):
        try:
            return cls.fromordinal(datetime.strptime(value, '%d.%m.%Y').toordinal())
        except ValueError:
            raise RuntimeError("Value does not match '%d.%m.%Y'.")


class ClassAsConverter:
    def __init__(self, name):
        self.greeting = f'Hello, {name}!'


class ClassWithHintsAsConverter:
    name: str

    def __init__(self, value: Union[int, str]):
        self.value = value


class AcceptSubscriptedGenerics:
    def __init__(self, numbers: List[int]):
        self.sum = sum(numbers)


class OnlyVarArg:
    def __init__(self, *varargs):
        self.value = varargs[0]
        library = varargs[1]
        if library is None:
            raise AssertionError('Expected library, got none')
        if not isinstance(library, ModuleType):
            raise AssertionError(f'Expected library to be instance of {ModuleType}, was {type(library)}')


class Strict:
    pass


class Invalid:
    pass


class TooFewArgs:
    pass


class TooManyArgs:
    def __init__(self, one, two, three):
        pass


class NoPositionalArg:
    def __init__(self, *, args):
        pass


class KwOnlyNotOk:
    def __init__(self, arg, *, kwo, another):
        pass


ROBOT_LIBRARY_CONVERTERS = {Number: string_to_int,
                            bool: parse_bool,
                            String: int_to_string_with_lib,
                            UsDate: UsDate.from_string,
                            FiDate: FiDate.from_string,
                            ClassAsConverter: ClassAsConverter,
                            ClassWithHintsAsConverter: ClassWithHintsAsConverter,
                            AcceptSubscriptedGenerics: AcceptSubscriptedGenerics,
                            OnlyVarArg: OnlyVarArg,
                            Strict: None,
                            Invalid: 666,
                            TooFewArgs: TooFewArgs,
                            TooManyArgs: TooManyArgs,
                            NoPositionalArg: NoPositionalArg,
                            KwOnlyNotOk: KwOnlyNotOk,
                            'Bad': int}


def only_var_arg(argument: OnlyVarArg, expected):
    assert isinstance(argument, OnlyVarArg)
    assert argument.value == expected


def number(argument: Number, expected: int = 0):
    if argument != expected:
        raise AssertionError(f'Expected value to be {expected!r}, got {argument!r}.')


def true(argument: bool):
    assert argument is True


def false(argument: bool):
    assert argument is False


def string(argument: String, expected: str = '123'):
    if argument != expected:
        raise AssertionError


def us_date(argument: UsDate, expected: date = None):
    assert argument == expected


def fi_date(argument: FiDate, expected: date = None):
    assert argument == expected


def dates(us: 'UsDate', fi: 'FiDate'):
    assert us == fi


def class_as_converter(argument: ClassAsConverter, expected):
    assert argument.greeting == expected


def class_with_hints_as_converter(argument: ClassWithHintsAsConverter, expected=None):
    assert argument.value == expected


def accept_subscripted_generics(argument: AcceptSubscriptedGenerics, expected):
    assert argument.sum == expected


def with_generics(a: List[Number], b: Tuple[FiDate, UsDate], c: Dict[Number, FiDate], d: Set[Number]):
    expected_date = date(2022, 9, 28)
    assert a == [1, 2, 3], a
    assert b == (expected_date, expected_date), b
    assert c == {1: expected_date}, c
    assert d == {1, 2, 3}, d


def typeddict(dates: TypedDict('Dates', {'fi': FiDate, 'us': UsDate})):
    fi, us = dates['fi'], dates['us']
    exp = date(2022, 9, 29)
    assert isinstance(fi, FiDate) and isinstance(us, UsDate) and fi == us == exp


def number_or_int(number: Union[Number, int]):
    assert number == 1


def int_or_number(number: Union[int, Number]):
    assert number == 1


def strict(argument: Strict):
    assert isinstance(argument, Strict)


def invalid(a: Invalid, b: TooFewArgs, c: TooManyArgs, d: KwOnlyNotOk):
    assert (a, b, c, d) == ('a', 'b', 'c', 'd')


def non_type_annotation(arg1: 'Hello world!', arg2: 2 = 2):
    assert arg1 == arg2


def multiplying_converter(value: str, library) -> int:
    return library.counter * int(value)


class StatefulLibrary:
    ROBOT_LIBRARY_CONVERTERS = {Number: multiplying_converter}

    def __init__(self):
        self.counter = 1

    def multiply(self, num: Number, expected: int):
        self.counter += 1
        assert num == int(expected)


class StatefulGlobalLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_CONVERTERS = {Number: multiplying_converter}

    def __init__(self):
        self.counter = 1

    def global_multiply(self, num: Number, expected: int):
        self.counter += 1
        assert num == int(expected)
