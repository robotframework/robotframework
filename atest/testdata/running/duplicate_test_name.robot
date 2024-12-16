*** Variables ***
${INDEX}          ${1}

*** Test Cases ***
Duplicates
    [Documentation]    FAIL    Executed!
    Fail    Executed!

Duplicates
    [Documentation]    FAIL    Executed!
    Fail    Executed!

Duplicates
    [Documentation]    FAIL    Executed!
    Fail    Executed!

Duplicates with different case and spaces
    [Documentation]    FAIL    Executed!
    Fail    Executed!

Duplicates with different CASE ands p a c e s
    [Documentation]    FAIL    Executed!
    Fail    Executed!

Duplicates but only one executed
    [Tags]    exclude
    Fail    Not executed!

Duplicates after resolving ${{'variables'}}
    [Documentation]    FAIL    Executed!
    Fail    Executed!

${{'Duplicates'}} after resolving variables
    [Documentation]    FAIL    Executed!
    Fail    Executed!

Duplicates but only one executed
    [Tags]    robot:exclude
    Fail    Not executed!

Duplicates but only one executed
    [Documentation]    FAIL    Executed!
    Fail    Executed!

Test ${INDEX}
    [Documentation]    FAIL    Executed!
    VAR    ${INDEX}    ${INDEX + 1}    scope=SUITE
    Fail    Executed!

Test ${INDEX}
    [Documentation]    FAIL    Executed!
    VAR    ${INDEX}    ${INDEX + 1}    scope=SUITE
    Fail    Executed!

Test ${INDEX}
    [Documentation]    FAIL    Executed!
    VAR    ${INDEX}    ${INDEX + 1}    scope=SUITE
    Fail    Executed!
