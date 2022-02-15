from robot.api.deco import keyword, library

from CustomConverters import Number, string_to_int


@library(converters={Number: string_to_int})
class CustomConvertersWithLibraryDecorator:

    @keyword
    def using_library_decorator(self, value: Number, expected: int):
        assert value == expected

    @keyword(name='Embedded "${arg1}" should be equal to "${arg2}"')
    def embedded(self, value: Number, expected: int):
        assert value == expected
