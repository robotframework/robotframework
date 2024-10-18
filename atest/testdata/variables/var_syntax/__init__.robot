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
    IF    $where == 'root suite setup'
        VAR    ${TEST}    set in ${where}    scope=test
    ELSE
        Should Be Equal    ${TEST}    set in root suite setup
        VAR    ${TEST}    set in ${where}
        Should Be Equal    ${TEST}    set in root suite teardown
    END
