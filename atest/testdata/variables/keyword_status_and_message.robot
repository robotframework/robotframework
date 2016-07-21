*** Test Cases ***

Pass status directly in teardown
    Passing keyword status

Pass message directly in teardown
    Passing keyword message

Fail status directly in teardown
    [Documentation]    FAIL    AssertionError
    Failing keyword status

Fail message directly in teardown
    [Documentation]    FAIL    Expected failure
    Failing keyword message

Pass status and message in keyword used in teardown
    Pass status and message in keyword used in teardown

Fail status and message in keyword used in teardown
    [Documentation]    FAIL    Another expected fail
    Fail status and message in keyword used in teardown

Status and message when keyword fails multiple times
    [Documentation]    FAIL    Several failures occurred:\n\n1) 1st\n\n2) 2nd
    Multiple failures

Status and message when there are only continuable failures
    [Documentation]    FAIL    Several failures occurred:\n\n1) one\n\n2) two
    Only continuable failures

Status and message are not available if not in teardown
    Variable should not exist    ${KEYWORD STATUS}
    Variable should not exist    ${KEYWORD MESSAGE}
    Status and message are not available if not in teardown

Status and message are not available after teardown
    Passing keyword message
    Variable should not exist    ${KEYWORD STATUS}
    Variable should not exist    ${KEYWORD MESSAGE}
    Status and message are not available if not in teardown

Previous status and message are not overwritten
    [Documentation]    FAIL    My message
    ${KEYWORD STATUS}=    Set variable    1
    ${KEYWORD MESSAGE}=    Set variable    2
    Keyword teardown with keyword teardown
    [Teardown]    Should be equal    ${KEYWORD STATUS}-${KEYWORD MESSAGE}    1-2

Status and message always contain latest values
    [Documentation]    FAIL
    ...    1
    ...
    ...    Also keyword teardown failed:
    ...    2
    ...
    ...    Also keyword teardown failed:
    ...    3
    Status and message always contain latest values

*** Keywords ***
Passing keyword status
    No operation
    [Teardown]    Should be equal    ${KEYWORD STATUS}    PASS

Passing keyword message
    No operation
    [Teardown]    Should be equal    ${KEYWORD MESSAGE}    ${EMPTY}

Failing keyword status
    Fail
    [Teardown]    Should be equal    ${KEYWORD STATUS}    FAIL

Failing keyword message
    Fail    Expected failure
    [Teardown]    Should be equal    ${KEYWORD MESSAGE}    Expected failure

Pass status and message in keyword used in teardown
    No operation
    [Teardown]    Keyword status should be    PASS

Fail status and message in keyword used in teardown
    Fail    Another expected fail
    [Teardown]    Keyword status should be    FAIL    Another expected fail

Multiple failures
    Run keyword and continue on failure    Fail    1st
    Fail   2nd
    [Teardown]    Keyword status should be    FAIL
    ...    Several failures occurred:\n\n1) 1st\n\n2) 2nd

Only continuable failures
    Run keyword and continue on failure    Fail    one
    Run keyword and continue on failure    Fail    two
    [Teardown]    Keyword status should be    FAIL
    ...    Several failures occurred:\n\n1) one\n\n2) two

Keyword status should be
    [Arguments]    ${status}    ${message}=    ${recurse}=yes
    Should be equal    ${KEYWORD STATUS}    ${status}
    Should be equal    ${KEYWORD MESSAGE}    ${message}
    [Teardown]    Run keyword if    "${recurse}" == "yes"
    ...    Keyword status should be    PASS    recurse=no

Status and message are not available if not in teardown
    Variable should not exist    ${KEYWORD STATUS}
    Variable should not exist    ${KEYWORD MESSAGE}

Status and message always contain latest values
    Fail    1
    [Teardown]    Status and message always contain latest values 2

Status and message always contain latest values 2
    Keyword status should be    FAIL    1
    Fail    2
    [Teardown]    Status and message always contain latest values 3

Status and message always contain latest values 3
    Keyword status should be    FAIL    2
    Fail    3
    [Teardown]    Status and message always contain latest values 4

Status and message always contain latest values 4
    Keyword status should be    FAIL    3
    [Teardown]    Status and message always contain latest values 5

Status and message always contain latest values 5
    Keyword status should be    PASS
    [Teardown]    Keyword status should be    PASS

Keyword teardown with keyword teardown
    Fail      My message
    [Teardown]   Another keyword teardown

Another keyword teardown
    Should be equal    ${KEYWORD STATUS}    FAIL
    Should be equal    ${KEYWORD MESSAGE}    My message
    Passing keyword status
    Passing keyword message
    Should be equal    ${KEYWORD STATUS}    FAIL
    Should be equal    ${KEYWORD MESSAGE}    My message
    [Teardown]      Should be equal    ${KEYWORD STATUS}-${KEYWORD MESSAGE}    PASS-
