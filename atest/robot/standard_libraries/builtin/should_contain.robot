*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/should_contain.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Contain
    Check test case    ${TESTNAME}

Should Contain with non-strings
    Check test case    ${TESTNAME}

Should Contain case-insensitive
    Check Test Case    ${TESTNAME}

Should Not Contain
    Check test case    ${TESTNAME}

Should Not Contain with non-strings
    Check test case    ${TESTNAME}

Should Not Contain case-insensitive
    Check Test Case    ${TESTNAME}
