*** Settings ***
Documentation     On Windows colors are never actually written to output.
...               Testing colors thus really works only on other platforms
Resource          console_resource.robot

*** Test Cases ***
Console Colors Auto
    Run Tests With Warnings    --consolecolors auto
    Outputs should not have ANSI codes

Console Colors Off
    Run Tests With Warnings    --consolecolors OFF
    Outputs should not have ANSI codes

Console Colors On
    Run Tests With Warnings    --ConsoleCol on
    Outputs should have ANSI colors when not on Windows

Console Colors ANSI
    Run Tests With Warnings    --Console-Colors AnSi
    Outputs should have ANSI codes

Invalid Console Colors
    Run Tests Without Processing Output    -C InVaLid    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Invalid console color value 'InVaLid'. Available 'AUTO', 'ON', 'OFF' and 'ANSI'.${USAGE TIP}\n

Console Width
    ${name} =    Evaluate    'Start-' + '0123456789' * 9 + '-end'
    Run Tests    --consolewidth 105 --name ${name} --doc x    misc/pass_and_fail.robot
    Stdout Should Contain    ${SEP_CHAR1 * 105}\n${name} :: x\n${SEP_CHAR1 * 105}\n
    Stdout Should Contain    ${SEP_CHAR2 * 105}\n${name[:-7]}... | FAIL |\n${MSG_211}\n${SEP_CHAR1 * 105}\n
    ${statuts} =    Create Status Line    Pass    93    PASS
    Stdout Should Contain    ${SEP_CHAR1 * 105}\n${statuts}\n${SEP_CHAR2 * 105}\n
    ${statuts} =    Create Status Line    Fail :: FAIL Expected failure    68    FAIL
    Stdout Should Contain    ${SEP_CHAR2 * 105}\n${statuts}\nExpected failure\n${SEP_CHAR2 * 105}\n
    Run Tests    -W 20 --name ${name}    misc/pass_and_fail.robot
    Stdout Should Contain    ${SEP_CHAR1 * 20}\nStart-01234567890...\n${SEP_CHAR1 * 20}\n
    Stdout Should Contain    ${SEP_CHAR2 * 20}\nStart-01... | FAIL |\n${MSG_211}\n${SEP_CHAR1 * 20}\n
    Stdout Should Contain    ${SEP_CHAR1 * 20}\nPass${SPACE * 8}| PASS |\n${SEP_CHAR2 * 20}\n
    Stdout Should Contain    ${SEP_CHAR2 * 20}\nFail :: ... | FAIL |\nExpected failure\n${SEP_CHAR2 * 20}\n

Invalid Width
    Run Tests Without Processing Output    -W InVaLid    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Invalid value for option '--consolewidth': Expected integer, got 'InVaLid'.${USAGE TIP}\n

Console links off
    [Documentation]    Console links being enabled is tested as part of testing console colors.
    Run Tests With Warnings    --console-links oFF --console-colors on
    Outputs should have ANSI colors when not on Windows    links=False

Invalid link config
    Run Tests Without Processing Output    --ConsoleLinks InVaLid    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Invalid console link value 'InVaLid. Available 'AUTO' and 'OFF'.${USAGE TIP}\n

*** Keywords ***
Run Tests With Warnings
    [Arguments]    ${options}
    Run Tests    ${options} --variable LEVEL1:WARN    misc/pass_and_fail.robot

Outputs should not have ANSI codes
    Stdout Should Contain    | PASS |
    Stdout Should Contain    | FAIL |
    Stderr Should Contain    [ WARN ]

Outputs should have ANSI colors when not on Windows
    [Arguments]    ${links}=True
    IF    os.sep == '/'
        Outputs should have ANSI codes    ${links}
    ELSE
       Outputs should not have ANSI codes
    END

Outputs should have ANSI codes
    [Arguments]    ${links}=True
    Stdout Should Not Contain    | PASS |
    Stdout Should Not Contain    | FAIL |
    Stderr Should Not Contain    [ WARN ]
    Stdout Should Contain    | \x1b[32mPASS\x1b[0m |
    Stdout Should Contain    | \x1b[31mFAIL\x1b[0m |
    Stderr Should Contain    [ \x1b[33mWARN\x1b[0m ]
    IF    ${links}
        Stdout Should Contain    \x1b]8;;file://
    ELSE
        Stdout Should Not Contain    \x1b]8;;file://
    END
