*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/setup_and_teardown_using_embedded_arguments.robot
Resource          atest_resource.robot

*** Test Cases ***
Suite setup and teardown
    Should Be Equal    ${SUITE.setup.status}      PASS
    Should Be Equal    ${SUITE.teardown.status}   PASS

Test setup and teardown
    Check Test Case    ${TESTNAME}

Keyword setup and teardown
    Check Test Case    ${TESTNAME}
