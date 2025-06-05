*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/setup_and_teardown_using_embedded_arguments.robot
Resource          atest_resource.robot

*** Test Cases ***
Suite setup and teardown
    Should Be Equal    ${SUITE.setup.name}       Embedded \${LIST}
    Should Be Equal    ${SUITE.teardown.name}    Embedded \${LIST}

Test setup and teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}          Embedded \${LIST}
    Should Be Equal    ${tc.teardown.name}       Embedded \${LIST}

Keyword setup and teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc[0].setup.name}       Embedded \${LIST}
    Should Be Equal    ${tc[0].teardown.name}    Embedded \${LIST}

Exact match after replacing variables has higher precedence
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}          Embedded not, exact match instead
    Should Be Equal    ${tc.teardown.name}       Embedded not, exact match instead
    Should Be Equal    ${tc[0].setup.name}       Embedded not, exact match instead
    Should Be Equal    ${tc[0].teardown.name}    Embedded not, exact match instead
