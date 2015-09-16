*** Settings ***
Suite Setup      Run Remote Tests    special_errors.robot    specialerrors.py
Resource         remote_resource.robot

*** Test Cases ***
Continuable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    message    FAIL
    Check Log Message    ${tc.kws[0].msgs[1]}    trace1    DEBUG
    Check Log Message    ${tc.kws[1].msgs[0]}    second message    FAIL
    Check Log Message    ${tc.kws[1].msgs[1]}    trace2    DEBUG
    Check Log Message    ${tc.kws[2].msgs[0]}    third message    FAIL
    Check Log Message    ${tc.kws[2].msgs[1]}    trace3    DEBUG

Fatal
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Execution ends here    FAIL
    Check Log Message    ${tc.kws[0].msgs[1]}    with this traceback    DEBUG
    Check Test Case    Fails due to earlier fatal error
