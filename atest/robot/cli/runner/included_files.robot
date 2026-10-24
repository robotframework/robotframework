*** Settings ***
Test Template      Expected number of tests should be run
Resource           atest_resource.robot

*** Variables ***
${MULTIPLE SOURCES}    ${DATADIR}/misc/suites/01__suite_with_prefix ${DATADIR}/misc/suites/subsuites

*** Test Cases ***
File name
    --parseinclude sample.robot                                          18

File path
    -I ${DATADIR}/parsing/data_formats${/}robot${/}SAMPLE.robot          18

Pattern with name
    --ParseInclude *.robot --parse-include sample.rb? -I no.match        49

Pattern with path
    --parse-include ${DATADIR}/parsing/data_formats/*/[st]???le.ROBOT    18

Single '*' is not recursive
    --parse-include ${DATADIR}/*/sample.robot                             0

Recursive glob requires '**'
    --parse-include ${DATADIR}/**/sample.robot                           18

Directories are recursive
    --parse-include ${DATADIR}/parsing/data_formats/robot                20
    --parse-include ${DATADIR}/parsing/*/robot                           20

Non-standard files matching patterns with extension are parsed
    --parse-include *.rst                                                20
    --parse-include ${DATADIR}/parsing/**/*.rst                          20
    --parse-include ${DATADIR}/parsing/data_formats/rest                  1

Multiple sources with matches only in some
    [Template]    NONE
    Run Tests    --parseinclude sub1.robot    ${MULTIPLE SOURCES}
    Should Contain Tests    ${SUITE}    SubSuite1 First

Multiple sources without matches
    [Template]    NONE
    ${result} =    Run Tests Without Processing Output    --parseinclude no.match    ${MULTIPLE SOURCES}
    Should Be Equal    ${result.rc}    ${252}
    Stderr Should Match Regexp    \\[ ERROR \\] Suite 'Suite With Prefix & Subsuites' contains no tests or tasks.${USAGE TIP}

*** Keywords ***
Expected number of tests should be run
    [Arguments]    ${options}    ${expected}
    Run Tests    ${options} --run-empty-suite    ${DATADIR}/parsing/data_formats
    Should Be Equal As Integers    ${SUITE.test_count}    ${expected}
