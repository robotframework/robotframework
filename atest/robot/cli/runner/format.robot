*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Variables ***
${DATA FORMATS}    ${DATADIR}/parsing/data_formats

*** Test Cases ***
One format
    --format robot    20
    --FORMAT .TXT     39

Multiple formats
    -F robot:txt:.ROBOT    59

Invalid format
    [Template]    NONE
    Run Tests Without Processing Output    --format invalid    ${DATA FORMATS}
    Stderr Should Be Equal To    [ ERROR ] Invalid test data format 'invalid'.${USAGE TIP}\n

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}=0
    Run Tests    ${options}    ${DATA FORMATS}
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
