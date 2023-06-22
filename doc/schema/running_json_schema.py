#!/usr/bin/env python3

"""JSON schema for ``robot.running.TestSuite`` model structure.

The schema is modeled using pydantic in this file. After updating the model,
execute this file to regenerate the actual schema file in ``running.json``.

https://pydantic-docs.helpmanual.io/usage/schema/
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Extra, Field


class BodyItem(BaseModel):
    lineno: int | None
    error: str | None


class Return(BodyItem):
    type = Field('RETURN', const=True)
    values: Sequence[str]


class Continue(BodyItem):
    type = Field('CONTINUE', const=True)


class Break(BodyItem):
    type = Field('BREAK', const=True)


class Error(BodyItem):
    type = Field('ERROR', const=True)
    values: Sequence[str]
    error: str


class Keyword(BodyItem):
    name: str
    args: Sequence[str] | None
    assign: Sequence[str] | None


class For(BodyItem):
    type = Field('FOR', const=True)
    variables: Sequence[str]
    flavor: str
    values: Sequence[str]
    start: str | None
    mode: str | None
    fill: str | None
    body: list['Keyword | For | While | If | Try | Error | Break | Continue | Return']


class While(BodyItem):
    type = Field('WHILE', const=True)
    condition: str | None
    limit: str | None
    on_limit: str | None
    on_limit_message: str | None
    body: list['Keyword | For | While | If | Try | Error | Break | Continue | Return']


class IfBranch(BodyItem):
    type: Literal['IF', 'ELSE IF', 'ELSE']
    condition: str | None
    body: list['Keyword | For | While | If | Try | Error | Break | Continue | Return']


class If(BodyItem):
    type = Field('IF/ELSE ROOT', const=True)
    body: list[IfBranch]


class TryBranch(BodyItem):
    type: Literal['TRY', 'EXCEPT', 'ELSE', 'FINALLY']
    patterns: Sequence[str] | None
    pattern_type: str | None
    variable: str | None
    body: list['Keyword | For | While | If | Try | Error | Break | Continue | Return']


class Try(BodyItem):
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
    body: list[Keyword | For | While | If | Try | Error]


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
    resource: 'Resource | None'

    class Config:
        # Do not allow extra attributes.
        extra = Extra.forbid
        # pydantic doesn't add schema version automatically.
        # https://github.com/samuelcolvin/pydantic/issues/1478
        schema_extra = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema'
        }


class Import(BaseModel):
    type: Literal['LIBRARY', 'RESOURCE', 'VARIABLES']
    name: str
    args: Sequence[str] | None
    alias: str | None
    lineno: int | None


class Variable(BaseModel):
    name: str
    value: Sequence[str]
    lineno: int | None
    error: str | None


class UserKeyword(BaseModel):
    name: str
    args: Sequence[str] | None
    doc: str | None
    tags: Sequence[str] | None
    return_: Sequence[str] | None
    timeout: str | None
    lineno: int | None
    error: str | None
    body: list[Keyword | For | While | If | Try | Error | Return]


class Resource(BaseModel):
    source: Path | None
    doc: str | None
    imports: list[Import] | None
    variables: list[Variable] | None
    keywords: list[UserKeyword] | None


for cls in [For, While, IfBranch, TryBranch, TestSuite]:
    cls.update_forward_refs()


if __name__ == '__main__':
    path = Path(__file__).parent / 'running.json'
    with open(path, 'w') as f:
        f.write(TestSuite.schema_json(indent=2))
    print(path.absolute())
