*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/should_contain.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Contain
    Check test case    ${TESTNAME}

Should Contain with non-strings
    Check test case    ${TESTNAME}

Should Contain case-insensitive
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)

Should Not Contain
    Check test case    ${TESTNAME}

Should Not Contain with non-strings
    Check test case    ${TESTNAME}

Should Not Contain case-insensitive
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)
