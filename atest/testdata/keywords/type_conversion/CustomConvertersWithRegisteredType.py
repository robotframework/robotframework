from CustomConverters import AutoConvertedNumber, AutoConvertedSpecialNumber


class CustomConvertersWithRegisteredType:
    """
    Library does not state any converters explicitly.
    Conversion is done from registered type.
    """

    def from_registered_type(self, value: AutoConvertedNumber, expected: int):
        assert value == expected, f"value [{value}] == expected [{expected}]"

    def from_registered_type_special(self, value: AutoConvertedSpecialNumber, expected: int):
        assert value == expected, f"value [{value}] == expected [{expected}]"
