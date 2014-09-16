*** Settings ***
Suite Setup     Check That Default Orders Are Correct
Force Tags      pybot  jybot  regression
Resource        ../cli_resource.robot

*** Variables ***
${DEFAULT SUITE ORDER}  [Suite First, Sub.Suite.1, Suite3, Suite4, Suite5, Suite10, Suite 6, SUite7, suiTe 8, Suite 9 Name]
${DEFAULT TEST ORDER}  [test1, test2, test3, test4, test5, test6, test7, test8, test9, test10, test11, test12]

*** Test Cases ***
Randomizing Tests
    [Setup]  Run Tests  --runmode random:test  misc/multiple_suites/01__suite_first.robot
    Should Not Be Equal As Strings  ${SUITE.tests}  ${DEFAULT TEST ORDER}

Randomizing Suites
    [Setup]  Run Tests  --runmode RANDOM:SuitE  misc/multiple_suites
    Should Not Be Equal As Strings  ${SUITE.suites}  ${DEFAULT SUITE ORDER}
    ${tests} =  Get Tests
    Should Be Equal As Strings  ${tests}  ${DEFAULT TEST ORDER}

Randomizing Suites And Tests
    [Setup]  Run Tests  --runmode random:all  misc/multiple_suites
    Should Not Be Equal As Strings  ${SUITE.suites}  ${DEFAULT SUITE ORDER}
    ${tests} =  Get Tests
    Should Not Be Equal As Strings  ${tests}  ${DEFAULT TEST ORDER}

*** Keywords ***
Check That Default Orders Are Correct
    Run Tests  ${EMPTY}  misc/multiple_suites
    Should Be Equal As Strings  ${SUITE.suites}  ${DEFAULT SUITE ORDER}
    Should Be Equal As Strings  ${SUITE.suites[0].tests}  ${DEFAULT TEST ORDER}

Get Tests
    Comment  This keyword is needed as there is also one directory suite, which does not contain tests.
    ${tests} =  Set Variable If  '${SUITE.suites[0].name}' == 'Sub.Suite.1'  ${SUITE.suites[0].suites[0].tests}  ${SUITE.suites[0].tests}
    [Return]  ${tests}
