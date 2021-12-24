from robot.api.deco import library

from CustomConverters import Number, string_to_int


@library(converters={Number: string_to_int}, auto_keywords=True)
class CustomConvertersWithLibraryDecorator:

    def using_library_decorator(self, value: Number, expected: int):
        assert value == expected
