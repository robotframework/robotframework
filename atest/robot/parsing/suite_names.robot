*** Settings ***
Documentation       Run testdata and validate that suite names are set correctly
Suite Setup         Run Tests    ${EMPTY}    misc/suites
Test Template       Should Be Equal
Resource            atest_resource.robot

*** Test Cases ***
Default directory suite name
    ${SUITE.name}                          Suites

Default file suite name
    ${SUITE.suites[1].name}                Fourth

Default name with prefix
    ${SUITE.suites[0].name}                Suite With Prefix
    ${SUITE.suites[0].suites[0].name}      Tests With Prefix

Name with double underscore at end
    ${SUITE.suites[4].name}                Suite With Double Underscore
    ${SUITE.suites[4].suites[0].name}      Tests With Double Underscore

Custom directory suite name
    ${SUITE.suites[3].name}                Custom name for 📂 'subsuites2'

Custom file suite name
    ${SUITE.suites[3].suites[1].name}      Custom name for 📜 'subsuite3.robot'
