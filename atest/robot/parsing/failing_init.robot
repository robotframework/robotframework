*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    parsing/failing_init/
Resource        atest_resource.robot

*** Test Cases ***
Failing Init
    Should Be Equal    ${SUITE.doc}    This should exist
    ${path} =    Normalize Path    ${DATADIR}/parsing/failing_init/
    Check Log Message    ${ERRORS[0]}    Test suite initialization file in '${path}' cannot contain tests or tasks.    ERROR
    Check Test Case    Fail Init
