*** Settings ***
Suite Setup     Run Tests And Remove Keywords
Resource        atest_resource.robot

*** Variables ***
${PASS MESSAGE}    -PASSED -ALL
${FAIL MESSAGE}    -ALL +PASSED
${REMOVED FOR MESSAGE}     -FOR -ALL
${KEPT FOR MESSAGE}        +FOR -ALL
${REMOVED WHILE MESSAGE}     -WHILE -ALL
${KEPT WHILE MESSAGE}        +WHILE -ALL
${REMOVED WUKS MESSAGE}    -WUKS -ALL
${KEPT WUKS MESSAGE}       +WUKS -ALL
${REMOVED BY NAME MESSAGE}    -BYNAME -ALL
${KEPT BY NAME MESSAGE}    +BYNAME -ALL
${REMOVED BY PATTERN MESSAGE}    -BYPATTERN -ALL
${KEPT BY PATTERN MESSAGE}    +BYPATTERN -ALL

*** Test Cases ***
PASSED option when test passes
    Log should not contain    ${PASS MESSAGE}
    Output should contain pass message

PASSED option when test fails
    Log should contain        ${FAIL MESSAGE}
    Output should contain fail message

FOR option
    Log should not contain    ${REMOVED FOR MESSAGE}
    Log should contain        ${KEPT FOR MESSAGE}
    Output should contain for messages

WHILE option
    Log should not contain    ${REMOVED WHILE MESSAGE}
    Log should contain        ${KEPT WHILE MESSAGE}
    Output should contain while messages

WUKS option
    Log should not contain    ${REMOVED WUKS MESSAGE}
    Log should contain        ${KEPT WUKS MESSAGE}
    Output should contain WUKS messages

NAME option
    Log should not contain    ${REMOVED BY NAME MESSAGE}
    Log should contain        ${KEPT BY NAME MESSAGE}
    Output should contain NAME messages

NAME option with pattern
    Log should not contain    ${REMOVED BY PATTERN MESSAGE}
    Log should contain        ${KEPT BY PATTERN MESSAGE}
    Output should contain NAME messages with patterns

TAGged keywords
    Log should contain        This is not removed by TAG
    Log should not contain    This is removed by TAG

Warnings and errors are preserved
    Log should contain        Keywords with warnings are not removed
    Log should contain        Keywords with errors are not removed
    Output should contain warning and error

*** Keywords ***
Run tests and remove keywords
    VAR    ${opts}
    ...    --removekeywords passed
    ...    --RemoveKeywords FoR
    ...    --RemoveKeywords whiLE
    ...    --removek WUKS
    ...    --removekeywords name:RemoveByName
    ...    --removekeywords name:Thisshouldbe*
    ...    --removekeywords name:Remove???
    ...    --removekeywords tag:removeANDkitty
    ...    --log log.html
    Run tests    ${opts}    cli/remove_keywords/all_combinations.robot
    ${log} =    Get file    ${OUTDIR}/log.html
    VAR    ${LOG}    ${log}    scope=SUITE

Log should not contain
    [Arguments]    ${msg}
    Should not contain    ${LOG}    ${msg}

Log should contain
    [Arguments]    ${msg}
    Should contain    ${LOG}    ${msg}

Output should contain pass message
    ${tc} =   Check test case    Passing
    Check Log Message    ${tc[0, 0]}    ${PASS MESSAGE}

Output should contain fail message
    ${tc} =   Check test case    Failing
    Check Log Message    ${tc[0, 0]}    ${FAIL MESSAGE}

Output should contain for messages
    Test should contain for messages    FOR when test passes
    Test should contain for messages    FOR when test fails

Test should contain for messages
    [Arguments]    ${name}
    ${tc} =    Check test case    ${name}
    Check log message    ${tc[0, 0, 0, 0, 1, 0, 0]}    ${REMOVED FOR MESSAGE} one
    Check log message    ${tc[0, 0, 1, 0, 1, 0, 0]}    ${REMOVED FOR MESSAGE} two
    Check log message    ${tc[0, 0, 2, 0, 1, 0, 0]}    ${REMOVED FOR MESSAGE} three
    Check log message    ${tc[0, 0, 3, 0, 0, 0, 0]}    ${KEPT FOR MESSAGE} LAST

Output should contain while messages
    Test should contain while messages    WHILE when test passes
    Test should contain while messages    WHILE when test fails

Test should contain while messages
    [Arguments]    ${name}
    ${tc} =    Check test case    ${name}
    Check log message    ${tc[0, 1, 0, 0, 1, 0, 0]}    ${REMOVED WHILE MESSAGE} 1
    Check log message    ${tc[0, 1, 1, 0, 1, 0, 0]}    ${REMOVED WHILE MESSAGE} 2
    Check log message    ${tc[0, 1, 2, 0, 1, 0, 0]}    ${REMOVED WHILE MESSAGE} 3
    Check log message    ${tc[0, 1, 3, 0, 0, 0, 0]}    ${KEPT WHILE MESSAGE} 4

Output should contain WUKS messages
    Test should contain WUKS messages    WUKS when test passes
    Test should contain WUKS messages    WUKS when test fails

Test should contain WUKS messages
    [Arguments]    ${name}
    ${tc} =    Check test case    ${name}
    Check log message    ${tc[0, 0, 1, 0, 0]}   ${REMOVED WUKS MESSAGE}    FAIL
    Check log message    ${tc[0, 8, 1, 0, 0]}   ${REMOVED WUKS MESSAGE}    FAIL
    Check log message    ${tc[0, 9, 2, 0, 0]}   ${KEPT WUKS MESSAGE}       FAIL

Output should contain NAME messages
    Test should contain NAME messages    NAME when test passes
    Test should contain NAME messages    NAME when test fails

Test should contain NAME messages
    [Arguments]    ${name}
    ${tc}=    Check test case    ${name}
    Check log message    ${tc[0, 0, 0]}       ${REMOVED BY NAME MESSAGE}
    Check log message    ${tc[1, 0, 0]}       ${REMOVED BY NAME MESSAGE}
    Check log message    ${tc[2, 0, 0, 0]}    ${REMOVED BY NAME MESSAGE}
    Check log message    ${tc[2, 1, 0]}       ${KEPT BY NAME MESSAGE}

Output should contain NAME messages with patterns
    Test should contain NAME messages with * pattern    NAME with * pattern when test passes
    Test should contain NAME messages with * pattern    NAME with * pattern when test fails
    Test should contain NAME messages with ? pattern    NAME with ? pattern when test passes
    Test should contain NAME messages with ? pattern    NAME with ? pattern when test fails

Test should contain NAME messages with * pattern
    [Arguments]    ${name}
    ${tc}=    Check test case    ${name}
    Check log message    ${tc[0, 0, 0]}       ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc[1, 0, 0]}       ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc[2, 0, 0]}       ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc[3, 0, 0, 0]}    ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc[3, 1, 0]}       ${KEPT BY PATTERN MESSAGE}

Test should contain NAME messages with ? pattern
    [Arguments]    ${name}
    ${tc}=    Check test case    ${name}
    Check log message    ${tc[0, 0, 0]}       ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc[1, 0, 0, 0]}    ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc[1, 1, 0]}       ${KEPT BY PATTERN MESSAGE}

Output should contain warning and error
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0, 0]}    Keywords with warnings are not removed    WARN
    Check Log Message    ${tc[1, 0, 0]}       Keywords with errors are not removed      ERROR
