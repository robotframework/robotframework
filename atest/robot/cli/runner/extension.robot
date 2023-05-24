*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Variables ***
${DATA FORMATS}    ${DATADIR}/parsing/data_formats

*** Test Cases ***
One extension
    --extension robot      29
    --EXTENSION .TXT       23

Multiple extensions
    -F robot:txt:.ROBOT    52

Any extension is accepted
    --extension bar        1
    --extension FoO:bar    2

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}=0
    Run Tests    ${options}    ${DATA FORMATS}
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
