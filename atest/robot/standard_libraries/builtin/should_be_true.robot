*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/should_be_true.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Be True
    Check test case    ${TESTNAME}

Should Be True with message
    Check test case    ${TESTNAME}

Should Be True with invalid expression
    Check test case    ${TESTNAME}

Should Not Be True
    Check test case    ${TESTNAME}

Should Not Be True with message
    Check test case    ${TESTNAME}

Should Not Be True with invalid expression
    Check test case    ${TESTNAME}

Should (Not) Be True automatically imports modules
    Check test case    ${TESTNAME}

Should (Not) Be True is evaluated with robot's variables
    Check test case    ${TESTNAME}
