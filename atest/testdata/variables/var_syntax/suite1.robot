*** Settings ***
Suite Setup      VAR in suite setup and teardown    suite1 setup
Suite Teardown   VAR in suite setup and teardown    suite1 teardown

*** Test Cases ***
Scalar
    VAR    ${name}    value
    Should Be Equal    ${name}    value

Scalar with separator
    VAR    ${a}    ${1}    2       3       separator=\n
    VAR    ${b}    1       ${2}    3       separator====
    VAR    ${c}    1       2       ${3}    separator=
    VAR    ${d}    ${a}    ${b}    ${c}    separator=${0}
    VAR    ${e}                            separator=no effect
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

Long values
    ${items} =    Create List
    ...    This is a rather long value.
    ...    It will be cut when it is logged by VAR.
    ...    Otherwise it should work normally.
    ...    This is a rather long value.
    ...    It will be cut when it is logged by VAR.
    ...    Otherwise it should work normally.
    VAR    ${scalar}    @{items}
    VAR    @{list}      @{items}
    VAR    &{dict}      &{{dict(enumerate($items))}}
    Should Be Equal    ${scalar}    ${{' '.join($items)}}
    Should Be Equal    ${list}      ${items}
    Should Be Equal    ${dict}      ${{dict(enumerate($items))}}

Invalid name
    [Documentation]    FAIL    Invalid variable name 'bad'.
    VAR    bad    name

No name
    [Documentation]    FAIL    Invalid variable name ''.
    VAR

No name with continuation
    [Documentation]    FAIL    Invalid variable name ''.
    VAR
    ...

Equals is accepted
    VAR    ${name}=    value
    Should Be Equal    ${name}    value
    VAR    @{name} =    v1    v2    v3
    Should Be Equal    ${name}    ${{['v1', 'v2', 'v3']}}
    VAR    &{name}=    k1=v1    k2=v2
    Should Be Equal    ${name}    ${{{'k1': 'v1', 'k2': 'v2'}}}

In root suite setup
    Should Be Equal    ${ROOT}      set in root suite setup

In suite setup
    Should Be Equal    ${SUITE}     set in suite1 setup
    Should Be Equal    ${SUITES}    set in suite1 setup
    Should Be Equal    ${GLOBAL}    set in suite1 setup

Scopes 1
    VAR   ${local1}    local1
    VAR   ${local2}    scope=local2    scope=LOCAL
    VAR   @{TEST}      scope=value     scope=test
    VAR   &{SUITE}     scope=value     scope=${{'suite'}}
    VAR   ${SUITES}    children too    scope=Suites
    VAR   ${GLOBAL}    global          scope=GLOBAL
    Should Be Equal    ${local1}    local1
    Should Be Equal    ${local2}    scope=local2
    Should Be Equal    ${TEST}      ${{['scope=value']}}
    Should Be Equal    ${SUITE}     ${{{'scope': 'value'}}}
    Should Be Equal    ${SUITES}    children too
    Should Be Equal    ${GLOBAL}    global
    Scopes
    Should Be Equal    ${TEST}      new-test
    Variable Should Not Exist    ${local3}

Scopes 2
    Variable Should Not Exist    ${local1}
    Variable Should Not Exist    ${local2}
    Should Be Equal    ${SUITE}     ${{{'scope': 'value'}}}
    Should Be Equal    ${SUITES}    children too
    Should Be Equal    ${GLOBAL}    global
    Should Be Equal    ${ROOT}      set in root suite setup

Invalid scope
    [Documentation]    FAIL    VAR option 'scope' does not accept value 'invalid'. Valid values are 'LOCAL', 'TEST', 'TASK', 'SUITE', 'SUITES' and 'GLOBAL'.
    VAR    ${x}    x    scope=invalid

Invalid scope from variable
    [Documentation]    FAIL    Invalid VAR scope: Value 'invalid' is not accepted. Valid values are 'LOCAL', 'TEST', 'TASK', 'SUITE', 'SUITES' and 'GLOBAL'.
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

