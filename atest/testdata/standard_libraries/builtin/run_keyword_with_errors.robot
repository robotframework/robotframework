*** Settings ***
Library           OperatingSystem

*** Variables ***
@{NEEDS ESCAPING}    c:\\temp\\foo\\not_new_line    \${notvar}
${MESSAGE}           My message
${ERROR MESSAGE}     My error message
${FAIL KW}           Fail

*** Test Cases ***
Ignore Error When Keyword Passes
    Run Keyword And Ignore Error    Log    ${MESSAGE}

Ignore Error When Keyword Fails
    Run Keyword And Ignore Error    Fail    ${ERROR MESSAGE}

Ignore Error Returns When Keyword Passes
    ${status}    ${ret val} =    Run Keyword And Ignore Error    Evaluate    1+2
    Should Be Equal    ${status}    PASS
    Should Be Equal    ${ret val}    ${3}

Ignore Error Returns When Keyword Fails
    ${status}    ${ret val} =    Run Keyword And Ignore Error    ${FAIL KW}    ${ERROR MESSAGE}
    Should Be Equal    ${status}    FAIL
    Should Be Equal    ${ret val}    My error message

Ignore Error With User Keyword When Keywords Pass
    ${status}    ${ret val} =    Run Keyword And Ignore Error    Passing UK
    Should Be Equal    ${status}    PASS
    Should Be Equal    ${ret val}    ${3}

Ignore Error With User Keyword When Keyword Fails
    ${status}    ${ret val} =    Run Keyword And Ignore Error    Failing Uk
    Should Be Equal    ${status}    FAIL
    Should Be Equal    ${ret val}    Expected failure in UK

Ignore Error With Arguments That Needs To Be Escaped
    ${status}    ${ret val} =    Run Keyword And Ignore Error    Directory Should Exist    ${CURDIR}
    Should Be Equal    ${status}    PASS
    Should Be Equal    ${ret val}    ${None}
    ${status}    ${ret val} =    Run Keyword And Ignore Error    Create List    @{NEEDS ESCAPING}
    Should Be Equal    ${status}    PASS
    Should Be True    ${ret val} == @{NEEDS ESCAPING}

Ignore Error When Timeout Occurs
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    Run Keyword And Ignore Error    Sleep    1 hour

Ignore Error When Timeout Occurs In UK
    [Documentation]    FAIL Keyword timeout 100 milliseconds exceeded.
    Run Keyword And Ignore Error    Timeouting UK

Ignore Error When Syntax Error At Parsing Time
    [Documentation]    FAIL Keyword name cannot be empty.
    Run Keyword And Ignore Error    Broken User Keyword

Ignore Error When Syntax Error At Run Time
    [Documentation]    FAIL Keyword 'BuiltIn.No Operation' expected 0 arguments, got 4.
    Run Keyword And Ignore Error    No Operation    wrong    number    of    arguments

Ignore Error When Syntax Error In Setting Variables
    [Documentation]    FAIL Cannot set variable '\@{incompatible}': Expected list-like value, got string.
    Run Keyword And Ignore Error    Invalid Syntax When Setting Variable

Ignore Error When Syntax Error In For Loop
    [Documentation]    FAIL  Variable '\${nonexisting}' not found.
    Run Keyword And Ignore Error    For Loop With Syntax Error

Ignore Error When Access To Nonexisting Variable
    Run Keyword And Ignore Error   Access To Nonexisting Variable

Ignore Error When Access To List Variable Nonexisting Index Syntax 1
    Run Keyword And Ignore Error   Access To List Variable Nonexisting Index Syntax 1

Ignore Error When Access To List Variable Nonexisting Index Syntax 2
    Run Keyword And Ignore Error   Access To List Variable Nonexisting Index Syntax 2

Ignore Error When Access To Dictionary Nonexisting Key Syntax 1
    Run Keyword And Ignore Error   Access To Dictionary Variable Nonexisting Key Syntax 1

Ignore Error When Access To Dictionary Nonexisting Key Syntax 2
    Run Keyword And Ignore Error   Access To Dictionary Variable Nonexisting Key Syntax 2

Expect Error When Error Occurs
    Run Keyword And Expect Error    ${ERROR MESSAGE}    ${FAIL KW}    ${ERROR MESSAGE}

Expect Error When Different Error Occurs
    [Documentation]    FAIL Expected error 'My error' but got 'My error message'.
    Run Keyword And Expect Error    My error    Fail    ${ERROR MESSAGE}
    Fail    This should not be executed

Expect Error When Different Error Occurs 2
    [Documentation]    FAIL REGEXP:Expected error 'My error' but got 'Evaluating expression 'foo == bar' failed: NameError: (name 'foo' is not defined|foo)'.
    Run Keyword And Expect Error    My error    Evaluate    foo == bar
    Fail    This should not be executed

Expect Error When No Errors Occur
    [Documentation]    FAIL Expected error 'My error message' did not occur.
    Run Keyword And Expect Error    My error message    Log    My message
    Fail    This should not be executed

