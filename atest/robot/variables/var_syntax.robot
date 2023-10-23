*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    variables/var_syntax.robot
Resource          atest_resource.robot

*** Test Cases ***
Scalar
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \${name}    value

Scalar with separator
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \${a}    \${1}    2        3               separator=\\n
    Validate VAR    ${tc.body}[1]    \${b}    1        \${2}    3               separator====
    Validate VAR    ${tc.body}[2]    \${c}    1        2        \${3}           separator=
    Validate VAR    ${tc.body}[3]    \${d}    \${a}    \${b}    \${c}           separator=\${0}
    Validate VAR    ${tc.body}[4]    \${e}                                      separator=has no effect
    Validate VAR    ${tc.body}[5]    \${f}    separator\=NO    separator\=NO    separator=--YES--

List
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \@{name}    v1    v2    separator\=v3

Dict
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \&{name}    k1=v1    k2=v2    separator\=v3

Equals is accepted
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \${name}    value
    Validate VAR    ${tc.body}[2]    \@{name}    v1    v2    v3
    Validate VAR    ${tc.body}[4]    \&{name}    k1=v1    k2=v2

Scopes
    ${tc} =    Check Test Case    ${TESTNAME} 1
    Validate VAR    ${tc.body}[0]    \${local1}    local1
    Validate VAR    ${tc.body}[1]    \${local2}    scope\=local2    scope=LOCAL
    Validate VAR    ${tc.body}[2]    \@{test}      scope\=value     scope=test
    Validate VAR    ${tc.body}[3]    \&{suite}     scope\=value     scope=\${{'suite'}}
    Validate VAR    ${tc.body}[4]    \${global}    global           scope=GLOBAL
    Check Test Case    ${TESTNAME} 2

Invalid scope
    Check Test Case    ${TESTNAME}

Invalid scope from variable
    Check Test Case    ${TESTNAME}

Non-existing variable as scope
    Check Test Case    ${TESTNAME}

Non-existing variable in value
    Check Test Case    ${TESTNAME}

Non-existing variable in separator
    Check Test Case    ${TESTNAME}

Named based on another variable
    Check Test Case    ${TESTNAME}

Non-existing variable in name
    Check Test Case    ${TESTNAME}

With FOR
    Check Test Case    ${TESTNAME}

With WHILE
    Check Test Case    ${TESTNAME}

With IF
    Check Test Case    ${TESTNAME}

With inline IF
    Check Test Case    ${TESTNAME}

With TRY
    Check Test Case    ${TESTNAME}

*** Keywords ***
Validate VAR
    [Arguments]    ${var}    ${name}    @{value}    ${scope}=${None}    ${separator}=${None}
    Should Be Equal    ${var.type}         VAR
    Should Be Equal    ${var.name}         ${name}
    Should Be Equal    ${var.value}        ${{tuple($value)}}
    Should Be Equal    ${var.scope}        ${scope}
    Should Be Equal    ${var.separator}    ${separator}
