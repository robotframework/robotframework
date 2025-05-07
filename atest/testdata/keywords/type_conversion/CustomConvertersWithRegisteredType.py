from CustomConverters import AutoConvertedNumber


class CustomConvertersWithRegisteredType:
    """
    Library does not state any converters explicitly.
    Conversion is done from registered type.
    """

    def from_registered_type(self, value: AutoConvertedNumber, expected: int):
        assert value == expected
