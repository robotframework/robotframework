*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/length.robot
Resource          builtin_resource.robot

*** Test Cases ***
Get Length
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0]}    Length is 0.
    Check Log Message    ${tc[1, 0, 0]}    Length is 1.
    Check Log Message    ${tc[2, 0, 0]}    Length is 2.
    Check Log Message    ${tc[3, 0, 0]}    Length is 3.
    Check Log Message    ${tc[4, 0, 0]}    Length is 11.
    Check Log Message    ${tc[5, 0, 0]}    Length is 0.

Length Should Be
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[-1, 0]}      Length is 2.
    Check Log Message    ${tc[-1, 1]}      Length of '*' should be 3 but is 2.    FAIL    pattern=yep
    Check Log Message    ${tc[-1, 2]}      Traceback*    DEBUG    pattern=yep
    Length Should Be     ${tc[-1].body}    3

Length Should Be with custom message
    Check Test Case    ${TESTNAME}

Length Should Be with invalid length
    Check Test Case    ${TESTNAME}

Should Be Empty
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Should Be Empty with custom message
    Check Test Case    ${TESTNAME}

Should Not Be Empty
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Should Not Be Empty with custom message
    Check Test Case    ${TESTNAME}

Getting length with `length` method is deprecated
    ${tc} =    Check Test Case    ${TESTNAME}
    Check custom length deprecation    ${tc[0, 0]}    item.length()    40
    Check custom length deprecation    ${tc[1]}       item.length()    40
    Check custom length deprecation    ${tc[2]}       item.length()    40
    Check custom length deprecation    ${tc[3]}       item.length()    40

Getting length with `size` method is deprecated
    ${tc} =    Check Test Case    ${TESTNAME}
    Check custom length deprecation    ${tc[0, 0]}    item.size()    41
    Check custom length deprecation    ${tc[1]}       item.size()    41
    Check custom length deprecation    ${tc[2]}       item.size()    41
    Check custom length deprecation    ${tc[3]}       item.size()    41

Getting length with `length` attribute is deprecated
    ${tc} =    Check Test Case    ${TESTNAME}
    Check custom length deprecation    ${tc[0, 0]}    item.length    42
    Check custom length deprecation    ${tc[1]}       item.length    42
    Check custom length deprecation    ${tc[2]}       item.length    42
    Check custom length deprecation    ${tc[3]}       item.length    42

*** Keywords ***
Check custom length deprecation
    [Arguments]    ${kw}    ${deprecated}    ${length}
    Check Log Message    ${kw[0]}    Using '${deprecated}' for getting object length is deprecated. Only 'len(obj)' will be supported in the future.    WARN
    Check Log Message    ${kw[1]}    Length is ${length}.
