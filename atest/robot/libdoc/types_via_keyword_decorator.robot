*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/TypesViaKeywordDeco.py
Resource          libdoc_resource.robot

*** Test Cases ***
Basics
    Keyword Arguments Should Be     0    integer: int    boolean: bool    string: str

With defaults
    Keyword Arguments Should Be     1    integer: int = 42    list_: list = None

Varargs and kwargs
    Keyword Arguments Should Be     2    *varargs: int    **kwargs: bool

Unknown types
    Keyword Arguments Should Be     3    unknown: UnknownType    unrecognized: Ellipsis

Non-type annotations
    Keyword Arguments Should Be     4    arg: One of the usages in PEP-3107
    ...                                  *varargs: But surely feels odd...

Keyword-only arguments
    Keyword Arguments Should Be     5    *    kwo: int    with_default: str = value
