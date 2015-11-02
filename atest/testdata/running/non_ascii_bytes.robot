*** Settings ***
Library           NonAsciiByteLibrary.py
Variables         expbytevalues.py

*** Test Cases ***
In Message
    In Message

In Multiline Message
    In Multiline Message

In Return Value
    [Documentation]    Return value is not altered by the framework and thus it
    ...    contains the exact same bytes that the keyword returned.
    ${retval} =    In Return Value
    Should Be Equal    ${retval}    ${exp_return_value}

In Exception
    [Documentation]    FAIL ${exp_error_msg}
    In Exception

In Exception In Setup
    [Documentation]    FAIL Setup failed:\n${exp_error_msg}
    [Setup]    In Exception
    No Operation

In Exception In Teardown
    [Documentation]    FAIL Teardown failed:\n${exp_error_msg}
    No Operation
    [Teardown]    In Exception
