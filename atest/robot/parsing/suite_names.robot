*** Settings ***
Documentation       Tests for default and custom suite names.
...                 Using `--name` is tested elsewhere.
Suite Setup         Run Tests    ${EMPTY}    misc/suites misc/multiple_suites
Test Template       Should Be Equal
Resource            atest_resource.robot

*** Test Cases ***
Combined suite name
    ${SUITE.name}                                  Suites & Multiple Suites

Directory suite name
    ${SUITE.suites[0].name}                        Suites
    ${SUITE.suites[1].name}                        Multiple Suites

File suite name
    ${SUITE.suites[0].suites[1].name}              Fourth
    ${SUITE.suites[1].suites[9].name}              Suite 9 Name

Names with upper case chars are not title cased
    ${SUITE.suites[1].suites[7].name}              SUite7
    ${SUITE.suites[1].suites[8].name}              suiTe 8
    ${SUITE.suites[1].suites[1].suites[1].name}    .Sui.te.2.

Spaces are preserved
    ${SUITE.suites[1].suites[6].name}              Suite 6

Dots in name
    ${SUITE.suites[1].suites[1].name}              Sub.Suite.1
    ${SUITE.suites[1].suites[1].suites[1].name}    .Sui.te.2.

Name with prefix
    ${SUITE.suites[0].suites[0].name}              Suite With Prefix
    ${SUITE.suites[0].suites[0].suites[0].name}    Tests With Prefix
    ${SUITE.suites[1].suites[1].name}              Sub.Suite.1

Name with double underscore at end
    ${SUITE.suites[0].suites[4].name}              Suite With Double Underscore
    ${SUITE.suites[0].suites[4].suites[0].name}    Tests With Double Underscore

Custom directory suite name
    ${SUITE.suites[0].suites[3].name}              Custom name for 📂 'subsuites2'

Custom file suite name
    ${SUITE.suites[0].suites[3].suites[1].name}    Custom name for 📜 'subsuite3.robot'
