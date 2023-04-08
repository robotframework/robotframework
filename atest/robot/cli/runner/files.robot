*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Variables ***
${DATA FORMATS}    ${DATADIR}/parsing/data_formats

*** Test Cases ***

Simple filename
    -f sample.robot                 18

Filtering by extension
    --files *.robot                 27
    --FILES *.txt                   23

Multiple patterns
    --files *.robot --files *.txt   50

Any extension is accepted
    --files *.bar                   1
    --files *.FoO --files *.bar     2

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}=0
    Run Tests    ${options}    ${DATA FORMATS}
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
