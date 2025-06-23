*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/setup_and_teardown_using_embedded_arguments.robot
Resource          atest_resource.robot

*** Test Cases ***
Suite setup and teardown
    Should Be Equal    ${SUITE.setup.name}       Embedded "arg"
    Should Be Equal    ${SUITE.teardown.name}    Object \${LIST}

Test setup and teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}          Embedded "arg"
    Should Be Equal    ${tc.teardown.name}       Embedded "arg"

Keyword setup and teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc[0].setup.name}       Embedded "arg"
    Should Be Equal    ${tc[0].teardown.name}    Embedded "arg"

Argument as variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}          Embedded "\${ARG}"
    Should Be Equal    ${tc[0].setup.name}       Embedded "\${ARG}"
    Should Be Equal    ${tc[0].teardown.name}    Embedded "\${ARG}"
    Should Be Equal    ${tc.teardown.name}       Embedded "\${ARG}"

Argument as non-string variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}          Object \${LIST}
    Should Be Equal    ${tc[0].setup.name}       Object \${LIST}
    Should Be Equal    ${tc[0].teardown.name}    Object \${LIST}
    Should Be Equal    ${tc.teardown.name}       Object \${LIST}

Argument matching only after replacing variables
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}          Embedded "arg"
    Should Be Equal    ${tc[0].setup.name}       Embedded "arg"
    Should Be Equal    ${tc[0].teardown.name}    Embedded "arg"
    Should Be Equal    ${tc.teardown.name}       Embedded "arg"

Exact match after replacing variables has higher precedence
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}          Embedded not, exact match instead
    Should Be Equal    ${tc[0].setup.name}       Embedded not, exact match instead
    Should Be Equal    ${tc[0].teardown.name}    Embedded not, exact match instead
    Should Be Equal    ${tc.teardown.name}       Embedded not, exact match instead
