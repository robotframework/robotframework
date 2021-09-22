*** Settings ***
Suite Setup      Run Tests With Listeners
Resource         listener_resource.robot
Test Template    Taking listener into use should have failed

*** Test Cases ***
Unsupported version
    0    unsupported_listeners.V1ClassListener
    ...    Listener 'unsupported_listeners.V1ClassListener' uses unsupported API version '1'.
    1    unsupported_listeners.InvalidVersionClassListener
    ...    Listener 'unsupported_listeners.InvalidVersionClassListener' uses unsupported API version 'kekkonen'.

No version information
    2    unsupported_listeners
    ...    Listener 'unsupported_listeners' does not have mandatory 'ROBOT_LISTENER_API_VERSION' attribute.

*** Keywords ***
Run Tests With Listeners
    ${listeners} =    Catenate
    ...    --listener unsupported_listeners.V1ClassListener
    ...    --listener unsupported_listeners.InvalidVersionClassListener
    ...    --listener unsupported_listeners
    Run Tests    ${listeners}    misc/pass_and_fail.robot

Taking listener into use should have failed
    [Arguments]    ${index}    ${name}    ${error}
    Check Log Message    ${ERRORS}[${index}]
    ...    Taking listener '${name}' into use failed: ${error}    ERROR
