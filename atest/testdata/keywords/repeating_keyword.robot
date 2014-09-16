*** Variables ***
${limit}  ${10}

*** Test Cases ***
Repeat Doing Nothing
    1 x  No Operation
    1000x  NOOPERATION

Repeat With Arguments Doing Nothing
    1 x  Comment  Nothing is done
    42 X  Comment  Still  nothing

Repeat With Messages
    1 x  Log  Hello, world
    33 x  Log  Hi, tellus

Repeating User Keyword
    1 x  Repeating UK  Yo, world
    2 x  Repeating UK  Yo, tellus
    2 x  Repeating UK With Sub KW

Repeating Inside User Keyword
    Repeating Inside UK

Repeating Inside Repeating
    4 x  Repeating Inside UK

Failing Repeat Keyword
    [Documentation]  FAIL Failing instead of repeating
    42 x  Fail  Failing instead of repeating

Not First Repeat Keyword Failing
    [Documentation]  FAIL Recursion limit exceeded
    1000x  Recursive

Failing Repeat Keyword and Teardown
    [Documentation]  FAIL Failing, again, instead of repeating\n\nAlso teardown failed:\nTeardown is executed but fails
    100 x  Fail  Failing, again, instead of repeating
    [Teardown]  Fail  Teardown is executed but fails

Non-Exising Variable In Repeat Keyword
    [Documentation]  FAIL Resolving variable '${non-exiting-variable}' failed: Non-existing variable '${non}'.
    1000x  Log  ${non-exiting-variable}

Non Existing Keyword In Repeat
    [Documentation]  FAIL No keyword with name 'Non Existing Keyword' found.
    1000x  Non Existing Keyword

Zero Repeat
    [Documentation]  This keyword is not executed
    0 x  Fail  This should not be executed

Negative Repeat
    [Documentation]  Negative repeat is the same as zero repeat
    -1 x  Fail  This should not be executed
    -1111 x  Fail  This should not be executed

Repeat With Valid Int Variable
    ${3} x  Log  Repeated ${3} times
    ${2}X  Log  Repeated ${2} times
    ${0} X  Fail  This should not be executed!!
    ${-100}x  Fail  This should not be executed!!

Repeat With Valid String Variable
    ${foo}  Set  4
    ${foo} x  Log  Repeated ${foo} times

Repeat With Variable Using Different Values In One test
    Repeat With Variables  1
    Repeat With Variables  2

Repeat With Variable Using Different Values In Another test
    Repeat With Variables  3

Repeat With Invalid String Variable
    [Documentation]  FAIL STARTS:'bar' cannot be converted to an integer: ValueError:
    ${foo} =  Set  bar
    ${foo} x  Noop

No Repeat With Variable value 2x
    ${foo} =  Set  2 x
    ${foo} =  Returning UK
    Equals  ${foo}  String

Repeat With Non Existing Variable Fails
    [Documentation]  FAIL Non-existing variable '\${foo}'.
    ${foo} x  Noop

Non Existing Keyword In Repeat With Variable
    [Documentation]  FAIL No keyword with name 'Non Existing Keyword' found.
    ${10} x  Non Existing Keyword

Normal Keyword With X At The End
    [Documentation]  FAIL No keyword with name 'Non Existing With X' found.
    Keyword With X
    Non Existing With X

*** Keywords ***
Repeating UK
    [Arguments]  ${msg}
    Log  Hello from Repeating UK
    Log  ${msg}

Repeating UK With Sub KW
    Repeating UK  Sub kw

Repeating Inside UK
    3 x  Repeating UK  Inside UK

Recursive
    ${limit}  Evaluate  ${limit} - 1
    Set Suite Variable  $limit
    Fail If Ints Equal  ${limit}  0  Recursion limit exceeded  No values

Returning UK
    Noop
    [Return]  String

Keyword With X
    NOOP

Repeat With Variables
    [Arguments]  ${count}
    Log  ${count}
    ${actually_repeated}  Set  0
    ${count} X  Increase Count
    Ints Equal  ${count}  ${actually_repeated}

Increase Count
    ${actually_repeated}  Evaluate  ${actually_repeated} + 1
    Set Test Variable  $actually_repeated  ${actually_repeated}

