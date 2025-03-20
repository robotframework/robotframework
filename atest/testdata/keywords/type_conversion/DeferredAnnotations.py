from robot.api.deco import library


class Library:

    def deferred_evaluation_of_annotations(self, arg: Argument) -> str:
        return arg.value


class Argument:

    def __init__(self, value: str):
        self.value = value

    @classmethod
    def from_string(cls, value: str) -> Argument:
        return cls(value)


Library = library(converters={Argument: Argument.from_string},
                  auto_keywords=True)(Library)
