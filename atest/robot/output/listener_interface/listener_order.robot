*** Settings ***
Suite Setup       Run Tests With Ordered Listeners
Resource          atest_resource.robot

*** Variables ***
${LISTENER}       ${DATADIR}/output/listener_interface/ListenerOrder.py

*** Test Cases ***
Validate normal order
    VAR    ${expected}
    ...    LIB 3 (999.9): start_suite
    ...    CLI 2 (3.14): start_suite
    ...    CLI 3 (None): start_suite
    ...    LIB 1 (0): start_suite
    ...    LIB 2 (None): start_suite
    ...    CLI 1 (-1): start_suite
    ...    LIB 3 (999.9): log_message
    ...    CLI 2 (3.14): log_message
    ...    CLI 3 (None): log_message
    ...    LIB 1 (0): log_message
    ...    LIB 2 (None): log_message
    ...    CLI 1 (-1): log_message
    ...    LIB 3 (999.9): end_test
    ...    CLI 2 (3.14): end_test
    ...    CLI 3 (None): end_test
    ...    LIB 1 (0): end_test
    ...    LIB 2 (None): end_test
    ...    CLI 1 (-1): end_test
    ...    separator=\n
    File Should Be Equal To    %{TEMPDIR}/listener_order.log    ${expected}\n

Validate close order
    [Documentation]    Library listeners are closed when libraries go out of scope.
    VAR    ${expected}
    ...    LIB 1 (0): close
    ...    LIB 2 (None): close
    ...    LIB 3 (999.9): close
    ...    CLI 2 (3.14): close
    ...    CLI 3 (None): close
    ...    CLI 1 (-1): close
    ...    separator=\n
    File Should Be Equal To    %{TEMPDIR}/listener_close_order.log    ${expected}\n

Invalid priority
    ${listener} =    Normalize Path    ${LISTENER}
    Check Log Message    ${ERRORS}[0]    Taking listener '${listener}:NOT USED:invalid' into use failed: Invalid listener priority 'invalid'.    ERROR
    Check Log Message    ${ERRORS}[1]    Error in library 'BAD': Registering listeners failed: Taking listener 'SELF' into use failed: Invalid listener priority 'bad'.    ERROR

*** Keywords ***
Run Tests With Ordered Listeners
    ${listener} =    Normalize Path    ${LISTENER}
    VAR    ${options}
    ...    --listener "${listener}:CLI 1:-1"
    ...    --listener "${listener}:CLI 2:3.14"
    ...    --listener "${listener}:NOT USED:invalid"
    ...    --listener "${listener}:CLI 3"
    Run Tests    ${options}    output/listener_interface/listener_order.robot
