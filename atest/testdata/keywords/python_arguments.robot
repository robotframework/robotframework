*** Settings ***
Library           ArgumentsPython
Library           Annotations.py
Library           ../libdoc/Decorators.py

*** Variables ***
@{LIST}           With    three    values

*** Test Cases ***
Correct Number Of Arguments When No Defaults Or Varargs
    ${ret} =    A 0
    Should Be Equal    ${ret}    a_0
    ${ret} =    A 1    my arg
    Should Be Equal    ${ret}    a_1: my arg
    ${ret} =    A 3    a1    a2    a3
    Should Be Equal    ${ret}    a_3: a1 a2 a3

Too Few Arguments When No Defaults Or Varargs 1
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 1' expected 1 argument, got 0.
    A 1

Too Few Arguments When No Defaults Or Varargs 2
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 3' expected 3 arguments, got 2.
    A 3    a1    a2

Too Many Arguments When No Defaults Or Varargs 1
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 0' expected 0 arguments, got 10.
    A 0    This    is    too    much    !    Really
    ...    way    too    much    !!!!!

Too Many Arguments When No Defaults Or Varargs 2
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 1' expected 1 argument, got 2.
    A 1    Too    much

Too Many Arguments When No Defaults Or Varargs 3
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 3' expected 3 arguments, got 4.
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
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 1 3' expected 1 to 3 arguments, got 0.
    A 1 3

Too Many Arguments With Defaults 1
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 0 1' expected 0 to 1 arguments, got 2.
    A 0 1    Too    much

Too Many Arguments With Defaults 2
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 1 3' expected 1 to 3 arguments, got 4.
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
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 1 N' expected at least 1 argument, got 0.
    A 1 N

Correct Number Of Arguments With Defaults And Varargs
    ${ret} =    A 1 2 N    Required arg
    Should Be Equal    ${ret}    a_1_2_n: Required arg default \
    ${ret} =    A 1 2 N    one (req)    two    three    four
    Should Be Equal    ${ret}    a_1_2_n: one (req) two three four

Too Few Arguments With Defaults And Varargs
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 1 2 N' expected at least 1 argument, got 0.
    A 1 2 N

Calling Using List Variables
    [Documentation]    FAIL Keyword 'ArgumentsPython.A 0 1' expected 0 to 1 arguments, got 3.
    A 0    @{EMPTY}
    A 1    @{EMPTY}    arg
    A 3    @{LIST}
    A 1 3    @{LIST}
    A 3    @{LIST}    @{EMPTY}
    A 0 1    @{LIST}    @{EMPTY}

Calling Using Annotations
    ${ret}=    Annotations    one    two_type_str
    Should Be Equal    ${ret}    annotations: one two_type_str

Calling Using Annotations With Defaults
    ${ret}=    Annotations With Defaults    one
    Should Be Equal    ${ret}    annotations: one default

Dummy decorator does not preserve arguments 1
    Keyword using decorator    foo    bar    zap

Dummy decorator does not preserve arguments 2
    [Documentation]    FAIL STARTS: TypeError:
    Keyword using decorator    argument    mismatch    is    not    detected

Decorator using functools.wraps preserves arguments
    [Documentation]    FAIL Keyword 'Decorators.Keyword Using Decorator With Wraps' expected 2 to 3 arguments, got 4.
    Keyword using decorator with wraps    foo    bar    zap
    Keyword using decorator with wraps    argument    mismatch    is    detected
