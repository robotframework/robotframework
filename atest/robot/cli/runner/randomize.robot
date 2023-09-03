*** Settings ***
Suite Setup     Check That Default Orders Are Correct
Resource        cli_resource.robot

*** Variables ***
@{DEFAULT SUITE ORDER}    Suite First    Sub.Suite.1    Suite3     Suite4     Suite5
...                       Suite10        Suite 6        SUite7     suiTe 8    Suite 9 Name
@{DEFAULT TEST ORDER}     test1          test2          test3      test4      test5
...                       test6          test7          test8      test9      test10
...                       test11         test12

*** Test Cases ***
Randomizing tests
    [Setup]  Run Tests  --randomize test  misc/multiple_suites/01__suite_first.robot
    Should Not Be Equal As Strings  ${SUITE.tests}  ${DEFAULT TEST ORDER}
    Randomized metadata is added    Tests

Randomizing suites
    [Setup]  Run Tests  --randomize Suites  misc/multiple_suites
    Suites should be randomized
    Tests should be in default order
    Randomized metadata is added    Suites

Randomizing suites and tests
    [Setup]  Run Tests  --randomize all  misc/multiple_suites
    Suites should be randomized
    Tests should be randomized
    Randomized metadata is added    Suites and tests

Randomizing tests with seed
    Run Tests  --randomize test:1234  misc/multiple_suites
    ${suites1} =    Suites should be in default order
    ${tests1} =    Tests should be randomized
    Randomized metadata is added    Tests    1234
    Run Tests  --randomize TESTS:1234  misc/multiple_suites
    ${suites2} =    Suites should be in default order
    ${tests2} =    Tests should be randomized
    Randomized metadata is added    Tests    1234
    Order should be same    ${suites1}    ${suites2}
    Order should be same    ${tests1}    ${tests2}

Randomizing suites with seed
    Run Tests  --randomize Suite:42  misc/multiple_suites
    ${suites1} =    Suites should be randomized
    ${tests1} =    Tests should be in default order
    Randomized metadata is added    Suites    42
    Run Tests  --randomize SuiteS:42  misc/multiple_suites
    ${suites2} =    Suites should be randomized
    ${tests2} =    Tests should be in default order
    Randomized metadata is added    Suites    42
    Order should be same    ${suites1}    ${suites2}
    Order should be same    ${tests1}    ${tests2}

Randomizing suites and tests with seed
    Run Tests  --randomize all:123456  misc/multiple_suites
    ${suites1} =    Suites should be randomized
    ${tests1} =    Tests should be randomized
    Randomized metadata is added    Suites and tests    123456
    Run Tests  --randomize ALL:123456  misc/multiple_suites
    ${suites2} =    Suites should be randomized
    ${tests2} =    Tests should be randomized
    Randomized metadata is added    Suites and tests    123456
    Order should be same    ${suites1}    ${suites2}
    Order should be same    ${tests1}    ${tests2}

Last option overrides all previous
    [Setup]    Run Tests    --randomize suites --randomize tests --randomize none    misc/multiple_suites
    Suites should be in default order
    Tests should be in default order

Invalid option value
    Run Should Fail    --randomize INVALID ${TESTFILE}
    ...    Invalid value for option '--randomize': Expected 'TESTS', 'SUITES', 'ALL' or 'NONE', got 'INVALID'.

Invalid seed value
    Run Should Fail    --randomize all:bad ${TESTFILE}
    ...    Invalid value for option '--randomize': Seed should be integer, got 'BAD'.

*** Keywords ***
Check That Default Orders Are Correct
    Run Tests    ${EMPTY}    misc/multiple_suites
    Suites should be in default order
    Tests should be in default order

Suites Should Be Randomized
    Should Not Be Equal    ${{[suite.name for suite in $SUITE.suites]}}    ${DEFAULT SUITE ORDER}
    RETURN    ${SUITE.suites}

Suites should be in default order
    Should Be Equal    ${{[suite.name for suite in $SUITE.suites]}}    ${DEFAULT SUITE ORDER}
    RETURN    ${SUITE.suites}

Tests Should Be Randomized
    ${tests} =  Get Tests
    Should Not Be Equal    ${{[test.name for test in $tests]}}    ${DEFAULT TEST ORDER}
    RETURN    ${tests}

Tests should be in default order
    ${tests} =  Get Tests
    Should Be Equal    ${{[test.name for test in $tests]}}    ${DEFAULT TEST ORDER}
    RETURN    ${tests}

Order should be same
    [Arguments]    ${first}    ${second}
    Should Be Equal As Strings    ${first}    ${second}

Get Tests
    # This keyword is needed because 'Sub.Suite.1' is directory and thus doesn't itself have tests
    ${tests} =  Set Variable If  '${SUITE.suites[0].name}' == 'Sub.Suite.1'  ${SUITE.suites[0].suites[0].tests}  ${SUITE.suites[0].tests}
    RETURN    ${tests}

Randomized metadata is added
    [Arguments]    ${what}    ${seed}=*
    Should Match    ${SUITE.metadata['Randomized']}    ${what} (seed ${seed})
    FOR    ${child}    IN    @{SUITE.suites}
        Should Not Contain    ${child.metadata}    Randomized
    END
