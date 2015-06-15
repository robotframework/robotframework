*** Settings ***
Suite Setup      Run Tests And Remove Keywords
Default Tags    regression  pybot  jybot
Resource        atest_resource.robot

*** Variables ***
${PASS MESSAGE}    -PASSED -ALL
${FAIL MESSAGE}    -ALL +PASSED
${REMOVED FOR MESSAGE}     -FOR -ALL
${KEPT FOR MESSAGE}        +FOR -ALL
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
    Log should contain    ${FAIL MESSAGE}
    Output should contain fail message

FOR option
    Log should not contain    ${REMOVED FOR MESSAGE}
    Log should contain    ${KEPT FOR MESSAGE}
    Output should contain for messages

WUKS option
    Log should not contain    ${REMOVED WUKS MESSAGE}
    Log should contain    ${KEPT WUKS MESSAGE}
    Output should contain WUKS messages

NAME option
    Log should not contain    ${REMOVED BY NAME MESSAGE}
    Log should contain    ${KEPT BY NAME MESSAGE}
    Output should contain NAME messages

NAME option with pattern
    Log should not contain    ${REMOVED BY PATTERN MESSAGE}
    Log should contain    ${KEPT BY PATTERN MESSAGE}
    Output should contain NAME messages with patterns

TAGged keywords
    Log should contain     This is not removed by TAG
    Log should not contain    This is removed by TAG

Warnings and errors are preserved
    Output should contain warning and error
    Log should contain    Keywords with warnings are not removed
    Log should contain    Keywords with errors are not removed

*** Keywords ***
Run tests and remove keywords
    ${opts} =    Catenate
    ...    --removekeywords passed
    ...    --RemoveKeywords FoR
    ...    --removek WUKS
    ...    --removekeywords name:RemoveByName
    ...    --removekeywords name:Thisshouldbe*
    ...    --removekeywords name:Remove???
    ...    --removekeywords tag:removeANDkitty
    ...    --log log.html
    Run tests    ${opts}    cli/remove_keywords/all_combinations.robot
    ${LOG} =    Get file    ${OUTDIR}/log.html
    Set suite variable    $LOG

Log should not contain
    [Arguments]    ${msg}
    Should not contain    ${LOG}    ${msg}

Log should contain
    [Arguments]    ${msg}
    Should contain    ${LOG}    ${msg}

Output should contain pass message
    ${tc} =   Check test case    Passing
    Check Log Message    ${tc.kws[0].msgs[0]}    ${PASS MESSAGE}

Output should contain fail message
    ${tc} =   Check test case    Failing
    Check Log Message    ${tc.kws[0].msgs[0]}    ${FAIL MESSAGE}

Output should contain for messages
    Test should contain for messages    For when test passes
    Test should contain for messages    For when test fails

Test should contain for messages
    [Arguments]    ${name}
    ${tc} =    Check test case    ${name}
    ${for} =    Set Variable    ${tc.kws[0].kws[0]}
    Check log message    ${for.kws[0].kws[0].kws[0].msgs[0]}    ${REMOVED FOR MESSAGE} one
    Check log message    ${for.kws[1].kws[0].kws[0].msgs[0]}    ${REMOVED FOR MESSAGE} two
    Check log message    ${for.kws[2].kws[0].kws[0].msgs[0]}    ${REMOVED FOR MESSAGE} three
    Check log message    ${for.kws[3].kws[0].kws[0].msgs[0]}    ${KEPT FOR MESSAGE} LAST

Output should contain WUKS messages
    Test should contain WUKS messages    WUKS when test passes
    Test should contain WUKS messages    WUKS when test fails

Test should contain WUKS messages
    [Arguments]    ${name}
    ${tc} =    Check test case    ${name}
    Check log message    ${tc.kws[0].kws[0].kws[1].kws[0].msgs[0]}   ${REMOVED WUKS MESSAGE}    FAIL
    Check log message    ${tc.kws[0].kws[8].kws[1].kws[0].msgs[0]}   ${REMOVED WUKS MESSAGE}    FAIL
    Check log message    ${tc.kws[0].kws[9].kws[2].kws[0].msgs[0]}   ${KEPT WUKS MESSAGE}    FAIL

Output should contain NAME messages
    Test should contain NAME messages    NAME when test passes
    Test should contain NAME messages    NAME when test fails

Test should contain NAME messages
    [Arguments]    ${name}
    ${tc}=    Check test case    ${name}
    Check log message    ${tc.kws[0].kws[0].msgs[0]}   ${REMOVED BY NAME MESSAGE}
    Check log message    ${tc.kws[1].kws[0].msgs[0]}   ${REMOVED BY NAME MESSAGE}
    Check log message    ${tc.kws[2].kws[0].kws[0].msgs[0]}   ${REMOVED BY NAME MESSAGE}
    Check log message    ${tc.kws[2].kws[1].msgs[0]}   ${KEPT BY NAME MESSAGE}

Output should contain NAME messages with patterns
    Test should contain NAME messages with * pattern    NAME with * pattern when test passes
    Test should contain NAME messages with * pattern    NAME with * pattern when test fails
    Test should contain NAME messages with ? pattern    NAME with ? pattern when test passes
    Test should contain NAME messages with ? pattern    NAME with ? pattern when test fails

Test should contain NAME messages with * pattern
    [Arguments]    ${name}
    ${tc}=    Check test case    ${name}
    Check log message    ${tc.kws[0].kws[0].msgs[0]}   ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc.kws[1].kws[0].msgs[0]}   ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc.kws[2].kws[0].msgs[0]}   ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc.kws[3].kws[0].kws[0].msgs[0]}    ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc.kws[3].kws[1].msgs[0]}    ${KEPT BY PATTERN MESSAGE}

Test should contain NAME messages with ? pattern
    [Arguments]    ${name}
    ${tc}=    Check test case    ${name}
    Check log message    ${tc.kws[0].kws[0].msgs[0]}    ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc.kws[1].kws[0].kws[0].msgs[0]}    ${REMOVED BY PATTERN MESSAGE}
    Check log message    ${tc.kws[1].kws[1].msgs[0]}    ${KEPT BY PATTERN MESSAGE}

Output should contain warning and error
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}    Keywords with warnings are not removed    WARN
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Keywords with errors are not removed    ERROR
