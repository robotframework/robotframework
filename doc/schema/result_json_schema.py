#!/usr/bin/env python3

"""JSON schemas for the full JSON result and for `robot.result.TestSuite`.

The schema is modeled using Pydantic in this file. After updating the model,
execute this file to regenerate the actual JSON schemas. Separate schema files
are generated for the full JSON result (`result.json`) and for the
`robot.result.TestSuite` structure (`result_suite.json`).

Requires Pydantic 1.10. https://docs.pydantic.dev/1.10/
"""

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel as PydanticBaseModel, Extra, Field


class BaseModel(PydanticBaseModel):

    class Config:
        # Do not allow extra attributes.
        extra = Extra.forbid


class WithStatus(BaseModel):
    elapsed_time: float
    status: str
    start_time: datetime | None
    message: str | None


class Var(WithStatus):
    type = Field('VAR', const=True)
    name: str
    value: Sequence[str]
    scope: str | None
    separator: str | None
    body: list['Keyword | Message'] | None


class Return(WithStatus):
    type = Field('RETURN', const=True)
    values: Sequence[str] | None
    body: list['Keyword | Message'] | None


class Continue(WithStatus):
    type = Field('CONTINUE', const=True)
    body: list['Keyword | Message'] | None


class Break(WithStatus):
    type = Field('BREAK', const=True)
    body: list['Keyword | Message'] | None


class Error(WithStatus):
    type = Field('ERROR', const=True)
    values: Sequence[str]
    body: list['Keyword | Message'] | None


class Message(BaseModel):
    type = Field('MESSAGE', const=True)
    message: str
    level: Literal['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FAIL', 'SKIP']
    html: bool | None
    timestamp: datetime | None


class ErrorMessage(BaseModel):
    message: str
    level: Literal['ERROR', 'WARN']
    html: bool | None
    timestamp: datetime | None


class Keyword(WithStatus):
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
    body: list['Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error | Message'] | None


class For(WithStatus):
    type = Field('FOR', const=True)
    assign: Sequence[str]
    flavor: str
    values: Sequence[str]
    start: str | None
    mode: str | None
    fill: str | None
    body: list['Keyword | For | ForIteration | While | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class ForIteration(WithStatus):
    type = Field('ITERATION', const=True)
    assign: dict[str, str]
    body: list['Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error| Message']


class While(WithStatus):
    type = Field('WHILE', const=True)
    condition: str | None
    limit: str | None
    on_limit: str | None
    on_limit_message: str | None
    body: list['Keyword | For | While | WhileIteration | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class WhileIteration(WithStatus):
    type = Field('ITERATION', const=True)
    body: list['Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class Group(WithStatus):
    type = Field('GROUP', const=True)
    name: str
    body: list['Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class IfBranch(WithStatus):
    type: Literal['IF', 'ELSE IF', 'ELSE']
    condition: str | None
    body: list['Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class If(WithStatus):
    type = Field('IF/ELSE ROOT', const=True)
    body: list['IfBranch | Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class TryBranch(WithStatus):
    type: Literal['TRY', 'EXCEPT', 'ELSE', 'FINALLY']
    patterns: Sequence[str] | None
    pattern_type: str | None
    assign: str | None
    body: list['Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class Try(WithStatus):
    type = Field('TRY/EXCEPT ROOT', const=True)
    body: list['TryBranch | Keyword | For | While | Group | If | Try | Var | Break | Continue | Return | Error | Message']


class TestCase(WithStatus):
    name: str
    id: str | None
    doc: str | None
    tags: Sequence[str] | None
    template: str | None
    timeout: str | None
    lineno: int | None
    error: str | None
    setup: Keyword | None
    teardown: Keyword | None
    body: list[Keyword | For | While | Group | If | Try | Var | Error | Message ]


class TestSuite(WithStatus):
    name: str
    id: str | None
    doc: str | None
    metadata: dict[str, str] | None
    source: Path | None
    rpa: bool | None
    setup: Keyword | None
    teardown: Keyword | None
    tests: list[TestCase] | None
    suites: list['TestSuite'] | None


class RootSuite(TestSuite):
    """JSON schema for `robot.result.TestSuite`.

    The whole result model with, for example, errors and statistics has its
    own schema.

    Compatible with JSON Schema Draft 2020-12.
    """

    class Config:
        title = 'robot.result.TestSuite'
        # pydantic doesn't add schema version automatically.
        # https://github.com/samuelcolvin/pydantic/issues/1478
        schema_extra = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema'
        }


class Stat(BaseModel):
    label: str
    pass_: int = Field(alias='pass')
    fail: int
    skip: int


class SuiteStat(Stat):
    name: str
    id: str


class TagStat(Stat):
    doc: str | None
    combined: str | None
    info: str | None
    links: str | None


class Statistics(BaseModel):
    total: Stat
    suites: list[SuiteStat]
    tags: list[TagStat]


class Result(BaseModel):
    """Schema for JSON output files.

    `robot.result.TestSuite` has a separate schema that can be used when not
    working with the full result model.

    Compatible with JSON Schema Draft 2020-12.
    """
    generated: datetime
    generator: str
    rpa: bool
    suite: TestSuite
    statistics: Statistics
    errors: list[ErrorMessage]

    class Config:
        # pydantic doesn't add schema version automatically.
        # https://github.com/samuelcolvin/pydantic/issues/1478
        schema_extra = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema'
        }


for cls in [Keyword, For, ForIteration, While, WhileIteration, Group, If, IfBranch,
            Try, TryBranch, TestSuite, Error, Break, Continue, Return, Var]:
    cls.update_forward_refs()


def generate(model, file_name):
    path = Path(__file__).parent / file_name
    with open(path, 'w') as f:
        f.write(model.schema_json(indent=2))
    print(path.absolute())


if __name__ == '__main__':
    generate(Result, 'result.json')
    generate(RootSuite, 'result_suite.json')
