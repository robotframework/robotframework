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
    Check Log Message    ${tc[0, 0]}    ${EMPTY}
    Check Log Message    ${tc[1, 0]}    RF
    Should Be Empty      ${tc[2].messages}

Failed
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Error: RF    FAIL
    Check Log Message    ${tc[0, 1]}    Traceback: RF    DEBUG
