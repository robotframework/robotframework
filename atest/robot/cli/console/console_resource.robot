*** Settings ***
Resource          atest_resource.robot
Library           expected_output/ExpectedOutputLibrary.py

*** Variables ***
${SEP_CHAR1}      =
${SEP_CHAR2}      -
${SEP_LINE1}      ${SEP_CHAR1 * 78}
${SEP_LINE2}      ${SEP_CHAR2 * 78}
${MSG_211}        2 critical tests, 1 passed, 1 failed, 0 skipped\n 2 tests total, 1 passed, 1 failed, 0 skipped
${MSG_110}        1 critical test, 1 passed, 0 failed, 0 skipped\n 1 test total, 1 passed, 0 failed, 0 skipped

*** Keywords ***
Create Status Line
    [Arguments]    ${name}    ${padding}    ${status}
    [Return]    ${name}${SPACE * ${padding}}| ${status} |

Stdout Should Be
    [Arguments]    ${expected}    &{replaced}
    Output Should Be     ${STDOUT FILE}    ${expected}    &{replaced}

Stderr Should Be
    [Arguments]    ${expected}    &{replaced}
    Output Should Be     ${STDERR FILE}    ${expected}    &{replaced}
