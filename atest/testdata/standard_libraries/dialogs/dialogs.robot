*** Settings ***
Library           Dialogs
Library           Collections
Test Tags         manual    no-ci

*** Variables ***
${FILLER} =     Wräp < & シ${SPACE}

*** Test Cases ***
Pause Execution
    Pause Execution    Press OK button.
    Pause Execution    Press <Enter> key.
    Pause Execution    Press <o> key.
    Pause Execution    Press <O> key.

Pause Execution With Long Line
    Pause Execution    Verify that the long text below is wrapped nicely.\n\n${FILLER*200}\n\nThen press OK or <Enter>.

Pause Execution With Multiple Lines
    Pause Execution    Verify that\nthis multi\nline text\nis displayed\nnicely.\n\nʕ•ᴥ•ʔ\n\nThen press <Esc>.

Execute Manual Step Passing
    Execute Manual Step    Verify the taskbar icon.\n\nPress PASS if it is ok.    Invalid taskbar icon.
    Execute Manual Step    Press <Enter> and validate that the dialog is *NOT* closed.\n\nThen press <P> or <p>

Execute Manual Step Failing
    [Documentation]  FAIL Predefined error message
    Execute Manual Step    Press FAIL, <F> or <f> and then OK the on next dialog.    Predefined error message

Execute Manual Step Exit
    [Documentation]  FAIL No value provided by user.
    Execute Manual Step    Press <Esc>.    This should not be shown!!

Get Value From User
    ${value} =    Get Value From User    Type 'robot' and press OK.    Overwrite me
    Should Be Equal    ${value}    robot

Get Non-ASCII Value From User
    ${value} =    Get Value From User    Press <Enter>.    ʕ•ᴥ•ʔ
    Should Be Equal    ${value}    ʕ•ᴥ•ʔ

Get Empty Value From User
    ${value} =    Get Value From User    Press OK or <Enter>.
    Should Be Equal    ${value}    ${EMPTY}

Get Hidden Value From User
    ${value} =    Get Value From User    Type 'c' and press OK or <Enter>.    hidden=yes
    Should Be Equal    ${value}    c
    ${value} =    Get Value From User    Press OK or <Enter>.    initial value    hide
    Should Be Equal    ${value}    initial value

Get Value From User Cancelled
    [Documentation]  FAIL No value provided by user.
    Get Value From User
    ...    Press Cancel.\n\nAlso verify that the default value below is not hidden.
    ...    Default value.    hidden=no

Get Value From User Exited
    [Documentation]  FAIL No value provided by user.
    Get Value From User
    ...    Press <Esc>.\n\nAlso verify that the long text below is wrapped nicely.\n\n${FILLER*200}

Get Value From User Shortcuts
    ${value} =    Get Value From User
    ...    1. Type 'oc'.\n2. Press <tab> to move focus.\n3. Press <o> to close the dialog.
    Should Be Equal    ${value}    oc

Get Selection From User
    ${value} =    Get Selection From User
    ...    Select 'valuë' and press OK.\n\nAlso verify that the dialog is resized properly.
    ...    zip    zap    v v v    valuë    ^ ^ ^    ʕ•ᴥ•ʔ
    ...    This is a really long string and the window should change the size properly to content.
    Should Be Equal    ${value}    valuë

Get Selection From User When Default Value Provided by Index
    ${value}=    Get Selection From User
    ...    Press OK or <Enter>.
    ...    value 1    value 2    value 3    value 4
    ...    default=1
    Should Be Equal    ${value}    value 1

Get Selection From User When Default Value Provided by String
    ${value}=    Get Selection From User
    ...    Press OK or <Enter>.
    ...    xxx    yyy    zzz    ååå    äää    ööö
    ...    default=ööö
    Should Be Equal    ${value}    ööö

Get Selection From User When Default Value Is Integer
    ${value}=    Get Selection From User
    ...    Press OK or <Enter>.
    ...    -2    -1    0    1    2
    ...    default=1
    Should Be Equal    ${value}    1

Get Selection From User When Default Value Index Is Out of Bounds
    [Documentation]    FAIL ValueError: Default value index is out of bounds.
    Get Selection From User
    ...    Press OK or <Enter>.
    ...    value 1    value 2    value 3    value 4
    ...    default=5

Get Selection From User When Default Value Cannot Be Found
    [Documentation]  FAIL ValueError: Invalid default value 'asd'.
    Get Selection From User
    ...    Press OK or <Enter>.
    ...    value 1    value 2    value 3    value 4
    ...    default=asd

Get Selection From User Cancelled
    [Documentation]  FAIL No value provided by user.
    Get Selection From User    Press <C> or <c>.    zip    zap    foo

Get Selection From User Exited
    [Documentation]  FAIL No value provided by user.
    Get Selection From User
    ...    Press <Esc>.\n\nAlso verify that the long text below is wrapped nicely.\n\n${FILLER*200}
    ...    zip    zap    foo

Get Selections From User
    ${values}=    Get Selections From User
    ...    Select 'FOO', 'BAR' & 'ZÄP' and press <Enter>.\n\nAlso verify that the dialog is resized properly.
    ...    1    FOO    3    ʕ•ᴥ•ʔ    BAR    6    ZÄP    7
    ...    This is a rather long value and the dialog size should be set so that it fits.
    ...    9    10    11    12    13    14    15    16    17    18    19    20
    Should Be True    type($values) is list
    ${expected values}=    Create List    FOO    BAR    ZÄP
    Lists Should Be Equal    ${values}    ${expected values}

Get Selections From User When No Input Provided
    ${values}=    Get Selections From User
    ...    Press OK or <Enter>.
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
    Pause Execution    Press OK or <Enter> and verify that dialog is closed immediately.\n\nNext dialog is opened after 1 second.
    Sleep    1 second
    Get Value From User    Press Cancel or <Esc> and verify that dialog is closed immediately.

Garbage Collection In Thread Should Not Cause Problems
    ${thread}=    Evaluate    threading.Thread(target=gc.collect)
    Pause Execution    Press OK or <Enter> and verify that execution does not crash.
    Call Method    ${thread}    start
    Call Method    ${thread}    join

Timeout can close dialog
    [Documentation]    FAIL Test timeout 1 second exceeded.
    [Timeout]    1 second
    Pause Execution    Wait for timeout.
