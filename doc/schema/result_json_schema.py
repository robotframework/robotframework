#!/usr/bin/env python3

"""JSON schema for ``robot.running.TestSuite`` model structure.

The schema is modeled using Pydantic in this file. After updating the model,
execute this file to regenerate the actual schema file in ``running.json``.

Requires Pydantic 1.10. https://docs.pydantic.dev/1.10/
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel as PydanticBaseModel, Extra, Field


class BaseModel(PydanticBaseModel):
    elapsed_time: float
    status: str
    start_time: str | None
    message: str | None

    class Config:
        # Do not allow extra attributes.
        extra = Extra.forbid


class Var(BaseModel):
    type = Field('VAR', const=True)
    name: str
    value: Sequence[str]
    scope: str | None
    separator: str | None


class Return(BaseModel):
    type = Field('RETURN', const=True)
    values: Sequence[str] | None


class Continue(BaseModel):
    type = Field('CONTINUE', const=True)


class Break(BaseModel):
    type = Field('BREAK', const=True)


class Error(BaseModel):
    type = Field('ERROR', const=True)
    values: Sequence[str]


class Keyword(BaseModel):
    name: str
    args: Sequence[str] | None
    assign: Sequence[str] | None
    owner: str | None
    source_name: str | None
    doc: str | None
    tags: Sequence[str] | None
    timeout: str | None
    setup: 'Keyword | None'
    teardown: 'Keyword | None'
    body: list['Keyword | For | While | If | Try | Var | Break | Continue | Return | Error']


class For(BaseModel):
    type = Field('FOR', const=True)
    assign: Sequence[str]
    flavor: str
    values: Sequence[str]
    start: str | None
    mode: str | None
    fill: str | None
    body: list['Keyword | For | While | If | Try | Var | Break | Continue | Return | Error']


class While(BaseModel):
    type = Field('WHILE', const=True)
    condition: str | None
    limit: str | None
    on_limit: str | None
    on_limit_message: str | None
    body: list['Keyword | For | While | If | Try | Var | Break | Continue | Return | Error']


class IfBranch(BaseModel):
    type: Literal['IF', 'ELSE IF', 'ELSE']
    condition: str | None
    body: list['Keyword | For | While | If | Try | Var | Break | Continue | Return | Error']


class If(BaseModel):
    type = Field('IF/ELSE ROOT', const=True)
    body: list[IfBranch]


class TryBranch(BaseModel):
    type: Literal['TRY', 'EXCEPT', 'ELSE', 'FINALLY']
    patterns: Sequence[str] | None
    pattern_type: str | None
    assign: str | None
    body: list['Keyword | For | While | If | Try | Var | Break | Continue | Return | Error']


class Try(BaseModel):
    type = Field('TRY/EXCEPT ROOT', const=True)
    body: list[TryBranch]


class TestCase(BaseModel):
    name: str
    doc: str | None
    tags: Sequence[str] | None
    template: str | None
    timeout: str | None
    lineno: int | None
    error: str | None
    setup: Keyword | None
    teardown: Keyword | None
    body: list[Keyword | For | While | If | Try | Var | Error]


class TestSuite(BaseModel):
    """JSON schema for `robot.running.TestSuite`.

    Compatible with JSON Schema Draft 2020-12.
    """
    name: str
    doc: str | None
    metadata: dict[str, str] | None
    source: Path | None
    rpa: bool | None
    setup: Keyword | None
    teardown: Keyword | None
    tests: list[TestCase] | None
    suites: list['TestSuite'] | None

    class Config:
        # pydantic doesn't add schema version automatically.
        # https://github.com/samuelcolvin/pydantic/issues/1478
        schema_extra = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema'
        }


for cls in [For, While, IfBranch, TryBranch, TestSuite]:
    cls.update_forward_refs()


if __name__ == '__main__':
    path = Path(__file__).parent / 'result.json'
    with open(path, 'w') as f:
        f.write(TestSuite.schema_json(indent=2))
    print(path.absolute())
