*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Variables ***
${DATA FORMATS}    ${DATADIR}/parsing/data_formats

*** Test Cases ***
Simple filename
    -f sample.robot                 18

Pattern
    --files *.robot                 29

Multiple patterns
    --files sample.robot --files tests.robot    27

Combine extension and files
    --files sample.rst -F rst       18

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}=0
    Run Tests    ${options}    ${DATA FORMATS}
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
