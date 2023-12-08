*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/Annotations.py
Resource          libdoc_resource.robot

*** Test Cases ***
Basics
    Keyword Arguments Should Be     0    integer: int    boolean: bool    string: str

Enums
    Keyword Arguments Should Be     1    small: Small
    ...                                  many_small: ManySmall
    ...                                  big: Big

With defaults
    Keyword Arguments Should Be     2    integer: int = 42    list_: list | None = None
    ...                                  enum: Small | None = None

Keyword-only arguments
    Keyword Arguments Should Be     3    *    kwo: int    with_default: str = value

Varargs and kwargs
    Keyword Arguments Should Be     4    *varargs: int    **kwargs: bool

Unknown types
    Keyword Arguments Should Be     5    unknown: UnknownType    unrecognized: ...

Non-type annotations
    Keyword Arguments Should Be     6    arg: One of the usages in PEP-3107
    ...                                  *varargs: But surely feels odd...

Drop `typing.` prefix
    Keyword Arguments Should Be     7    a: Any    b: List    c: Any | List

Union from typing
    Keyword Arguments Should Be     8    a: int | str | list | tuple
    Keyword Arguments Should Be     9    a: int | str | list | tuple | None = None

Nested
    Keyword Arguments Should Be    10    a: List[int]    b: List[int | float]    c: Tuple[Tuple[UnknownType], Dict[str, Tuple[float]]]


Literal
    Keyword Arguments Should Be    11    a: Literal['on', 'off', 'int']    b: Literal[1, 2, 3]   c: Literal[one, True, None]

Union syntax
    [Tags]    require-py3.10
    Keyword Arguments Should Be    12    a: int | str | list | tuple
    Keyword Arguments Should Be    13    a: int | str | list | tuple | None = None
