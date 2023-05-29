*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Test Cases ***
File name
    --parseinclude sample.robot                                          18

File path
    --ParseI ${DATADIR}/parsing/data_formats${/}robot${/}SAMPLE.robot    18

Pattern with name
    --ParseInclude *.robot --parse-include sample.rb?                    47

Pattern with path
    --parse-include ${DATADIR}/parsing/data_formats/*/[st]???le.ROBOT    18

Recursive glob
    --parse-include ${DATADIR}/**/sample.robot                           18
    --parse-include ${DATADIR}/*/sample.robot --run-empty-suite           0

Directories are recursive
    --parse-include ${DATADIR}/parsing/data_formats/robot                20
    --parse-include ${DATADIR}/parsing/data_formats/r*t -F robot:rst     40

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}
    Run Tests    ${options}    ${DATADIR}/parsing/data_formats
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
