class StaticAndClassMethod:

    @staticmethod
    def static_method(arg: int):
        assert arg == 42

    @classmethod
    def class_method(cls, arg: int):
        assert arg == 42