Expected Error Is Pattern
    Run Keyword And Expect Error    *    Fail    Critical error
    Run Keyword And Expect Error    C*a? e*rro?    Fail    Critical error

Expected Error Is Multiline
    Run Keyword And Expect Error    My error message\nIn multiple\nLines    Fail    My error message\nIn multiple\nLines
    Run Keyword And Expect Error    My error message*Lines    Fail    My error message\nIn multiple\nLines

Expected Error Should Be Returned
    ${error} =    Run Keyword And Expect Error    *    Fail    Critical error
    Should Be Equal    ${error}    Critical error

Expect Error With User Keyword When Keywords Pass
    [Documentation]    FAIL Expected error 'My error' did not occur.
    Run Keyword And Expect Error    My error    Passing UK

Expect Error With User Keyword When Keyword Fails
    Run Keyword And Expect Error    Expected failure in UK    Failing Uk

Expect Error With Arguments That Needs To Be Escaped
    [Documentation]    FAIL Expected error 'There are no errors' did not occur.
    Run Keyword And Expect Error    Directory '%{TEMPDIR}' exists.    Directory Should Not Exist    %{TEMPDIR}
    Run Keyword And Expect Error    There are no errors    Log Many    @{NEEDS ESCAPING}

Expect Error When Timeout Occurs
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    Run Keyword And Expect Error    *    Sleep    1 hour

Expect Error When Timeout Occurs In UK
    [Documentation]    FAIL Keyword timeout 100 milliseconds exceeded.
    Run Keyword And Expect Error    *    Timeouting UK

Expect Error When Syntax Error At Parsing Time
    [Documentation]    FAIL Keyword name cannot be empty.
    Run Keyword And Expect Error    *    Broken User Keyword

Expect Error When Syntax Error At Run Time
    [Documentation]    FAIL No keyword with name 'Non existing keyword' found.
    Run Keyword And Expect Error    *    Non existing keyword

Expect Error When Syntax Error In Setting Variables
    [Documentation]    FAIL Cannot set variable '\@{incompatible}': Expected list-like value, got string.
    Run Keyword And Expect Error    *    Invalid Syntax When Setting Variable

Expect Error When Syntax Error In For Loop
    [Documentation]    FAIL  Variable '\${nonexisting}' not found.
    Run Keyword And Expect Error    *    For Loop With Syntax Error

Expect Error When Access To Nonexisting Variable
    Run Keyword And Expect Error    Variable '\${nonexisting}' not found.    Access To Nonexisting Variable

Expect Error When Access To List Variable Nonexisting Index Syntax 1
    ${expected_err_msg} =  Set Variable    Resolving variable '\${list[2]}' failed: IndexError:*
    Run Keyword And Expect Error    ${expected_err_msg}    Access To List Variable Nonexisting Index Syntax 1

Expect Error When Access To List Variable Nonexisting Index Syntax 2
    ${expected_err_msg} =  Set Variable    List variable '\@{list}' has no item in index 2.
    Run Keyword And Expect Error    ${expected_err_msg}    Access To List Variable Nonexisting Index Syntax 2

Expect Error When Access To Dictionary Nonexisting Key Syntax 1
    ${expected_err_msg} =  Set Variable   Resolving variable '\${dict[c]}' failed: NameError: name 'c' is not defined
    Run Keyword And Expect Error    ${expected_err_msg}    Access To Dictionary Variable Nonexisting Key Syntax 1

Expect Error When Access To Dictionary Nonexisting Key Syntax 2
    ${expected_err_msg} =  Set Variable    Dictionary variable '\&{dict}' has no key 'c'.
    Run Keyword And Expect Error    ${expected_err_msg}    Access To Dictionary Variable Nonexisting Key Syntax 2

*** Keywords ***
Passing UK
    Log    Hello world
    No Operation
    ${ret} =    Evaluate    1+2
    [Return]    ${ret}

Failing Uk
    Passing Uk
    Fail    Expected failure in UK
    Fail    This should not be executed

Timeouting UK
    [Timeout]    0.1 seconds
    Run Keyword And Ignore Error    Sleep    1 hour

Invalid Syntax When Setting Variable
    @{incompatible} =    Set Variable    string

For Loop With Syntax Error
    : FOR    ${a}    IN    ${nonexisting}
    \    Whatever

Broken User Keyword
    ${x}

Access To Nonexisting Variable
    Log    ${nonexisting}

Access To List Variable Nonexisting Index Syntax 1
    ${list} =    Create list    1    2
    Log    ${list[2]}

Access To List Variable Nonexisting Index Syntax 2
    ${list} =    Create list    1    2
    Log    @{list}[2]

Access To Dictionary Variable Nonexisting Key Syntax 1
    ${dict} =    Create dictionary    a=1    b=2
    Log    ${dict[c]}

Access To Dictionary Variable Nonexisting Key Syntax 2
    ${dict} =    Create dictionary    a=1    b=2
    Log    &{dict}[c]
