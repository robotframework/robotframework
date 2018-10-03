try:
    unicode
except NameError:
    unicode = str


messages = [u'Circle is 360\u00B0',
            u'Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4',
            u'\u0989\u09C4 \u09F0 \u09FA \u099F \u09EB \u09EA \u09B9']


class NonAsciiLibrary:

    def print_non_ascii_strings(self):
        """Prints message containing non-ASCII characters"""
        for msg in messages:
            print('*INFO*' + msg)

    def print_and_return_non_ascii_object(self):
        """Prints object with non-ASCII `str()` and returns it."""
        obj = NonAsciiObject()
        print(unicode(obj))
        return obj

    def raise_non_ascii_error(self):
        raise AssertionError(', '.join(messages))


class NonAsciiObject:

    def __init__(self):
        self.message = u', '.join(messages)

    def __str__(self):
        return self.message

    def __repr__(self):
        return repr(self.message)
