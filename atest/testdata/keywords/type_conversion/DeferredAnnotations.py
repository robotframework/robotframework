from typing import TYPE_CHECKING

from robot.api.deco import library

if TYPE_CHECKING:
    from collections.abc import Sequence


class Library:
    def deferred_evaluation_of_annotations(self, arg: Argument) -> str:  # noqa: F821
        return arg.value

    def type_checking_annotation(self, seq: Sequence[int]) -> int:  # noqa: F821
        return sum(seq)

    def nonexisting_annotation(self, arg: NonExisting):  # noqa: F821
        return arg


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
