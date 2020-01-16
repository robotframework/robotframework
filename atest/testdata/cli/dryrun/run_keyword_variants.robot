*** Variables ***
${LOG GOT WRONG ARGS}    Keyword 'BuiltIn.Log' expected 1 to 6 arguments, got
${UK GOT WRONG ARGS}     Keyword 'UK' expected 0 arguments, got
${LOG KW}                Log
@{LOG THAT}              Log    that    DEBUG

*** Test Cases ***
Run Keyword With Keyword with Invalid Number of Arguments
    [Documentation]  FAIL ${LOG GOT WRONG ARGS} 0.
    Run Keyword    Log

Run Keyword With Missing Keyword
    [Documentation]  FAIL No keyword with name 'Missing' found.
    Run Keyword    Missing

Keywords with variable in name are ignored
    Run Keyword    ${non-existing variable}
    Run Keyword    No Operation
    Run Keyword    Existing variable ${42}
    Run Keywords    ${non existing}    No Operation    Existing @{TEST TAGS}

Keywords with variable in name are ignored also when variable is argument
    Higher order fun    No Operation
    Higher order fun    ${name}

Run Keyword With UK
    Run Keyword  UK

Run Keyword With Failing UK
    [Documentation]  FAIL ${LOG GOT WRONG ARGS} 0.
    Run Keyword  Failing UK

Comment
    Comment  Missing Keyword  Should Not Fail  Even Missing ${variable} Should Not Fail

Set Test/Suite/Global Variable
    Set Test Variable  ${test}  value
    Set Test Variable  \${test}
    Set Test Variable  $test
    Set Suite Variable  ${suite}
    Set Suite Variable  \${suite}  value
    Set Suite Variable  $suite
    Set Suite Variable  ${global}
    Set Suite Variable  \${global}
    Set Suite Variable  $global  value

Variable Should (Not) Exist
    Variable Should Exist  ${var}
    Variable Should Exist  \${var}
    Variable Should Exist  $var
    Variable Should Not Exist  ${var}
    Variable Should Not Exist  \${var}
    Variable Should Not Exist  $var

Get Variable Value
    Get Variable Value  ${var}
    Get Variable Value  \${var}  default
    Get Variable Value  $var  ${default}

Set Variable If
    Set Variable If  True  ${foo}  ${bar}

Run Keywords When All Keywords Pass
    Run Keywords  Fail  No Operation  UK

Run Keywords When One Keyword Fails
    [Documentation]  FAIL ${LOG GOT WRONG ARGS} 0.
    Run Keywords  Fail  No Operation  Log  UK

Run Keywords When Multiple Keyword Fails
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 0.\n\n
    ...  2) No keyword with name 'Missing' found.
    Run Keywords  Fail  No Operation  Log  UK  Missing

Run Keywords With Arguments When All Keywords Pass
    Run Keywords  Log Many  this  is  valid  AND  No Operation

Run Keywords With Arguments When One Keyword Fails
    [Documentation]  FAIL  ${LOG GOT WRONG ARGS} 12.
    Run Keywords  Log  valid  AND  Log  1  2  3  4  5  6  7  8  9  10  11  12

Run Keywords With Arguments When Multiple Keyword Fails
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 8.\n\n
    ...  2) No keyword with name 'Unknown Keyword' found.
    Run Keywords
    ...    Log    msg    DEBUG    and    too    many    args    we    have
    ...    AND
    ...    Unknown Keyword

Run Keywords With Arguments With Variables
    Run Keywords  ${LOG KW}  this  DEBUG  AND  @{LOG THAT}  AND  Log  only kw

Run Keyword in For Loop Pass
    FOR    ${i}    IN RANGE    5
        Run Keyword  No Operation
    END

Run Keyword in For Loop Fail
    [Documentation]  FAIL ${LOG GOT WRONG ARGS} 0.
    FOR    ${i}    IN RANGE    5
        Run Keyword    Log
    END

Wait Until Keyword Succeeds Pass
    Wait Until Keyword Succeeds  30 seconds  1 second  No Operation

Wait Until Keyword Succeeds Fail
    [Documentation]  FAIL ${LOG GOT WRONG ARGS} 0.
    Wait Until Keyword Succeeds  30 seconds  1 second  Log

Run Keyword If Pass
    Run Keyword If  ${TRUE}  No Operation

Run Keyword If Fail
    [Documentation]  FAIL ${LOG GOT WRONG ARGS} 0.
    Run Keyword If  ${FALSE}  Log

Run Keyword If with ELSE
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 0.\n\n
    ...  2) ${UK GOT WRONG ARGS} 1.\n\n
    ...  3) No keyword with name 'Non Existing' found.\n\n
    ...  4) ${LOG GOT WRONG ARGS} 8.
    Run Keyword If    expression    No Operation    ELSE    UK
    RunKeywordIf      expression    Log             ELSE    No Operation
    runkeywordif      expression    No operation    ELSE    UK    not allowed
    RUN_KEYWORD_IF    expression    Non Existing    ELSE    Log    1    2    3    4    5    6    7    8

Run Keyword If with ELSE IF
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 0.\n\n
    ...  2) ${UK GOT WRONG ARGS} 1.\n\n
    ...  3) No keyword with name 'Non Existing' found.\n\n
    ...  4) ${LOG GOT WRONG ARGS} 8.
    Run Keyword If    expr    No Operation    ELSE IF    expr    UK
    Run Keyword If    expr    Log             ELSE IF    expr    No Operation
    Run Keyword If    expr    No operation    ELSE IF    expr    UK    not allowed
    Run Keyword If    expr    Non Existing    ELSE IF    expr    Log    1    2    3    4    5    6    7    8

