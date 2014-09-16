*** Settings ***
Suite Setup     Run Tests  --exclude jybot_only  standard_libraries/dialogs/dialogs.robot
Force Tags      regression  manual
Default Tags    jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
Pause Execution
    Check Test Case  ${TESTNAME}

Pause Execution With Long Line
    Check Test Case  ${TESTNAME}

Pause Execution With Multiple Lines
    Check Test Case  ${TESTNAME}

Execute Manual Step Passing
    Check Test Case  ${TESTNAME}

Execute Manual Step Failing
    Check Test Case  ${TESTNAME}

Get Value From User
    Check Test Case  ${TESTNAME}

Get Empty Value From User
    Check Test Case  ${TESTNAME}

Get Hidden Value From User
    Check Test Case  ${TESTNAME}

Get Value From User Cancelled
    Check Test Case  ${TESTNAME}

Get Value From User Exited
    Check Test Case  ${TESTNAME}

Get Selection From User
    Check Test Case  ${TESTNAME}

Get Selection From User Cancelled
    Check Test Case  ${TESTNAME}

Get Selection From User Exited
    Check Test Case  ${TESTNAME}

Multiple dialogs in a row
    Check Test Case  ${TESTNAME}

Dialog and timeout
    [Tags]    jybot
    Run Tests  --include jybot_only  standard_libraries/dialogs/dialogs.robot
    Check Test Case  ${TESTNAME}  FAIL  Test timeout 1 second exceeded.
