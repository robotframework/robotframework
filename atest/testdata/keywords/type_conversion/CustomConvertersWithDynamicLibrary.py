from CustomConverters import Number, string_to_int


class CustomConvertersWithDynamicLibrary:
    ROBOT_LIBRARY_CONVERTERS = {Number: string_to_int}

    def get_keyword_names(self):
        return ['dynamic keyword']

    def run_keyword(self, name, args, named):
        self._validate(*args, **named)

    def _validate(self, argument, expected):
        assert argument == expected

    def get_keyword_arguments(self, name):
        return ['argument', 'expected']

    def get_keyword_types(self, name):
        return [Number, int]
