*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/continue_on_failure_tag.robot
Resource          atest_resource.robot

*** Test Cases ***
Continue in test with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in user kewyord with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in test with tag and UK without tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in test with tag and nested UK with and without tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in for loop with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in for loop without tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in for loop in UK with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in for loop in UK without tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in IF with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in IF without tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in IF in UK with tag
    ${tc}=    Check Test Case    ${TESTNAME}

Continue in IF in UK without tag
    ${tc}=    Check Test Case    ${TESTNAME}
