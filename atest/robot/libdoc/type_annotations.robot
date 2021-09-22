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
    Keyword Arguments Should Be     5    unknown: UnknownType    unrecognized: Ellipsis

Non-type annotations
    Keyword Arguments Should Be     6    arg: One of the usages in PEP-3107
    ...                                  *varargs: But surely feels odd...

Drop `typing.` prefix
    Keyword Arguments Should Be     7    a: Any    b: List    c: Any | List
