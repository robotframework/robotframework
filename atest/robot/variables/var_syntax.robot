*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    variables/var_syntax
Resource          atest_resource.robot

*** Test Cases ***
Scalar
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \${name}    value    log=value

Scalar with separator
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \${a}    \${1}    2        3               separator=\\n          log=1\n2\n3
    Validate VAR    ${tc.body}[1]    \${b}    1        \${2}    3               separator====          log=1===2===3
    Validate VAR    ${tc.body}[2]    \${c}    1        2        \${3}           separator=             log=123
    Validate VAR    ${tc.body}[3]    \${d}    \${a}    \${b}    \${c}           separator=\${0}        log=1\n2\n301===2===30123
    Validate VAR    ${tc.body}[4]    \${e}                                      separator=no effect    log=
    Validate VAR    ${tc.body}[5]    \${f}    separator\=NO    separator\=NO    separator=--YES--      log=separator=NO--YES--separator=NO

List
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \@{name}    v1    v2    separator\=v3          log=[ v1 | v2 | separator=v3 ]

Dict
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \&{name}    k1=v1    k2=v2    separator\=v3    log={ k1=v1 | k2=v2 | separator=v3 }

Long values
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[1]    \${scalar}    \@{items}                        log=This is a rather long value. It will be cut when it is logged by VAR. Otherwise it should work normally. This is a rather long value. It will be cut when it is logged by VAR. Otherwise it should work ...
    Validate VAR    ${tc.body}[2]    \@{list}      \@{items}                        log=[ This is a rather long value. | It will be cut when it is logged by VAR. | Otherwise it should work normally. | This is a rather long value. | It will be cut when it is logged by VAR. | Otherwise it ...
    Validate VAR    ${tc.body}[3]    \&{dict}      \&{{dict(enumerate($items))}}    log={ 0=This is a rather long value. | 1=It will be cut when it is logged by VAR. | 2=Otherwise it should work normally. | 3=This is a rather long value. | 4=It will be cut when it is logged by VAR. | 5=O...

Invalid name
    Check Test Case    ${TESTNAME}

No name
    Check Test Case    ${TESTNAME}

No name with continuation
    Check Test Case    ${TESTNAME}

Equals is accepted
    ${tc} =    Check Test Case    ${TESTNAME}
    Validate VAR    ${tc.body}[0]    \${name}    value             log=value
    Validate VAR    ${tc.body}[2]    \@{name}    v1    v2    v3    log=[ v1 | v2 | v3 ]
    Validate VAR    ${tc.body}[4]    \&{name}    k1=v1    k2=v2    log={ k1=v1 | k2=v2 }

In init file suite setup and teardown
    Check Test Case    In root suite setup
    Validate VAR    ${SUITE.setup.body}[0]       \${local}     value                               log=value
    Validate VAR    ${SUITE.setup.body}[1]       \${SUITE}     set in \${where}    scope=suite     log=set in root suite setup
    Validate VAR    ${SUITE.setup.body}[2]       \${SUITES}    set in \${where}    scope=suites    log=set in root suite setup
    Validate VAR    ${SUITE.setup.body}[3]       \${GLOBAL}    set in \${where}    scope=global    log=set in root suite setup
    Validate VAR    ${SUITE.teardown.body}[0]    \${local}     value                               log=value
    Validate VAR    ${SUITE.teardown.body}[1]    \${SUITE}     set in \${where}    scope=suite     log=set in root suite teardown
    Validate VAR    ${SUITE.teardown.body}[2]    \${SUITES}    set in \${where}    scope=suites    log=set in root suite teardown
    Validate VAR    ${SUITE.teardown.body}[3]    \${GLOBAL}    set in \${where}    scope=global    log=set in root suite teardown

In suite setup and teardown
    Check Test Case    In suite setup
    Validate VAR    ${SUITE.suites[0].setup.body}[3]       \${local}     value                               log=value
    Validate VAR    ${SUITE.suites[0].setup.body}[4]       \${SUITE}     set in \${where}    scope=suite     log=set in suite1 setup
    Validate VAR    ${SUITE.suites[0].setup.body}[5]       \${SUITES}    set in \${where}    scope=suites    log=set in suite1 setup
    Validate VAR    ${SUITE.suites[0].setup.body}[6]       \${GLOBAL}    set in \${where}    scope=global    log=set in suite1 setup
    Validate VAR    ${SUITE.suites[0].teardown.body}[3]    \${local}     value                               log=value
    Validate VAR    ${SUITE.suites[0].teardown.body}[4]    \${SUITE}     set in \${where}    scope=suite     log=set in suite1 teardown
    Validate VAR    ${SUITE.suites[0].teardown.body}[5]    \${SUITES}    set in \${where}    scope=suites    log=set in suite1 teardown
    Validate VAR    ${SUITE.suites[0].teardown.body}[6]    \${GLOBAL}    set in \${where}    scope=global    log=set in suite1 teardown

Scopes
    ${tc} =    Check Test Case    ${TESTNAME} 1
    Validate VAR    ${tc.body}[0]    \${local1}    local1                                  log=local1
    Validate VAR    ${tc.body}[1]    \${local2}    scope\=local2    scope=LOCAL            log=scope=local2
    Validate VAR    ${tc.body}[2]    \@{TEST}      scope\=value     scope=test             log=[ scope=value ]
    Validate VAR    ${tc.body}[3]    \&{SUITE}     scope\=value     scope=\${{'suite'}}    log={ scope=value }
    Validate VAR    ${tc.body}[4]    \${SUITES}    children too     scope=Suites           log=children too
    Validate VAR    ${tc.body}[5]    \${GLOBAL}    global           scope=GLOBAL           log=global
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

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

Name based on another variable
    Check Test Case    ${TESTNAME}

Name based on variable defined in different scope
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

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
    [Arguments]    ${var}    ${name}    @{value}    ${scope}=${None}    ${separator}=${None}    ${log}
    Should Be Equal    ${var.type}         VAR
    Should Be Equal    ${var.name}         ${name}
    Should Be Equal    ${var.value}        ${{tuple($value)}}
    Should Be Equal    ${var.scope}        ${scope}
    Should Be Equal    ${var.separator}    ${separator}
    Check Log Message    ${var.msgs[0]}    ${name} = ${log}
