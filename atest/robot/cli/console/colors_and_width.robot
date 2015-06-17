*** Settings ***
Documentation     On Windows colors are never actually written to output.
...               Testing colors thus really works only on other platforms
Force Tags        regression    pybot    jybot
Resource          console_resource.robot

*** Test Cases ***
Console Colors Auto
    Run Tests With Colors    --consolecolors auto
    Outputs should not have ANSI colors

Console Colors Off
    Run Tests With Colors    --consolecolors OFF
    Outputs should not have ANSI colors

Console Colors On
    Run Tests With Colors    --ConsoleCol on
    Outputs should have ANSI colors when not on Windows

Console Colors ANSI
    Run Tests With Colors    --ConsoleColors AnSi
    Outputs should have ANSI colors

Invalid Console Colors
    Run Tests Without Processing Output    -C InVaLid    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Invalid console color value 'InVaLid'. Available 'AUTO', 'ON', 'OFF' and 'ANSI'.${USAGE TIP}\n

Console Width
    ${name} =    Evaluate    'Start-' + '0123456789' * 9 + '-end'
    Run Tests    --consolewidth 105 --name ${name} --doc x    misc/pass_and_fail.robot
    Check Stdout Contains    ${SEP_CHAR1 * 105}\n ${name} :: x\n ${SEP_CHAR1 * 105}\n
    Check Stdout Contains    ${SEP_CHAR2 * 105}\n ${name[:-7]}... | FAIL |\n ${MSG_211}\n ${SEP_CHAR1 * 105}\n
    ${statuts} =    Create Status Line    Pass    93    PASS
    Check Stdout Contains    ${SEP_CHAR1 * 105}\n ${statuts}\n ${SEP_CHAR2 * 105}\n
    ${statuts} =    Create Status Line    Fail :: FAIL Expected failure    68    FAIL
    Check Stdout Contains    ${SEP_CHAR2 * 105}\n ${statuts}\n Expected failure\n ${SEP_CHAR2 * 105}\n
    Run Tests    -W 20 --name ${name}    misc/pass_and_fail.robot
    Check Stdout Contains    ${SEP_CHAR1 * 20}\n Start-01234567890...\n ${SEP_CHAR1 * 20}\n
    Check Stdout Contains    ${SEP_CHAR2 * 20}\n Start-01... | FAIL |\n ${MSG_211}\n ${SEP_CHAR1 * 20}\n
    Check Stdout Contains    ${SEP_CHAR1 * 20}\n Pass${SPACE * 8}| PASS |\n ${SEP_CHAR2 * 20}\n
    Check Stdout Contains    ${SEP_CHAR2 * 20}\n Fail :: ... | FAIL |\n Expected failure\n ${SEP_CHAR2 * 20}\n

Invalid Width
    Run Tests Without Processing Output    -W InVaLid    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Option '--consolewidth' expected integer value but got 'InVaLid'.${USAGE TIP}\n

*** Keywords ***
Run Tests With Colors
    [Arguments]    ${colors}
    Run Tests    ${colors} --variable LEVEL1:WARN    misc/pass_and_fail.robot

Outputs should not have ANSI colors
    Check Stdout Contains    | PASS |
    Check Stdout Contains    | FAIL |
    Check Stderr Contains    [ WARN ]

Outputs should have ANSI colors when not on Windows
    Run Keyword If    os.sep == '/'    Outputs should have ANSI colors
    Run Keyword Unless    os.sep == '/'    Outputs should not have ANSI colors

Outputs should have ANSI colors
    Check Stdout Does Not Contain    | PASS |
    Check Stdout Does Not Contain    | FAIL |
    Check Stderr Does Not Contain    [ WARN ]
    Check Stdout Contains    PASS
    Check Stdout Contains    FAIL
    Check Stderr Contains    WARN
