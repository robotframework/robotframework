*** Settings ***
Library         Dialogs
Library         Collections

*** Variable ***
${FILLER} =     Wräp < & シ${SPACE}

*** Test Cases ***
Pause Execution
    Pause Execution    Press OK.

Pause Execution With Long Line
    Pause Execution    Verify that the long text below is wrapped nicely.\n\n${FILLER*200}\n\nAnd then press OK.

Pause Execution With Multiple Lines
    Pause Execution    Verify that\nthis multi\nline text\nis displayed\nnicely.\n\nʕ•ᴥ•ʔ\n\nAnd then press <Esc>.

Execute Manual Step Passing
    Execute Manual Step    Press PASS.

Execute Manual Step Failing
    [Documentation]  FAIL Predefined error message
    Execute Manual Step    Press FAIL and then OK on next dialog.    Predefined error message

Execute Manual Step Exit
    [Documentation]  FAIL No value provided by user.
    Execute Manual Step    Press <Esc>.    This should not be shown!!

Get Value From User
    ${value} =    Get Value From User    Type 'value' and press OK.    Overwrite me
    Should Be Equal    ${value}    value

Get Non-ASCII Value From User
    ${value} =    Get Value From User    Press OK.    ʕ•ᴥ•ʔ
    Should Be Equal    ${value}    ʕ•ᴥ•ʔ

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
    Get Value From User
    ...    Press Cancel.\n\nAlso verify that the default value below is not hidded.
    ...    Default value.    hidden=no

Get Value From User Exited
    [Documentation]  FAIL No value provided by user.
    Get Value From User
    ...    Press <Esc>.\n\nAlso verify that the long text below is wrapped nicely.\n\n${FILLER*200}

Get Selection From User
    ${value} =    Get Selection From User
    ...    Select 'valuë' and press OK.\n\nAlso verify that the dialog is resized properly.
    ...    zip    zap    v v v    valuë    ^ ^ ^    ʕ•ᴥ•ʔ
    ...    This is a really long string and the window should change the size properly to content.
    Should Be Equal    ${value}    valuë

Get Selection From User Cancelled
    [Documentation]  FAIL No value provided by user.
    Get Selection From User    Press Cancel.    zip    zap    foo

Get Selection From User Exited
    [Documentation]  FAIL No value provided by user.
    Get Selection From User
    ...    Press <Esc>.\n\nAlso verify that the long text below is wrapped nicely.\n\n${FILLER*200}
    ...    zip    zap    foo

Get Selections From User
    ${values}=    Get Selections From User
    ...    Select 'FOO', 'BAR' & 'ZÄP' and press OK.\n\nAlso verify that the dialog is resized properly.
    ...    1    FOO    3    ʕ•ᴥ•ʔ    BAR    6    ZÄP    7
    ...    This is a really long string and the window should change the size properly to content.
    ...    9    10    11    12    13    14    15    16    17    18    19    20
    Should Be True    type($values) is list
    ${expected values}=    Create List    FOO    BAR    ZÄP
    Lists Should Be Equal    ${values}    ${expected values}

Get Selections From User When No Input Provided
    ${values}=    Get Selections From User
    ...    Press OK.
    ...    value 1    value 2    value 3    value 4
    Should Be True    type($values) is list
    ${expected values}=    Create List
    Lists Should Be Equal    ${values}    ${expected values}

Get Selections From User Cancelled
    [Documentation]  FAIL No value provided by user.
    Get Selections From User
    ...    Press Cancel.
    ...    value 1    value 2    value 3    value 4

Get Selections From User Exited
    [Documentation]  FAIL No value provided by user.
    Get Selections From User
    ...    Press <Esc>.\n\nAlso verify that the long text below is wrapped nicely.\n\n${FILLER*200}
    ...    value 1    value 2    value 3    value 4

Multiple dialogs in a row
    [Documentation]  FAIL No value provided by user.
    Pause Execution    Verify that dialog is closed immediately.\n\nAfter pressing OK.
    Sleep    0.5s
    Get Value From User    Verify that dialog is closed immediately.\n\nAfter pressing Cancel.
