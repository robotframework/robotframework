*** Settings ***
Documentation       Run testdata and validate that suite names are set correctly
Suite Setup         Run Tests    ${EMPTY}    misc/suites
Resource            atest_resource.robot

*** Test Cases ***
Custom Suite Name
    Should Be Equal    ${SUITE.suites[2].name}    Subsuites
    Should Be Equal    ${SUITE.suites[2].suites[0].name}    Custom sub1 Name

Default File Suite Name
    Should Be Equal    ${SUITE.suites[2].name}    Subsuites
    Should Be Equal    ${SUITE.suites[2].suites[1].name}    Sub2

Cutom Suite Name With Parent init
    Should Be Equal    ${SUITE.suites[3].name}    Custom Parent Suite Name
    Should Be Equal    ${SUITE.suites[3].suites[0].name}    Sub.Suite.4
    Should Be Equal    ${SUITE.suites[3].suites[2].name}    SubSuite333

Custom Child Suite Name
    Should Be Equal    ${SUITE.suites[3].suites[1].name}    SubParentSuite3Name
    Should Be Equal    ${SUITE.suites[3].suites[1].suites[0].name}    Another Custom Sub Suite
