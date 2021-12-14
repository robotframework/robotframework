from datetime import date, datetime
from typing import List, Union


class Number:
    pass


def string_to_int(value: str) -> int:
    try:
        return ['zero', 'one', 'two', 'three', 'four'].index(value.lower())
    except ValueError:
        raise ValueError(f"Don't know number {value!r}.")


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
            raise RuntimeError("Value does not match '%m/%d/%Y'.")


class FiDate(date):
    @classmethod
    def from_string(cls, value: str):
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


class Invalid:
    pass


class TooFewArgs:
    pass


class TooManyArgs:
    def __init__(self, one, two):
        pass


class KwOnlyNotOk:
    def __init__(self, arg, *, kwo):
        pass


ROBOT_LIBRARY_CONVERTERS = {Number: string_to_int,
                            bool: parse_bool,
                            UsDate: UsDate.from_string,
                            FiDate: FiDate.from_string,
                            ClassAsConverter: ClassAsConverter,
                            ClassWithHintsAsConverter: ClassWithHintsAsConverter,
                            AcceptSubscriptedGenerics: AcceptSubscriptedGenerics,
                            Invalid: 666,
                            TooFewArgs: TooFewArgs,
                            TooManyArgs: TooManyArgs,
                            KwOnlyNotOk: KwOnlyNotOk,
                            'Bad': int}


def number(argument: Number, expected: int = 0):
    if argument != expected:
        raise AssertionError(f'Expected value to be {expected!r}, got {argument!r}.')


def true(argument: bool):
    assert argument is True


def false(argument: bool):
    assert argument is False


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


def number_or_int(number: Union[Number, int]):
    assert number == 1


def int_or_number(number: Union[int, Number]):
    assert number == 1


def invalid(a: Invalid, b: TooFewArgs, c: TooManyArgs, d: KwOnlyNotOk):
    assert (a, b, c, d) == ('a', 'b', 'c', 'd')


def non_type_annotation(arg1: 'Hello, world!', arg2: 2 = 2):
    assert arg1 == arg2
