*** Settings ***
Documentation     These tests mainly verify that using BuiltIn externally does not cause importing problems as in
...               https://github.com/robotframework/robotframework/issues/654.
...               There are separate tests for creating and registering Run Keyword variants.
Suite Setup       Run Tests    --listener ${CURDIR}/listener_using_builtin.py    standard_libraries/builtin/used_in_custom_libs_and_listeners.robot
Resource          atest_resource.robot

*** Test Cases ***
Keywords Using BuiltIn
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Log level changed from INFO to DEBUG
    Check Log Message    ${tc.kws[0].msgs[1]}    Hello, debug world!    DEBUG

Listener Using BuiltIn
    Check Test Case    ${TESTNAME}

Use 'Run Keyword' with non-Unicode values
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    42
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    \\xff
