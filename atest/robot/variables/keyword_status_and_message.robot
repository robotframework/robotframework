*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/keyword_status_and_message.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Pass status directly in teardown
    Check Test Case    ${TESTNAME}

Pass message directly in teardown
    Check Test Case    ${TESTNAME}

Fail status directly in teardown
    Check Test Case    ${TESTNAME}

Fail message directly in teardown
    Check Test Case    ${TESTNAME}

Pass status and message in keyword used in teardown
    Check Test Case    ${TESTNAME}

Fail status and message in keyword used in teardown
    Check Test Case    ${TESTNAME}

Status and message when keyword fails multiple times
    Check Test Case    ${TESTNAME}

Status and message when there are only continuable failures
    Check Test Case    ${TESTNAME}

Status and message are not available if not in teardown
    Check Test Case    ${TESTNAME}

Status and message are not available after teardown
    Check Test Case    ${TESTNAME}

Previous status and message are not overwritten
    Check Test Case    ${TESTNAME}

Status and message always contain latest values
    Check Test Case    ${TESTNAME}
