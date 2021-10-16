class CustomLen:

    def __init__(self, length):
        self._length=length

    def __len__(self):
        return self._length


class LengthMethod:

    def length(self):
        return 40

    def __str__(self):
        return 'length()'


class SizeMethod:

    def size(self):
        return 41

    def __str__(self):
        return 'size()'


class LengthAttribute:
    length=42

    def __str__(self):
        return 'length'


def get_variables():
    return dict(
        CUSTOM_LEN_0=CustomLen(0),
        CUSTOM_LEN_1=CustomLen(1),
        CUSTOM_LEN_2=CustomLen(2),
        CUSTOM_LEN_3=CustomLen(3),
        LENGTH_METHOD=LengthMethod(),
        SIZE_METHOD=SizeMethod(),
        LENGTH_ATTRIBUTE=LengthAttribute()
    )
