*** Settings ***
Documentation     Non-interactive acceptance tests for the `Debug` keyword.
...               The real Tk dialog is replaced with a scripted fake by
...               `FakeDebuggerDialog` so these can run unattended on CI.
Library           Dialogs
Library           FakeDebuggerDialog
Suite Teardown    Reset Debugger

*** Test Cases ***
Continue resumes immediately
    Script Debugger Actions    CONTINUE
    Debug    Continue test
    Log    after debug
    Debugger Open Count Should Be    1

Step In stops on the very next body item
    Script Debugger Actions    STEP_IN    CONTINUE
    Debug    Step in test
    Log    next sibling 1
    Log    next sibling 2
    Debugger Open Count Should Be    2

Step Over skips nested user keyword body
    Script Debugger Actions    STEP_OVER    CONTINUE
    Debug    Step over test
    Nested User Keyword
    Log    after nested
    Debugger Open Count Should Be    2

Step Out runs to the caller
    Script Debugger Actions    STEP_OUT    CONTINUE
    Run Inner With Debug
    Log    after caller
    Debugger Open Count Should Be    2

Multiple Debug calls each open the dialog
    Script Debugger Actions    CONTINUE    CONTINUE    CONTINUE
    Debug    First
    Debug    Second
    Debug    Third
    Debugger Open Count Should Be    3

Abort ends the run
    [Documentation]    FAIL    Test execution aborted from debugger.
    Script Debugger Actions    ABORT
    Debug    Abort here
    Log    should not be reached

*** Keywords ***
Nested User Keyword
    Log    inside nested 1
    Log    inside nested 2

Run Inner With Debug
    Debug    Inside inner
    Log    inner step after debug
