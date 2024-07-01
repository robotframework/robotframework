*** Settings ***
Documentation     Testing that long variable value are truncated
Test Template     Assignment messages should be
Resource          atest_resource.robot

*** Variables ***
@{TESTS}          10 chars    200 chars    201 chars    1000 chars    1001 chars    VAR

*** Test Cases ***
Default limit
    ${EMPTY}
    ...    '0123456789'
    ...    '0123456789' * 20
    ...    '0123456789' * 20 + '...'
    ...    '0123456789' * 20 + '...'
    ...    '0123456789' * 20 + '...'
    ...    '0123456789' * 20 + '...'

Custom limit
    10
    ...    '0123456789'
    ...    '0123456789' + '...'
    ...    '0123456789' + '...'
    ...    '0123456789' + '...'
    ...    '0123456789' + '...'
    ...    '0123456789' + '...'
    1000
    ...    '0123456789'
    ...    '0123456789' * 20
    ...    '0123456789' * 20 + '0'
    ...    '0123456789' * 100
    ...    '0123456789' * 100 + '...'
    ...    '0123456789' * 100
    10000
    ...    '0123456789'
    ...    '0123456789' * 20
    ...    '0123456789' * 20 + '0'
    ...    '0123456789' * 100
    ...    '0123456789' * 100 + '0'
    ...    '0123456789' * 100

Hide value
    0
    ...    '...'
    ...    '...'
    ...    '...'
    ...    '...'
    ...    '...'
    ...    '...'
    -666
    ...    '...'
    ...    '...'
    ...    '...'
    ...    '...'
    ...    '...'
    ...    '...'

Invalid
    [Template]    NONE
    Run Tests Without Processing Output    --maxass oops    cli/console/max_assign_length.robot
    Stderr Should Be Equal To
    ...    [ ERROR ] Invalid value for option '--maxassignlength':
    ...    Expected integer, got 'oops'.${USAGE TIP}\n


*** Keywords ***
Assignment messages should be
    [Arguments]    ${limit}    @{messages}
    IF    $limit
        Run Tests    --maxassignlength ${limit}    cli/console/max_assign_length.robot
    ELSE
        Run Tests    ${EMPTY}    cli/console/max_assign_length.robot
    END
    FOR    ${name}    ${msg}    IN ZIP    ${TESTS}    ${messages}    mode=STRICT
        ${tc} =    Check Test Case    ${name}
        ${msg} =    Evaluate    ${msg}
        Check Log Message    ${tc.body[0].msgs[0]}    \${value} = ${msg}
    END
