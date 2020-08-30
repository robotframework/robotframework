*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/Annotations.py
Force Tags        require-py3
Resource          libdoc_resource.robot

*** Test Cases ***
Basics
    Keyword Arguments Should Be     0    integer: int    boolean: bool    string: str

Enums
    Keyword Arguments Should Be     1    small: Small { one | two | three | four }
    ...                                  many_small: ManySmall { A | B | C | D | E | F | G | H | I | J | K }
    ...                                  big: Big { FIRST_MEMBER_IS_LONG | SECOND_MEMBER_IS_LONGER | ... }

With defaults
    Keyword Arguments Should Be     2    integer: int = 42    list_: list = None
    ...                                  enum: Small { one | two | three | four } = None

Keyword-only arguments
    Keyword Arguments Should Be     3    *    kwo: int    with_default: str = value

Varargs and kwargs
    Keyword Arguments Should Be     4    *varargs: int    **kwargs: bool

Unknown types
    Keyword Arguments Should Be     5    unknown: UnknownType    unrecognized: Ellipsis

Non-type annotations
    Keyword Arguments Should Be     6    arg: One of the usages in PEP-3107
    ...                                  *varargs: But surely feels odd...
