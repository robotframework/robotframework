*** Settings ***
Documentation     Continuable and fatal errors.
Library           Remote    127.0.0.1:${PORT}
Suite Setup       Set Log Level    DEBUG

*** Variables ***
${PORT}           8270

*** Test Cases ***
Continuable
    [Documentation]  FAIL Several failures occurred:\n\n
    ...    1) message\n\n
    ...    2) second message\n\n
    ...    3) third message
    Continuable    message    trace1
    Continuable    second message    trace2
    Continuable    third message    trace3

Fatal
    [Documentation]  FAIL Execution ends here
    Fatal    Execution ends here    with this traceback
    Fail    This should not be executed

Fails due to earlier fatal error
    [Documentation]  FAIL Test execution stopped due to a fatal error.
    Fail    This should not be executed
