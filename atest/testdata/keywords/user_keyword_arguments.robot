*** Settings ***
Library           Collections

*** Variables ***
${VAR}            Variable value
@{LIST}           With    three    values

*** Test Cases ***
Correct Number Of Arguments When No Defaults Or Varargs
    ${ret} =    A 0
    Should Be Equal    ${ret}    a_0
    ${ret} =    A 0 B
    Should Be Equal    ${ret}    a_0_b
    ${ret} =    A 1    my arg
    Should Be Equal    ${ret}    a_1: my arg
    ${ret} =    A 3    a1    a2    a3
    Should Be Equal    ${ret}    a_3: a1 a2 a3

Too Few Arguments When No Defaults Or Varargs 1
    [Documentation]    FAIL Keyword 'A 1' expected 1 argument, got 0.
    A 1

Too Few Arguments When No Defaults Or Varargs 2
    [Documentation]    FAIL Keyword 'A 3' expected 3 arguments, got 2.
    A 3    a1    a2

Too Many Arguments When No Defaults Or Varargs 1
    [Documentation]    FAIL Keyword 'A 0' expected 0 arguments, got 10.
    A 0    This    is    too    much    !    Really
    ...    way    too    much    !!!!!

Too Many Arguments When No Defaults Or Varargs 2
    [Documentation]    FAIL Keyword 'A 1' expected 1 argument, got 2.
    A 1    Too    much

Too Many Arguments When No Defaults Or Varargs 3
    [Documentation]    FAIL Keyword 'A 3' expected 3 arguments, got 4.
    A 3    a1    a2    a3    a4

Correct Number Of Arguments With Defaults
    ${ret} =    A 0 1
    Should Be Equal    ${ret}    a_0_1: default
    ${ret} =    A 0 1    This works too
    Should Be Equal    ${ret}    a_0_1: This works too
    ${ret} =    A 1 3    My argument
    Should Be Equal    ${ret}    a_1_3: My argument default default
    ${ret} =    A 1 3    My argument    My argument 2
    Should Be Equal    ${ret}    a_1_3: My argument My argument 2 default
    ${ret} =    A 1 3    My argument    My argument 2    My argument 3
    Should Be Equal    ${ret}    a_1_3: My argument My argument 2 My argument 3

Too Few Arguments With Defaults
    [Documentation]    FAIL Keyword 'A 1 3' expected 1 to 3 arguments, got 0.
    A 1 3

Too Many Arguments With Defaults 1
    [Documentation]    FAIL Keyword 'A 0 1' expected 0 to 1 arguments, got 2.
    A 0 1    Too    much

Too Many Arguments With Defaults 2
    [Documentation]    FAIL Keyword 'A 1 3' expected 1 to 3 arguments, got 4.
    A 1 3    This    is    too    much

Correct Number Of Arguments With Varargs
    ${ret} =    A 0 N
    Should Be Equal    ${ret}    a_0_n: \
    ${ret} =    A 0 N    My arg
    Should Be Equal    ${ret}    a_0_n: My arg
    ${ret} =    A 0 N    1    2    3    4
    Should Be Equal    ${ret}    a_0_n: 1 2 3 4
    ${ret} =    A 1 N    Required arg
    Should Be Equal    ${ret}    a_1_n: Required arg \
    ${ret} =    A 1 N    1 (req)    2    3    4    5
    ...    6    7    8    9
    Should Be Equal    ${ret}    a_1_n: 1 (req) 2 3 4 5 6 7 8 9

Too Few Arguments With Varargs
    [Documentation]    FAIL Keyword 'A 1 N' expected at least 1 argument, got 0.
    A 1 N

Correct Number Of Arguments With Defaults And Varargs
    ${ret} =    A 1 2 N    Required arg
    Should Be Equal    ${ret}    a_1_2_n: Required arg default \
    ${ret} =    A 1 2 N    one (req)    two    three    four
    Should Be Equal    ${ret}    a_1_2_n: one (req) two three four

Too Few Arguments With Defaults And Varargs
    [Documentation]    FAIL Keyword 'A 1 2 N' expected at least 1 argument, got 0.
    A 1 2 N

Default With Variable
    ${ret} =    Default With Variable    Given value
    Should Be Equal    ${ret}    Given value
    ${ret} =    Default With Variable
    Should Be Equal    ${ret}    Variable value

Local Variable Does Not Affect Variable In Default Value
    ${var} =    Set Variable    not used as default
    ${ret} =    Default With Variable
    Should Be Equal    ${ret}    Variable value

