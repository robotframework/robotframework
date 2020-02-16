*** Settings ***
Resource       console_resource.robot
Suite Setup    Run Tests Without Processing Output   --consolemarkers on    ${TEST FILE}

*** Variables ***
${TEST FILE}    cli/console/markers.robot
${SEPARATOR}    -

*** Test Cases ***
Few Pass Markers
    Stdout Should Contain    SEPARATOR=\r
    ...    ${TESTNAME}${SPACE * 54}.....
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 54}| PASS |\n

Few Pass And Fail Markers
    Stdout Should Contain    SEPARATOR=
    ...    ${TESTNAME}${SPACE * 45}..F.F..\r
    ...    ${SPACE * 78}\r
    ...    ${TESTNAME}${SPACE * 45}| FAIL |\n
    ...    Several failures occurred:\n
    ...    \n
    ...    1) AssertionError\n
    ...    \n
    ...    2) AssertionError\n

More Markers Than Fit Into Status Area
    Stdout Should Contain    SEPARATOR=\r
    ...    ${TESTNAME}${SPACE * 32}........
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 32}........
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 32}........
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 32}.....
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 32}| PASS |\n

Warnings Are Shown Correctly
    Stdout Should Contain    SEPARATOR=\r
    ...    ${TESTNAME}${SPACE * 42}....
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 42}........
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 42}....
    ...    ${SPACE * 78}
    ...    ${TESTNAME}${SPACE * 42}| PASS |\n
    Stderr Should Contain    SEPARATOR=\n
    ...    [ WARN ] Warning
    ...    [ WARN ] Second warning

Errors Are Shown Correctly
    Stderr Should Contain    [ ERROR ] Error in file

Markers Can Be Disabled
    Run Tests And Verify That Markers Are Disabled    -K OFF

Markers Are Disabled By Default When Redirecting Output
    Run Tests And Verify That Markers Are Disabled    --ConsoleMarkers AuTo

Invalid Markers
    Run Tests Without Processing Output    -K InVaLid    ${TEST FILE}
    Stderr Should Be Equal To    [ ERROR ] Invalid console marker value 'InVaLid'. Available 'AUTO', 'ON' and 'OFF'.${USAGE TIP}\n

*** Keywords ***
Run Tests And Verify That Markers Are Disabled
    [Arguments]    ${opt}
    Run Tests Without Processing Output    ${opt}    ${TEST FILE}
    Stdout Should Contain    SEPARATOR=\n
    ...    Few Pass Markers${SPACE * 54}| PASS |
    ...    ${SEPARATOR * 78}
    ...    Few Pass And Fail Markers${SPACE * 45}| FAIL |
    ...    Several failures occurred:
    ...    ${EMPTY}
    ...    1) AssertionError
    ...    ${EMPTY}
    ...    2) AssertionError
    ...    ${SEPARATOR * 78}
    ...    More Markers Than Fit Into Status Area${SPACE * 32}| PASS |
    ...    ${SEPARATOR * 78}
    ...    Warnings Are Shown Correctly${SPACE * 42}| PASS |
