MESSAGES = [
    "Circle is 360°",
    "Hyvää üötä",
    "\u0989\u09c4 \u09f0 \u09fa \u099f \u09eb \u09ea \u09b9",
]


class NonAsciiLibrary:

    def print_non_ascii_strings(self):
        """Prints message containing non-ASCII characters"""
        for msg in MESSAGES:
            print("*INFO*" + msg)

    def print_and_return_non_ascii_object(self):
        """Prints object with non-ASCII `str()` and returns it."""
        obj = NonAsciiObject()
        print(obj)
        return obj

    def raise_non_ascii_error(self):
        raise AssertionError(", ".join(MESSAGES))


class NonAsciiObject:

    def __init__(self):
        self.message = ", ".join(MESSAGES)

    def __str__(self):
        return self.message

    def __repr__(self):
        return repr(self.message)