Name based on another variable
    VAR    ${x}      y
    VAR    ${${x}}   z
    VAR    ${x-${x}-${y}}   x-y-z
    Should Be Equal    ${y}    z
    Should Be Equal    ${x-y-z}    x-y-z

Name based on variable defined in different scope 1
    VAR    ${x}       g-1
    VAR    ${y}       s-1
    VAR    ${z}       t-1
    VAR    ${${x}}    g-2    scope=GLOBAL
    VAR    ${${y}}    s-2    scope=SUITE
    VAR    ${${z}}    t-2    scope=TEST
    Should Be Equal    ${g-1}    g-2
    Should Be Equal    ${s-1}    s-2
    Should Be Equal    ${t-1}    t-2

Name based on variable defined in different scope 2
    Should Be Equal    ${g-1}    g-2
    Should Be Equal    ${s-1}    s-2
    VAR    ${g-${g-1}}    g-3    scope=GLOBAL
    VAR    ${g-${s-1}}    g-4    scope=GLOBAL
    VAR    ${s-${g-1}}    s-3    scope=SUITE
    VAR    ${s-${s-1}}    s-4    scope=SUITE
    VAR    ${t-${g-1}}    t-3    scope=TEST
    VAR    ${t-${s-1}}    t-4    scope=TEST
    Should Be Equal    ${g-g-2}    g-3
    Should Be Equal    ${g-s-2}    g-4
    Should Be Equal    ${s-g-2}    s-3
    Should Be Equal    ${s-s-2}    s-4
    Should Be Equal    ${t-g-2}    t-3
    Should Be Equal    ${t-s-2}    t-4

Name based on variable defined in different scope 3
    Should Be Equal    ${g-1}      g-2
    Should Be Equal    ${s-1}      s-2
    Should Be Equal    ${g-g-2}    g-3
    Should Be Equal    ${g-s-2}    g-4
    Should Be Equal    ${s-g-2}    s-3
    Should Be Equal    ${s-s-2}    s-4

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
    Variable Should Not Exist    ${local}
    Variable Should Not Exist    ${local1}
    Variable Should Not Exist    ${local2}
    Should Be Equal    ${TEST}      ${{['scope=value']}}
    Should Be Equal    ${SUITE}     ${{{'scope': 'value'}}}
    Should Be Equal    ${GLOBAL}    global
    VAR                ${local3}    local3
    VAR                ${TEST}      new    test    scope=${{'test'}}    separator=${{'-'}}
    Should Be Equal    ${local3}    local3
    Should Be Equal    ${TEST}      new-test

VAR in suite setup and teardown
    [Arguments]    ${where}
    Variable Should Not Exist    ${local}
    Should Be Equal    ${ROOT}      set in root suite setup
    IF    'setup' in $where
        Variable Should Not Exist    ${SUITE}
        Should Be Equal    ${SUITES}    set in root suite setup
        Should Be Equal    ${GLOBAL}    set in root suite setup
    ELSE
        Should Be Equal    ${SUITE}     ${{{'scope': 'value'}}}
        Should Be Equal    ${SUITES}    children too
        Should Be Equal    ${GLOBAL}    global
    END
    VAR    ${local}     value
    VAR    ${SUITE}     set in ${where}    scope=suite
    VAR    ${SUITES}    set in ${where}    scope=suites
    VAR    ${GLOBAL}    set in ${where}    scope=global
    Should Be Equal    ${local}     value
    Should Be Equal    ${SUITE}     set in ${where}
    Should Be Equal    ${SUITES}    set in ${where}
    Should Be Equal    ${GLOBAL}    set in ${where}
    TRY
        VAR    ${TEST}    this fails    scope=test
    EXCEPT    AS    ${err}
        Should Be Equal    ${err}    Setting variable '\${TEST}' failed: Cannot set test variable when no test is started.
    END
