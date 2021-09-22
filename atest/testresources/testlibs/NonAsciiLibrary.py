MESSAGES = ['Circle is 360°',
            'Hyvää üötä',
            '\u0989\u09C4 \u09F0 \u09FA \u099F \u09EB \u09EA \u09B9']


class NonAsciiLibrary:

    def print_non_ascii_strings(self):
        """Prints message containing non-ASCII characters"""
        for msg in MESSAGES:
            print('*INFO*' + msg)

    def print_and_return_non_ascii_object(self):
        """Prints object with non-ASCII `str()` and returns it."""
        obj = NonAsciiObject()
        print(obj)
        return obj

    def raise_non_ascii_error(self):
        raise AssertionError(', '.join(MESSAGES))


class NonAsciiObject:

    def __init__(self):
        self.message = ', '.join(MESSAGES)

    def __str__(self):
        return self.message

    def __repr__(self):
        return repr(self.message)
