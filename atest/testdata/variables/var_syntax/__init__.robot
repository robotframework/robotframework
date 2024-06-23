*** Settings ***
Suite Setup      VAR in suite setup and teardown    root suite setup
Suite Teardown   VAR in suite setup and teardown    root suite teardown

*** Keywords ***
VAR in suite setup and teardown
    [Arguments]    ${where}
    VAR    ${local}     value
    VAR    ${SUITE}     set in ${where}    scope=suite
    VAR    ${SUITES}    set in ${where}    scope=suites
    VAR    ${GLOBAL}    set in ${where}    scope=global
    VAR    ${ROOT}      set in ${where}    scope=global
    Should Be Equal    ${local}     value
    Should Be Equal    ${SUITE}     set in ${where}
    Should Be Equal    ${GLOBAL}    set in ${where}
    TRY
        VAR    ${TEST}    this fails    scope=test
    EXCEPT    AS    ${err}
        Should Be Equal    ${err}    Setting variable '\${TEST}' failed: Cannot set test variable when no test is started.
    END
