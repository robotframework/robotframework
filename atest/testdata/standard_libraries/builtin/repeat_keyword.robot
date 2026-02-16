*** Variables ***
${COUNT}             0
${NORMAL FAIL}       no
${PASS EXECUTION}    no

*** Test Cases ***
Times As String
    Repeat Keyword    2    Log    Hello, repeating world!

Times As Integer
    Repeat Keyword    ${42}    Log    This works too!!

Times With 'times' Postfix
    Repeat Keyword    3 times    Log    This is done 3 times
    Repeat Keyword    2TimeS    Log    Case and space insensitive

Times With 'x' Postfix
    Repeat Keyword    10 x    Log    Close to old repeating syntax
    Repeat Keyword    ${1}X    Log    Case and space

Zero And Negative Times
    Repeat Keyword    0 times    This is not executed
    Repeat Keyword    ${-1}    ${nonex}    ${nonex}
    Repeat Keyword    0 secs    This is not executed

Invalid Times 1
    [Documentation]    FAIL STARTS: ValueError: '1.3' cannot be converted to an integer:
    Repeat Keyword    ${1.3}    Log    Not an integer

Invalid Times 2
    [Documentation]    FAIL STARTS: ValueError: 'notaninteger' cannot be converted to an integer:
    Repeat Keyword    Not an integer    No Operation

Repeat Keyword With Time String
    Repeat Keyword    00:00:00.003      Log    This is done for 00:00:00.003
    Repeat Keyword    3 milliseconds    Log    This is done for 3 milliseconds
    Repeat Keyword    3ms               Log    This is done for 3ms

Repeat Keyword With `timedelta`
    Repeat Keyword    ${{datetime.timedelta(milliseconds=3)}}
    ...                                 Log    This is done for `timedelta(milliseconds=3)`

Repeat Keyword Arguments As Variables
    VAR    ${kw}    Should Be Equal
    Repeat Keyword    2 times    ${kw}    @{{['Hello, world!']}}    ${{'Hello, world!'}}

    VAR    ${escaped}    \\ and \${notvar}
    Repeat Keyword    42 times    ${kw}    ${escaped}    \\ and \${notvar}

    VAR    @{times_and_kw}    10 times    No Operation
    Repeat Keyword    @{times_and_kw}

    VAR    @{escaped}    ${kw}    ${escaped}    \\ and \${notvar}
    Repeat Keyword    1x    @{escaped}

Repeated Keyword As Non-existing Variable
    [Documentation]    FAIL Variable '\${non existing}' not found.
    Repeat Keyword    1 x    ${non existing}

Argument To Repeated Keyword As Non-existing Variable
    [Documentation]    FAIL Variable '\${nonexisting}' not found.
    Repeat Keyword    1 x    Log    ${nonexisting}

Repeated Keyword Failing Immediately
    [Documentation]    FAIL Immediate failure
    Repeat Keyword    1000 times    Fail    Immediate failure

Repeated Keyword Failing On Third Round
    [Documentation]    FAIL '3 < 3' should be true.
    Repeat Keyword    1000 times    Keyword Failing On Third Run

Repeat Keyword With Continuable Failure
    [Documentation]    FAIL Several failures occurred:\n\n1) XXX\n\n2) XXX\n\n3) XXX
    Repeat Keyword    3x    Run Keyword And Continue On Failure    Fail    XXX

Repeat Keyword With Failure After Continuable Failure
    [Documentation]    FAIL Several failures occurred:\n\n1) Continuable\n\n2) Normal

    Repeat Keyword    3x    First Continuable Failure And Then Normal Failure

Repeat Keyword With Pass Execution
    [Documentation]    PASS Message
    Repeat Keyword    3x    Pass Execution    Message

Repeat Keyword With Pass Execution After Continuable Failure
    [Documentation]    FAIL Continuable
    Repeat Keyword    3x    First Continuable Failure And Then Pass Execution

*** Keywords ***
Keyword Failing On Third Run
    ${COUNT} =    Evaluate    ${COUNT} + 1
    Should Be True    ${COUNT} < 3
    Set Suite Variable    ${COUNT}

First Continuable Failure And Then Normal Failure
    Should Be True    "${NORMAL FAIL}" == "no"    Normal
    Set Suite Variable    ${NORMAL FAIL}    yes
    Run Keyword And Continue On Failure    Fail    Continuable

First Continuable Failure And Then Pass Execution
    Pass Execution If    "${PASS EXECUTION}" == "yes"    Message
    Set Suite Variable    ${PASS EXECUTION}    yes
    Run Keyword And Continue On Failure    Fail    Continuable
