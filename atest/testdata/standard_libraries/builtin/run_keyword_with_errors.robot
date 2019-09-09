*** Settings ***
Library              OperatingSystem

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
    [Documentation]    FAIL Assignment can contain only one list variable.
    Run Keyword And Ignore Error    Invalid Syntax When Setting Variable

Ignore Error When Invalid Return Values When Setting Variables
    ${status}    ${error} =    Run Keyword And Ignore Error    Invalid Return Values When Setting Variables
    Should Be Equal    ${status}: ${error}    FAIL: Cannot set variables: Expected 2 return values, got 3.

Ignore Error When Syntax Error In For Loop
    [Documentation]    FAIL Invalid FOR loop variable 'IN KEKKONEN'.
    Run Keyword And Ignore Error    For Loop With Syntax Error

Ignore Error When Non Existing Variable In For Loop
    Run Keyword And Ignore Error    For Loop With Non Existing Variable

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

Ignore Error With "Passing" Exceptions
    [Documentation]    PASS    The message
    Keyword With Ignore Error With "Passing" Exceptions
    Run Keyword And Ignore Error    Pass Execution    The message
    Fail    Test should have passsed already!

Expect Error When Error Occurs
    Run Keyword And Expect Error    ${ERROR MESSAGE}    ${FAIL KW}    ${ERROR MESSAGE}

Expect Error When Different Error Occurs
    [Documentation]    FAIL Expected error 'My error' but got 'My error message'.
    Run Keyword And Expect Error    My error    Fail    ${ERROR MESSAGE}
    Fail    This should not be executed

Expect Error When Different Error Occurs 2
    [Documentation]    FAIL STARTS: Expected error 'My error' but got 'Evaluating expression 'foo == bar' failed: NameError:
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
    Run Keyword And Expect Error
    ...    My error message\nIn multiple\nLines
    ...    Fail    My error message\nIn multiple\nLines
    Run Keyword And Expect Error
    ...    My error message*Lines
    ...    Fail    My error message\nIn multiple\nLines

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
    Run Keyword And Expect Error
    ...    Directory '%{TEMPDIR}' exists.
    ...    Directory Should Not Exist    %{TEMPDIR}
    Run Keyword And Expect Error
    ...    There are no errors
    ...    Log Many    @{NEEDS ESCAPING}

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
    Run Keyword And Expect Error
    ...    No keyword with name 'Non existing keyword' found.
    ...    Non existing keyword

Expect Error When Syntax Error In Setting Variables
    [Documentation]    FAIL Assignment can contain only one list variable.
    Run Keyword And Expect Error    *    Invalid Syntax When Setting Variable

Expect Error When Invalid Return Values When Setting Variables
    Run Keyword And Expect Error
    ...    Cannot set variables: Expected 2 return values, got 3.
    ...    Invalid Return Values When Setting Variables

Expect Error When Syntax Error In For Loop
    [Documentation]    FAIL Invalid FOR loop variable 'IN KEKKONEN'.
    Run Keyword And Expect Error    *    For Loop With Syntax Error

Expect Error When Non Existing Variable In For Loop
    Run Keyword And Expect Error
    ...    Variable '\${non existing}' not found.
    ...    For Loop With Non Existing Variable

Expect Error When Access To Nonexisting Variable
    Run Keyword And Expect Error
    ...    Variable '\${nonexisting}' not found.
    ...    Access To Nonexisting Variable

Expect Error When Access To List Variable Nonexisting Index Syntax 1
    Run Keyword And Expect Error
    ...    Resolving variable '\${list?2?}' failed: IndexError:*
    ...    Access To List Variable Nonexisting Index Syntax 1

Expect Error When Access To List Variable Nonexisting Index Syntax 2
    Run Keyword And Expect Error
    ...    List '\@{list}' has no item in index 2.
    ...    Access To List Variable Nonexisting Index Syntax 2

Expect Error When Access To Dictionary Nonexisting Key Syntax 1
    Run Keyword And Expect Error
    ...    Resolving variable '\${dict?c?}' failed: NameError: *
    ...    Access To Dictionary Variable Nonexisting Key Syntax 1

Expect Error When Access To Dictionary Nonexisting Key Syntax 2
    Run Keyword And Expect Error
    ...    Dictionary '\&{dict}' has no key 'c'.
    ...    Access To Dictionary Variable Nonexisting Key Syntax 2

Expect Error With Explicit GLOB
    [Documentation]    FAIL Expected error 'GLOB:Your *' but got 'My message'.
    [Template]    Run Keyword And Expect Error
    GLOB:My message    Fail    My message
    GLOB: My mes*g?    Fail    My message
    GLOB:Your *        Fail    My message

Expect Error With EQUALS
    [Documentation]    FAIL Expected error 'EQUALS:*' but got 'My message'.
    [Template]    Run Keyword And Expect Error
    EQUALS:My message        Fail    My message
    EQUALS: My [message]?    Fail    My [message]?
    EQUALS:*                 Fail    My message

Expect Error With STARTS
    [Documentation]    FAIL Expected error 'STARTS: my' but got 'My message'.
    [Template]    Run Keyword And Expect Error
    STARTS:My me    Fail    My message
    STARTS: My      Fail    My message
    STARTS: my      Fail    My message

Expect Error With REGEXP
    [Documentation]    FAIL Expected error 'REGEXP:oopps' but got 'My message'.
    [Template]    Run Keyword And Expect Error
    REGEXP:My.*                       Fail    My message
    REGEXP: (My|Your) [Mm]\\w+ge!?    Fail    My message
    REGEXP:oopps                      Fail    My message

Expect Error With Unrecognized Prefix
    [Documentation]    FAIL Expected error '1:2:3:4:5' but got 'Ooops'.
    [Template]    Run Keyword And Expect Error
    XXX:My message    Fail    XXX:My message
    :Message:         Fail    :Message:
    1:2:3:4:5         Fail    Ooops

Expect Error With "Passing" Exceptions
    [Documentation]    PASS    The message
    Keyword With Expect Error With "Passing" Exceptions
    Run Keyword And Expect Error    Whatever    Pass Execution    The message
    Fail    Test should have passsed already!

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

Invalid Return Values When Setting Variables
    ${one}    ${two} =    Create List    too    many    args

Invalid Syntax When Setting Variable
    @{this}    @{is}    @{invalid} =    Create List

For Loop With Syntax Error
    FOR    ${a}    IN KEKKONEN   foo    bar
        Whatever
    END

For Loop With Non Existing Variable
    FOR    ${a}    IN    ${non existing}
        Whatever
    END

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

Keyword With Ignore Error With "Passing" Exceptions
    Run Keyword And Ignore Error    Return From Keyword
    Fail    Should have returned from keyword already!

Keyword With Expect Error With "Passing" Exceptions
    Run Keyword And Expect Error    Whatever    Return From Keyword
    Fail    Should have returned from keyword already!
