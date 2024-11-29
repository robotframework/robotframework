*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    core/keyword_setup.robot
Resource          atest_resource.robot

*** Test Cases ***
Passing setup
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message     ${tc[0].setup[0]}             Hello, setup!

Failing setup
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0].setup[0]}              Hello, setup!          FAIL
    Should Be Equal      ${tc[0, 0].status}             NOT RUN

Failing setup and passing teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.setup.setup[0]}           Hello, setup!          FAIL
    Should Be Equal      ${tc.setup[0].status}          NOT RUN
    Check Log Message    ${tc.setup.teardown[0]}        Hello, teardown!       INFO

Failing setup and teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0].setup[0]}              Hello, setup!          FAIL
    Should Be Equal      ${tc[0, 0].status}             NOT RUN
    Check Log Message    ${tc[0].teardown[0]}           Hello, teardown!       FAIL

Continue-on-failure mode is not enabled in setup
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.setup.setup[0, 0]}        Hello, setup!          INFO
    Check Log Message    ${tc.setup.setup[1, 0]}        Hello again, setup!    FAIL
    Should Be Equal      ${tc.setup.setup[2].status}    NOT RUN

NONE is same as no setup
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal      ${tc[0].setup.name}            ${None}

Empty [Setup] is same as no setup
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal      ${tc[0].setup.name}            ${None}

Using variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal      ${tc[0].setup.name}            Log
    Should Be Equal      ${tc[1].setup.name}            ${None}
    Should Be Equal      ${tc[2].setup.name}            ${None}
    Should Be Equal      ${tc[3].setup.name}            Fail
