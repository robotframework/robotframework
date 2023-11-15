*** Settings ***
Suite Setup        Run Libdoc And Parse Output    ${TESTDATADIR}/ReturnType.py
Test Template      Return Type Should Be
Resource           libdoc_resource.robot

*** Test Cases ***
No return
    0    None

None return
    1    None

Simple return
    2    int

Parameterized return
    3    List    int

Union return
    4    Union    int    float

Stringified return
    5    Union    int    float

Unknown return
    6    Unknown

Invalid return
    [Template]    NONE
    VAR    ${error}
    ...    [ ERROR ] Error in library 'ReturnType':
    ...    Adding keyword 'H_invalid_return' failed:
    ...    Parsing type 'list[int' failed:
    ...    Error at end:
    ...    Closing ']' missing.
    Should Start With    ${OUTPUT}    ${error}

Return types are in typedocs
    [Template]    Usages Should Be
    0    Standard    float
    ...    E Union Return
    ...    F Stringified Return
    1    Standard    integer
    ...    C Simple Return
    ...    D Parameterized Return
    ...    E Union Return
    ...    F Stringified Return
    2    Standard    list
    ...    D Parameterized Return
