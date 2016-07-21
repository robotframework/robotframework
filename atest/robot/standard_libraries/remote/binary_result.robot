*** Settings ***
Suite Setup      Run Remote Tests    binary_result.robot    binaryresult.py
Resource         remote_resource.robot

*** Test Cases ***
Returned
    Check Test Case    ${TESTNAME}

Returned in list
    Check Test Case    ${TESTNAME}

Returned in dict
    Check Test Case    ${TESTNAME}

Returned in nested structure
    Check Test Case    ${TESTNAME}

Logged
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${EMPTY}
    Check Log Message    ${tc.kws[1].msgs[0]}    RF
    Should Be Empty    ${tc.kws[2].msgs}

Failed
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Error: RF    FAIL
    Check Log Message    ${tc.kws[0].msgs[1]}    Traceback: RF    DEBUG