Explicitly Set Variable Affects Variable In Default Value
    Set Test Variable    ${var}    This is used as default
    ${ret} =    Default With Variable
    Should Be Equal    ${ret}    This is used as default

Default With Automatic Variable
    ${ret} =    Default With None Variable
    Should Be Equal    ${ret}    ${None}
    ${ret} =    Default With Number Variable
    Should Be Equal    ${ret}    ${1000}

Default With Extended Variable Syntax
    ${ret} =    Default With Extended Variable Syntax
    Should Be Equal    ${ret}    VARIABLE VALUE

Calling Using List Variables
    [Documentation]    FAIL Keyword 'A 0 1' expected 0 to 1 arguments, got 3.
    A 0    @{EMPTY}
    A 1    @{EMPTY}    arg
    A 3    @{LIST}
    A 1 3    @{LIST}
    A 3    @{LIST}    @{EMPTY}
    A 0 1    @{LIST}    @{EMPTY}

Calling Using Dict Variables
    &{arg} =    Create Dictionary    arg=value
    &{args} =    Create Dictionary    arg1=v1    arg3=v3
    A 0    &{EMPTY}
    ${ret} =    A 1    &{arg}
    Should Be Equal    ${ret}    a_1: value
    ${ret} =    A 3    &{args}    arg2=v2
    Should Be Equal    ${ret}    a_3: v1 v2 v3
    ${ret} =    A 1 3    &{args}
    Should Be Equal    ${ret}    a_1_3: v1 default v3

Caller does not see modifications to varargs
    @{v1} =    Create List    list1
    @{v2} =    Create List    list2
    Mutate Lists    ${v1}    @{v2}
    Should Be True    @{v1} == ['list1', 'list1.2']
    Should Be True    @{v2} == ['list2']

Invalid Arguments Spec - Invalid argument syntax
    [Documentation]    FAIL Invalid argument specification: Invalid argument syntax 'no deco'.
    Invalid argument syntax

Invalid Arguments Spec - Non-default after defaults
    [Documentation]    FAIL Invalid argument specification: Non-default argument after default arguments.
    Non-default after defaults

Invalid Arguments Spec - Varargs not last
    [Documentation]    FAIL Invalid argument specification: Positional argument after varargs.
    Varargs not last

*** Keywords ***
A 0
    [Return]    a_0

A 0 B
    [Return]    a_0_b

A 1
    [Arguments]    ${arg}
    [Return]    a_1: ${arg}

A 3
    [Arguments]    ${arg1}    ${arg2}    ${arg3}
    [Return]    a_3: ${arg1} ${arg2} ${arg3}

A 0 1
    [Arguments]    ${arg}=default
    [Return]    a_0_1: ${arg}

A 1 3
    [Arguments]    ${arg1}    ${arg2}=default    ${arg3}=default
    [Return]    a_1_3: ${arg1} ${arg2} ${arg3}

A 0 N
    [Arguments]    @{args}
    ${ret} =    Catenate    @{args}
    [Return]    a_0_n: ${ret}

A 1 N
    [Arguments]    ${arg}    @{args}
    ${ret} =    Catenate    @{args}
    [Return]    a_1_n: ${arg} ${ret}

A 1 2 N
    [Arguments]    ${arg1}    ${arg2}=default    @{args}
    ${ret} =    Catenate    @{args}
    [Return]    a_1_2_n: ${arg1} ${arg2} ${ret}

Default With Variable
    [Arguments]    ${arg}=${VAR}
    [Return]    ${arg}

Default With None Variable
    [Arguments]    ${arg}=${None}
    [Return]    ${arg}

Default With Number Variable
    [Arguments]    ${arg}=${1e3}
    [Return]    ${arg}

Default With Extended Variable Syntax
    [Arguments]    ${arg}=${VAR.upper()}
    [Return]    ${arg}

Mutate Lists
    [Arguments]    ${list1}    @{list2}
    Should Be True    @{list1} == ['list1']
    Should Be True    @{list2} == ['list2']
    Append To List    ${list1}    list1.2
    Append To List    ${list2}    list2.2
    Should Be True    @{list1} == ['list1', 'list1.2']
    Should Be True    @{list2} == ['list2', 'list2.2']

Invalid argument syntax
    [Arguments]    no deco
    No Operation

Non-default after defaults
    [Arguments]    ${named}=value    ${positional}
    No Operation

Varargs not last
    [Arguments]    @{varargs}    ${positional}
    No Operation
