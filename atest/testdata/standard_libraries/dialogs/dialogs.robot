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
    Pause Execution    Press <O> key.
    Pause Execution    Press <o> key.

Pause Execution With Long Line
    Pause Execution    Verify that the long text below is wrapped nicely.\n\n${FILLER*200}\n\nThen press OK or <Enter>.

Pause Execution With Multiple Lines
    Pause Execution    Verify that\nthis multi\nline text\nis displayed\nnicely.\n\nʕ•ᴥ•ʔ\n\nThen press <Esc>.

Execute Manual Step Passing
    Execute Manual Step    Press PASS.
    Execute Manual Step    Press <Enter> and validate that the dialog is *NOT* closed.\n\nThen press PASS.
    Execute Manual Step    Press <P> or <p>.    This should not be shown!!

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
    ...    Press Cancel.\n\nAlso verify that the default value below is not hidded.
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
    Pause Execution    Verify that dialog is closed immediately.\n\nAfter pressing OK or <Enter>.
    Get Value From User    Verify that dialog is closed immediately.\n\nAfter pressing Cancel or <Esc>.

Garbage Collection In Thread Should Not Cause Problems
    ${thread}=    Evaluate    threading.Thread(target=gc.collect)    modules=gc,threading
    Pause Execution    Verify that the execution does not crash after pressing OK or <Enter>.
    Call Method    ${thread}    start
    Call Method    ${thread}    join
