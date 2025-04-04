*** Settings ***
Documentation     These tests mainly verify that using BuiltIn externally does not cause importing problems as in
...               https://github.com/robotframework/robotframework/issues/654.
...               There are separate tests for creating and registering Run Keyword variants.
Suite Setup       Run Tests    --listener ${CURDIR}/listener_using_builtin.py    standard_libraries/builtin/used_in_custom_libs_and_listeners.robot
Resource          atest_resource.robot

*** Test Cases ***
Keywords Using BuiltIn
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Log level changed from NONE to DEBUG.    DEBUG
    Check Log Message    ${tc[0, 1]}    Hello, debug world!    DEBUG
    Length should be     ${tc[0].messages}    2

Listener Using BuiltIn
    Check Test Case    ${TESTNAME}

Use 'Run Keyword' with non-Unicode values
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0]}    42
    Check Log Message    ${tc[0, 1, 0]}    \xff

Use BuiltIn keywords with timeouts
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}       Log level changed from NONE to DEBUG.    DEBUG
    Check Log Message    ${tc[0, 1]}       Hello, debug world!    DEBUG
    Length should be     ${tc[0].messages}    2
    Check Log Message    ${tc[3, 0, 0]}    Test timeout 1 day active. * seconds left.    level=DEBUG    pattern=True
    Check Log Message    ${tc[3, 0, 1]}    42
    Check Log Message    ${tc[3, 1, 0]}    Test timeout 1 day active. * seconds left.    level=DEBUG    pattern=True
    Check Log Message    ${tc[3, 1, 1]}    \xff

User keyword used via 'Run Keyword'
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0, 0]}    This is x-911-zzz

User keyword used via 'Run Keyword' with timeout and trace level
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 1, 0, 1]}    This is x-911-zzz
