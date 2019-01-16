*** Settings ***
Suite Setup       Run Tests    sources=standard_libraries/builtin/should_contain_any.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Contain Any
    Check test case    ${TESTNAME}

Should Contain Any failing
    Check test case    ${TESTNAME}

Should Contain Any without items fails
    Check test case    ${TESTNAME}

Should Contain Any case-insensitive
    ${tc}=    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)

Should Contain Any with invalid configuration
    Check test case    ${TESTNAME}

Should Not Contain Any
    Check test case    ${TESTNAME}

Should Not Contain Any failing
    Check test case    ${TESTNAME}

Should Not Contain Any without items fails
    Check test case    ${TESTNAME}

Should Not Contain Any case-insensitive
    ${tc}=    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    (case insensitive)

Should Not Contain Any with invalid configuration
    Check test case    ${TESTNAME}
