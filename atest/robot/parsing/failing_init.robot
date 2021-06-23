*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    parsing/failing_init/
Resource        atest_resource.robot

*** Test Cases ***
Failing Init
    Should Be Equal    ${SUITE.doc}    This should exist
    Error In File    0    parsing/failing_init/__init__.robot    1
    ...    'Test Cases' section is not allowed in suite initialization file.
    Check Test Case    Fail Init
