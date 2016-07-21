try:
    unicode
except NameError:
    unicode = str


messages = [ u'Circle is 360\u00B0',
             u'Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4',
             u'\u0989\u09C4 \u09F0 \u09FA \u099F \u09EB \u09EA \u09B9' ]


class UnicodeLibrary:

    def print_unicode_strings(self):
        """Prints message containing unicode characters"""
        for msg in messages:
            print('*INFO*' + msg)

    def print_and_return_unicode_object(self):
        """Prints unicode object and returns it."""
        object = UnicodeObject()
        print(unicode(object))
        return object

    def raise_unicode_error(self):
        raise AssertionError(', '.join(messages))


class UnicodeObject:

    def __init__(self):
        self.message = u', '.join(messages)

    def __str__(self):
        return self.message

    def __repr__(self):
        return repr(self.message)
