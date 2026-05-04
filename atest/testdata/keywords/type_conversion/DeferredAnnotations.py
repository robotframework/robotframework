from typing import TYPE_CHECKING

from robot.api.deco import library

if TYPE_CHECKING:
    from typing import Sequence
    class TypeCheckingOnly: ...


class Library:

    def deferred_evaluation_of_annotations(self, arg: Argument) -> str:  # noqa: F821
        return arg.value

    def type_checking_annotation(self, arg: TypeCheckingOnly) -> TypeCheckingOnly:  # noqa: F821
        return arg

    def nonexisting_annotation(self, arg: NonExisting):  # noqa: F821
        return arg

    def my_sum(self, seq: Sequence[int]) -> int:  # noqa: F821
        return sum(seq)

class Argument:

    def __init__(self, value: str):
        self.value = value

    @classmethod
    def from_string(cls, value: str) -> Argument:  # noqa: F821
        return cls(value)


Library = library(
    converters={Argument: Argument.from_string},
    auto_keywords=True,
)(Library)
