from typing import TYPE_CHECKING

from robot.api.deco import library

if TYPE_CHECKING:
    from typing import Sequence

    class TypeCheckingOnly:
        pass


class Library:

    def created_later(self, arg: Argument) -> str:  # noqa: F821
        return arg.value

    def type_checking_only(self, arg: TypeCheckingOnly) -> TypeCheckingOnly:
        return arg

    def type_checking_only_but_known(self, seq: Sequence[int]) -> int:  # noqa: F821
        return sum(seq)

    def non_existing(self, arg: NonExisting):  # noqa: F821
        return arg

    def invalid(self, arg: 1 / 0):
        pass


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
