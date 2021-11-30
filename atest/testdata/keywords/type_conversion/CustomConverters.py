from datetime import date, datetime


class Number:
    pass


def string_to_int(value):
    try:
        return ['zero', 'one', 'two', 'three', 'four'].index(value.lower())
    except ValueError:
        raise ValueError(f"Don't know number {value!r}.")


def parse_bool(value):
    if isinstance(value, str):
        value = value.lower()
    return value not in ['false', '', 'epätosi', '\u2639', False, 0]


class UsDate(date):
    @classmethod
    def from_string(cls, value):
        if not isinstance(value, str):
            raise TypeError("Only strings accepted!")
        try:
            return cls.fromordinal(datetime.strptime(value, '%m/%d/%Y').toordinal())
        except ValueError:
            raise RuntimeError("Value does not match '%m/%d/%Y'.")


class FiDate(date):
    @classmethod
    def from_string(cls, value):
        if not isinstance(value, str):
            raise TypeError("Only strings accepted!")
        try:
            return cls.fromordinal(datetime.strptime(value, '%d.%m.%Y').toordinal())
        except ValueError:
            raise RuntimeError("Value does not match '%d.%m.%Y'.")


class Invalid:
    pass


ROBOT_LIBRARY_CONVERTERS = {Number: string_to_int, bool: parse_bool,
                            UsDate: UsDate.from_string, FiDate: FiDate.from_string,
                            Invalid: 666}


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


def dates(us: UsDate, fi: FiDate):
    assert us == fi


def invalid(argument: Invalid):
    assert False


def non_type_annotation(arg1: 'Hello, world!', arg2: 2 = 2):
    assert arg1 == arg2