Run Keyword If with ELSE IF and ELSE
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 0.\n\n
    ...  2) ${UK GOT WRONG ARGS} 2.\n\n
    ...  3) No keyword with name 'not found kw' found.\n\n
    ...  4) ${LOG GOT WRONG ARGS} 10.
    Run Keyword If    expr    Log
    ...    ELSE IF    expr    UK    1    2
    ...    ELSE IF    expr    not found kw
    ...    ELSE    Log    1    2    3    4    5    6    7    8    9    10

Run Keyword If with ELSE IF and ELSE without keywords
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) Invalid 'Run Keyword If' usage.\n\n
    ...  2) Invalid 'Run Keyword If' usage.\n\n
    ...  3) Invalid 'Run Keyword If' usage.\n\n
    ...  4) Invalid 'Run Keyword If' usage.\n\n
    ...  5) Invalid 'Run Keyword If' usage.\n\n
    ...  6) Invalid 'Run Keyword If' usage.\n\n
    ...  7) Invalid 'Run Keyword If' usage.\n\n
    ...  8) Invalid 'Run Keyword If' usage.\n\n
    ...  9) Invalid 'Run Keyword If' usage.\n\n
    ...  10) Invalid 'Run Keyword If' usage.\n\n
    ...  11) Keyword 'BuiltIn.Run Keyword If' expected at least 2 arguments, got 1.\n\n
    ...  12) Keyword 'BuiltIn.Run Keyword If' expected at least 2 arguments, got 1.\n\n
    ...  13) Invalid 'Run Keyword If' usage.\n\n
    ...  14) Invalid 'Run Keyword If' usage.
    Run Keyword If    False   No Operation    ELSE IF    True
    Run Keyword If    False   No Operation    ELSE IF
    Run Keyword If    False   No Operation    ELSE
    Run Keyword If    False   No Operation    ELSE IF    True    ELSE    No Operation
    Run Keyword If    False   No Operation    ELSE IF    ELSE    No Operation
    Run Keyword If    False   No Operation    ELSE IF    ELSE
    Run Keyword If    False   ELSE IF    ELSE
    Run Keyword If    False   ELSE IF
    Run Keyword If    False   ELSE
    Run Keyword If    ELSE IF    ELSE
    Run Keyword If    ELSE IF
    Run Keyword If    ELSE
    Run Keyword If    True    ELSE    No Operation
    Run Keyword If    True    ELSE

Run Keyword If with escaped or non-caps ELSE IF and ELSE
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 8.\n\n
    ...  2) ${LOG GOT WRONG ARGS} 7.
     Run Keyword If    expr    Log    \ELSE IF    INFO    and    too    many    args    we    have
     Run Keyword If    expr    Log    \ELSE    DEBUG
     Run Keyword If    expr    Log    else if    WARN    html=yes
     Run Keyword If    expr    Log    else    too    many    args    again    here    is

Run Keyword If with list variable in ELSE IF and ELSE
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 9.\n\n
    ...  2) ${LOG GOT WRONG ARGS} 8.
    Run Keyword If    @{list}
    Run Keyword If    @{list}    ELSE      @{list}
    Run Keyword If    @{list}    ELSE IF   @{list}
    Run Keyword If    @{list}    ELSE IF   @{list}    ELSE    @{list}
    Run Keyword If    @{list}    Not Considered Keyword     ELSE    @{list}    XXX
    Run Keyword If    @{list}    ELSE      Log   1    2    3    4    5    6    7    8    9
    Run Keyword If    expr       No Operation    ELSE IF    @{list}    UK    1
    Run Keyword If    expr       No Operation    ELSE IF    @{list}    UK    1    2
    ...    ELSE IF    expr       Log    1    2    3    4    5    6    7    8
    Run Keyword If    expr       No Operation    ELSE IF    @{list}    No Operation
    ...  ELSE    @{list}

Test Teardown Related Run Keyword Variants
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) ${LOG GOT WRONG ARGS} 0.\n\n
    ...  2) ${LOG GOT WRONG ARGS} 0.\n\n
    ...  3) ${LOG GOT WRONG ARGS} 0.
    Run Keyword If Test Failed  Log
    Run Keyword If Test Passed  Log
    Run Keyword If Timeout Occurred  Log

Given/When/Then
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...    1) No keyword with name 'Nonex' found.\n\n
    ...    2) Keyword 'BuiltIn.Convert To Integer' expected 1 to 2 arguments, got 0.
    Given run keyword if    True    Log     This is really strange usage.....
    When run keyword if    expr
    ...    No Operation
    ...    ELSE IF    expr
    ...    No Operation
    ...    ELSE
    ...    No Operation
    and run keyword if      True    Nonex    ELSE    Convert To Integer
    Then run keywords
    ...    Log    xxx    INFO     AND
    ...    Log    yyy    DEBUG    AND
    ...    Log    zzz    TRACE
    and run keywords    No Operation    Log Many    No Operation

*** Keywords ***
UK
    No Operation

Failing UK
    Log

Higher order fun
    [Arguments]    ${name}
    Run Keyword    ${name}
