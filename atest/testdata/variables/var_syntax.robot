*** Test Cases ***
Scalar
    VAR    ${name}    value
    Should Be Equal    ${name}    value

Scalar with separator
    VAR    ${a}    ${1}    2       3       separator=\n
    VAR    ${b}    1       ${2}    3       separator====
    VAR    ${c}    1       2       ${3}    separator=
    VAR    ${d}    ${a}    ${b}    ${c}    separator=${0}
    VAR    ${e}                            separator=has no effect
    VAR    ${f}    separator=NO    separator=NO    separator=--YES--
    Should Be Equal    ${a}    1\n2\n3
    Should Be Equal    ${b}    1===2===3
    Should Be Equal    ${c}    123
    Should Be Equal    ${d}    ${a}0${b}0${c}
    Should Be Equal    ${e}    ${EMPTY}
    Should Be Equal    ${f}    separator=NO--YES--separator=NO

List
    VAR    @{name}    v1    v2    separator=v3
    Should Be Equal    ${name}    ${{['v1', 'v2', 'separator=v3']}}

Dict
    VAR    &{name}    k1=v1    k2=v2    separator=v3
    Should Be Equal    ${name}    ${{{'k1': 'v1', 'k2': 'v2', 'separator': 'v3'}}}

Equals is accepted
    VAR    ${name}=    value
    Should Be Equal    ${name}    value
    VAR    @{name} =    v1    v2    v3
    Should Be Equal    ${name}    ${{['v1', 'v2', 'v3']}}
    VAR    &{name}=    k1=v1    k2=v2
    Should Be Equal    ${name}    ${{{'k1': 'v1', 'k2': 'v2'}}}

Scopes 1
    VAR   ${local1}    local1
    VAR   ${local2}    scope=local2    scope=LOCAL
    VAR   @{test}      scope=value     scope=test
    VAR   &{suite}     scope=value     scope=${{'suite'}}
    VAR   ${global}    global          scope=GLOBAL
    Should Be Equal    ${local1}    local1
    Should Be Equal    ${local2}    scope=local2
    Should Be Equal    ${test}      ${{['scope=value']}}
    Should Be Equal    ${suite}     ${{{'scope': 'value'}}}
    Should Be Equal    ${global}    global
    Scopes
    Should Be Equal    ${test}      new-test
    Variable Should Not Exist    ${local3}

Scopes 2
    Variable Should Not Exist    ${local1}
    Variable Should Not Exist    ${local2}
    Should Be Equal    ${suite}     ${{{'scope': 'value'}}}
    Should Be Equal    ${global}    global

Invalid scope
    [Documentation]    FAIL    VAR option 'scope' does not accept value 'invalid'. Valid values are 'GLOBAL', 'SUITE', 'TEST', 'TASK' and 'LOCAL'.
    VAR    ${x}    x    scope=invalid

Invalid scope from variable
    [Documentation]    FAIL    Invalid VAR scope: Value 'invalid' is not accepted. Valid values are 'GLOBAL', 'SUITE', 'TEST', 'TASK' and 'LOCAL'.
    VAR    ${x}    x    scope=${{'invalid'}}

Non-existing variable as scope
    [Documentation]    FAIL    Invalid VAR scope: Variable '\${invalid}' not found.
    VAR    ${x}    x    scope=${invalid}

Non-existing variable in value
    [Documentation]    FAIL    Setting variable '\${x}' failed: Variable '\${bad}' not found.
    VAR    ${x}    ${bad}

Non-existing variable in separator
    [Documentation]    FAIL    Setting variable '\${x}' failed: Variable '\${bad}' not found.
    VAR    ${x}    a    b    separator=${bad}

Named based on another variable
    VAR    ${x}      y
    VAR    ${${x}}   z
    VAR    ${x-${x}-${y}}   x-y-z
    Should Be Equal    ${y}    z
    Should Be Equal    ${x-y-z}    x-y-z

Non-existing variable in name
    [Documentation]    FAIL    Setting variable '\${this is \${bad}}' failed: Variable '${\bad}' not found.
    VAR    ${this is ${bad}}    wharever

With FOR
    FOR    ${x}    IN    a    b    c
        VAR    ${y}    ${x}
        Should Be Equal    ${y}    ${x}
    END
    Should Be Equal    ${y}    c

With WHILE
    VAR    ${cond}    True
    WHILE    ${cond}
        VAR    ${cond}    False
    END
    Should Be Equal    ${cond}    False

With IF
    IF    True
        VAR    ${x}    set
    ELSE
        VAR    ${x}    not set
    END
    Should Be Equal    ${x}    set

With inline IF
    IF    False    VAR    ${x}    not set    ELSE    VAR    ${x}    set
    Should Be Equal    ${x}    set

With TRY
    TRY
        VAR    ${x}    try
    EXCEPT
        VAR    ${x}    not set
    ELSE
        VAR    ${x}    ${x}-else
    FINALLY
        VAR    ${x}    ${x}-finally
    END
    Should Be Equal    ${x}    try-else-finally

*** Keywords ***
Scopes
    Variable Should Not Exist    ${local1}
    Variable Should Not Exist    ${local2}
    Should Be Equal    ${test}      ${{['scope=value']}}
    Should Be Equal    ${suite}     ${{{'scope': 'value'}}}
    Should Be Equal    ${global}    global
    VAR                ${local3}    local3
    VAR                ${test}      new    test    scope=${{'test'}}    separator=${{'-'}}
    Should Be Equal    ${local3}    local3
    Should Be Equal    ${test}      new-test
