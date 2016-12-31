*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Variables ***
${DATA FORMATS}    ${DATADIR}/parsing/data_formats

*** Test Cases ***
One extension
    --extension robot    20
    --EXTENSION .TXT     39

Multiple extensions
    -F robot:txt:.ROBOT    59

Invalid extension
    [Template]    NONE
    Run Tests Without Processing Output    --extension invalid    ${DATA FORMATS}
    Stderr Should Be Equal To    [ ERROR ] Invalid extension to limit parsing 'invalid'.${USAGE TIP}\n

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}=0
    Run Tests    ${options}    ${DATA FORMATS}
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
