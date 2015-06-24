*** Settings ***
Library         Dialogs

*** Variable ***
${FILLER} =     wrapped${SPACE}


*** Test Cases ***
Pause Execution
    Pause Execution    Press OK.

Pause Execution With Long Line
    Pause Execution    Verify that the long text below is wrapped nicely.\n\n${FILLER*200}\n\nAnd then press OK.

Pause Execution With Multiple Lines
    Pause Execution    Verify that\nthis multi\nline text\nis displayed\nnicely.\n\nAnd then press OK.

Execute Manual Step Passing
    Execute Manual Step    Press PASS.

Execute Manual Step Failing
    [Documentation]  FAIL Predefined error message
    Execute Manual Step    Press FAIL and then OK on next dialog.    Predefined error message

Get Value From User
    ${value} =    Get Value From User  Type 'value' and press OK.    Overwrite me
    Should Be Equal    ${value}    value

Get Empty Value From User
    ${value} =    Get Value From User    Press OK.
    Should Be Equal    ${value}    ${EMPTY}

Get Hidden Value From User
    ${value} =    Get Value From User    Type 'value' and press OK.    hidden=yes
    Should Be Equal    ${value}    value
    ${value} =    Get Value From User    Press OK.    initial value    hide
    Should Be Equal    ${value}    initial value

Get Value From User Cancelled
    [Documentation]  FAIL No value provided by user.
    Get Value From User    Press Cancel.\n\nAlso verify that the default value below is not hidded.
    ...    Default value.    hidden=no

Get Value From User Exited
    [Documentation]  FAIL No value provided by user.
    Get Value From User    Press <Esc>.

Get Selection From User
    ${value} =    Get Selection From User    Select 'value' and press OK.
    ...    zip    zap    foo    value    bar
    Should Be Equal    ${value}    value

Get Selection From User Cancelled
    [Documentation]  FAIL No value provided by user.
    Get Selection From User    Press Cancel.    zip    zap    foo

Get Selection From User Exited
    [Documentation]  FAIL No value provided by user.
    Get Selection From User    Press <Esc>.    zip    zap    foo

Multiple dialogs in a row
    [Documentation]  FAIL No value provided by user.
    Pause Execution    Verify that dialog is closed immediately.\n\nAfter pressing Ok.
    Sleep    1s
    Get Value From User    Verify that dialog is closed immediately.\n\nAfter pressing Cancel.
    [Teardown]    Sleep    1s

Dialog and timeout
    [Timeout]  1s
    [Tags]     jybot_only
    Execute Manual Step    Wait for timeout
