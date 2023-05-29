*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Test Cases ***
File name
    -f sample.robot                                                18

File path
    -f ${DATADIR}/parsing/data_formats${/}robot${/}SAMPLE.robot    18

Pattern with name
    --files *.robot --files sample.rb?                             47

Pattern with path
    -f ${DATADIR}/parsing/data_formats/*/[st]???le.ROBOT           18

Recursive glob
    -f ${DATADIR}/**/sample.robot                                  18
    -f ${DATADIR}/*/sample.robot --run-empty-suite                  0

Directories are recursive
    -f ${DATADIR}/parsing/data_formats/robot                       20
    -f ${DATADIR}/parsing/data_formats/r*t -F robot:rst            40

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}
    Run Tests    ${options}    ${DATADIR}/parsing/data_formats
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
