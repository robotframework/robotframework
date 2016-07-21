*** Settings ***
Resource        atest_resource.robot
Suite Setup     Run Tests    ${EMPTY}    misc/suites

*** Test Cases ***
Ids in output after test run
    Suite And Test Ids Should Be Correct

Ids in output after rebot
    Copy Previous Outfile
    Run Rebot    ${EMPTY}    ${OUTFILE COPY}
    Suite And Test Ids Should Be Correct

*** Keywords ***
Suite And Test Ids Should Be Correct
    Should Be Equal    ${SUITE.id}                                   s1
    Should Be Equal    ${SUITE.suites[0].id}                         s1-s1
    Should Be Equal    ${SUITE.suites[0].tests[-1].id}               s1-s1-t1
    Should Be Equal    ${SUITE.suites[1].suites[0].id}               s1-s2-s1
    Should Be Equal    ${SUITE.suites[1].suites[-1].id}              s1-s2-s2
    Should Be Equal    ${SUITE.suites[1].suites[-1].tests[-1].id}    s1-s2-s2-t1
    Should Be Equal    ${SUITE.suites[3].tests[-1].id}               s1-s4-t3
    Should Be Equal    ${SUITE.suites[-1].id}                        s1-s6
