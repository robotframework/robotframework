*** Settings ***
Resource          atest_resource.robot
Library           expected_output/ExpectedOutputLibrary.py

*** Variables ***
${SEP_CHAR1}      =
${SEP_CHAR2}      -
${SEP_LINE1}      ${SEP_CHAR1 * 78}
${SEP_LINE2}      ${SEP_CHAR2 * 78}
${MSG_211}        2 tests, 1 passed, 1 failed
${MSG_110}        1 test, 1 passed, 0 failed

*** Keywords ***
Create Status Line
    [Arguments]    ${name}    ${padding}    ${status}
    RETURN    ${name}${SPACE * ${padding}}| ${status} |

Stdout Should Be
    [Arguments]    ${expected}    &{replaced}
    Output Should Be     ${STDOUT FILE}    ${expected}    &{replaced}

Stderr Should Be
    [Arguments]    ${expected}    &{replaced}
    Output Should Be     ${STDERR FILE}    ${expected}    &{replaced}
