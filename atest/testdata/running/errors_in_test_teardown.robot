*** Settings ***
Library            Exceptions
Suite Setup        Set Suite Teardown Failed Variable
Suite Teardown     Suite Teardown With Errors

*** Test Cases ***
One Error In Teardown
    [documentation]  FAIL Teardown failed:\n
    ...  Message\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  One Error

Many Errors In Teardown
    [documentation]  FAIL Teardown failed:\n
    ...  Several failures occurred:\n\n
    ...  1) Message 1\n\n
    ...  2) Message 2\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  Many Errors

Errors In Teardown When Setting Variables
    [documentation]  FAIL  Teardown failed:\n
    ...  no return value is set\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  Errors when setting variables

Errors In For Loop In Teardown
    [documentation]  FAIL Teardown failed:\n
    ...  Several failures occurred:\n\n
    ...  1) cat\n\n
    ...  2) again\n\n
    ...  3) dog\n\n
    ...  4) again\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  Errors In For Loop

Keyword Timeout In Teardown
    [documentation]  FAIL Teardown failed:\n
    ...  Keyword timeout 42 milliseconds exceeded.\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  Timeout

Syntax Error in Teardown
    [documentation]  FAIL Teardown failed:\nSeveral failures occurred:\n\n
    ...  1) Variable '${non existing variable}' not found.\n\n
    ...  2) No keyword with name 'Keyword Missing' found.\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  Syntax Error

Syntax Error in For Loop in Teardown
    [documentation]  FAIL Teardown failed:\nSeveral failures occurred:\n\n
    ...  1) Variable '${non existing variable}' not found.\n\n
    ...  2) This should be executed\n\n
    ...  3) Variable '${non existing variable}' not found.\n\n
    ...  4) This should be executed\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  Syntax Errors In For Loop

Fatal Error In Teardown
    [documentation]  FAIL Teardown failed:\n
    ...  FatalCatastrophyException\n\n
    ...  ${SUITE TEARDOWN FAILED}
    No Operation
    [teardown]  Fatal Error


*** Keywords ***
Set Suite Teardown Failed Variable
    ${SUITE TEARDOWN FAILED} =    Catenate    SEPARATOR=\n
    ...    Also parent suite teardown failed:
    ...    Several failures occurred:
    ...    ${EMPTY}
    ...    1) Suite Message 1
    ...    ${EMPTY}
    ...    2) Suite Message 2 (with ∏ön ÄßÇïï €§)
    ...    ${EMPTY}
    ...    3) No keyword with name 'Missing Keyword' found.
    Set Suite Variable    ${SUITE TEARDOWN FAILED}

Suite Teardown With Errors
    Fail  Suite Message 1
    Fail  Suite Message 2 (with ∏ön ÄßÇïï €§)
    Missing Keyword
    Log  This As Well Should Be Executed

One Error
    Fail  Message
    Log  This Should Be executed

Many Errors
    Fail  Message 1
    Fail  Message 2
    Log  This Should Also Be Executed

Errors when setting variables
    ${ret} =  Fail  no return value is set
    Should Be Equal  ${ret}  ${None}

Errors In For Loop
    :FOR  ${animal}  in  cat  dog
    \    Fail  ${animal}
    \    Fail  again

Timeout
    [timeout]  42 ms
    Sleep  1 s
    Fail  This Should Not Be Executed

Syntax Error
    Log  ${non existing variable}
    Keyword Missing
    Log  This Should Be Executed

Syntax Errors In For Loop
    :FOR  ${i}  IN RANGE  2
    \  Log  ${non existing variable}
    \  Fail  This should be executed
    Log  This should be executed

Fatal Error
    Exit On Failure
    Fail  This Should Not Be Executed
